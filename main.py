import datetime
import platform
import time
import requests
import subprocess
import re
from config import (
    CHECK_INTERVAL, DEVICES, CHAT_ID, TELEGRAM_TOKEN,
    TOPICO_QUEDA_E_VOLTA, TOPICO_QUEDAS, TOPICO_LATENCIA, TOPICO_SISTEMA,
    MAX_RETRIES, LATENCY_THRESHOLD_MS
)

def send_telegram_message(message, thread_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "message_thread_id": thread_id,
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f"Erro ao enviar no Telegram: {e}")

def ping_with_latency(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]
    try:
        output = subprocess.check_output(command, universal_newlines=True, stderr=subprocess.STDOUT)
        match = re.search(r'time[=<]([0-9.]+)', output, re.IGNORECASE)
        if match:
            return True, float(match.group(1))
        return True, 0.0
    except subprocess.CalledProcessError:
        return False, 0.0

def monitor():
    print("🚀 Monitoramento Avançado iniciado!")
    send_telegram_message("🤖 *Bot iniciado!* Monitoramento online.", TOPICO_SISTEMA)

    state = {
        dev["host"]: {
            "is_down": False, 
            "down_start_time": None, 
            "fail_count": 0,
            "latency_alert_sent": False
        }
        for dev in DEVICES
    }
    
    heartbeat_sent_today = False

    while True:
        now = datetime.datetime.now()
        
        # --- LÓGICA DO HEARTBEAT DIÁRIO (08:00 AM) ---
        if now.hour == 8 and now.minute == 0 and not heartbeat_sent_today:
            online_count = sum(1 for d in state.values() if not d["is_down"])
            msg_hb = (f"✅ *Bom dia! Monitoramento ativo.*\n"
                      f"📡 {online_count}/{len(DEVICES)} dispositivos online.")
            send_telegram_message(msg_hb, TOPICO_SISTEMA)
            heartbeat_sent_today = True
            
        if now.hour == 0:
            heartbeat_sent_today = False # Reseta à meia-noite

        # --- LÓGICA DE PING E LATÊNCIA ---
        for dev in DEVICES:
            name = dev["name"]
            host = dev["host"]
            is_up, latency = ping_with_latency(host)
            dev_state = state[host]

            # 1. QUEDA DETECTADA (Com Retries)
            if not is_up:
                dev_state["fail_count"] += 1
                if dev_state["fail_count"] >= MAX_RETRIES and not dev_state["is_down"]:
                    dev_state["is_down"] = True
                    dev_state["down_start_time"] = now
                    msg_down = (f"🚨 *ALERTA DE QUEDA*\n\n🖥️ *Dispositivo:* `{name}`\n"
                                f"🌐 *IP:* `{host}`\n🔴 *Horário:* {now.strftime('%H:%M:%S')}")
                    print(f"[{now.strftime('%H:%M:%S')}] 🔴 {name} caiu!")
                    send_telegram_message(msg_down, thread_id=TOPICO_QUEDAS)
            
            # 2. RETORNO DETECTADO
            elif is_up:
                dev_state["fail_count"] = 0 
                
                # Tratar recuperação de queda
                if dev_state["is_down"]:
                    down_time = dev_state["down_start_time"]
                    downtime_seconds = int((now - down_time).total_seconds())
                    m, s = divmod(downtime_seconds, 60)
                    h, m = divmod(m, 60)
                    time_str = f"{h}h {m}m {s}s".replace("0h ", "").replace("0m ", "")
                    
                    msg_up = (f"📊 *RETORNO*\n\n🖥️ *Dispositivo:* `{name}`\n"
                              f"⏱️ *Tempo OFF:* `{time_str}`")
                    print(f"[{now.strftime('%H:%M:%S')}] 🟢 {name} voltou!")
                    send_telegram_message(msg_up, thread_id=TOPICO_QUEDA_E_VOLTA)
                    dev_state["is_down"] = False

                # 3. ALERTA DE LATÊNCIA
                if latency > LATENCY_THRESHOLD_MS and not dev_state["latency_alert_sent"]:
                    msg_lat = (f"⚠️ *REDE LENTA*\n🖥️ `{name}` ({host})\n"
                               f"🐌 *Tempo de resposta:* `{latency}ms`")
                    send_telegram_message(msg_lat, thread_id=TOPICO_LATENCIA)
                    dev_state["latency_alert_sent"] = True
                elif latency <= LATENCY_THRESHOLD_MS and dev_state["latency_alert_sent"]:
                    dev_state["latency_alert_sent"] = False # Reseta quando normaliza

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
import datetime
import os
import platform
import time
import requests
from config import (
    CHECK_INTERVAL,
    DEVICES,
    CHAT_ID,
    TELEGRAM_TOKEN,
    TOPICO_QUEDA_E_VOLTA,
    TOPICO_QUEDAS,
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


def ping(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = (
        f"ping {param} 1 {host} > NUL 2>&1"
        if platform.system().lower() == "windows"
        else f"ping {param} 1 {host} > /dev/null 2>&1"
    )
    return os.system(command) == 0


def monitor():
    print("🚀 Monitoramento Multi-IP iniciado com sucesso!")
    print(f"  -> Dispositivos na fila: {len(DEVICES)}")

    # Dicionário para guardar o estado de cada dispositivo
    state = {
        dev["host"]: {"is_down": False, "down_start_time": None}
        for dev in DEVICES
    }

    while True:
        for dev in DEVICES:
            name = dev["name"]
            host = dev["host"]
            is_up = ping(host)

            dev_state = state[host]

            # 1. QUEDA DETECTADA
            if not is_up and not dev_state["is_down"]:
                dev_state["is_down"] = True
                dev_state["down_start_time"] = datetime.datetime.now()

                msg_down = (
                    f"🚨 *ALERTA DE QUEDA*\n\n"
                    f"🖥️ *Dispositivo:* `{name}`\n"
                    f"🌐 *IP:* `{host}`\n"
                    f"🔴 *Horário:* {dev_state['down_start_time'].strftime('%d/%m/%Y às %H:%M:%S')}"
                )
                print(
                    f"[{dev_state['down_start_time'].strftime('%H:%M:%S')}] 🔴 {name} ({host}) caiu!"
                )
                send_telegram_message(msg_down, thread_id=TOPICO_QUEDAS)

            # 2. RETORNO DETECTADO
            elif is_up and dev_state["is_down"]:
                up_time = datetime.datetime.now()
                down_time = dev_state["down_start_time"]
                downtime_seconds = int((up_time - down_time).total_seconds())

                minutes, seconds = divmod(downtime_seconds, 60)
                hours, minutes = divmod(minutes, 60)

                time_str = ""
                if hours > 0:
                    time_str += f"{hours}h "
                if minutes > 0:
                    time_str += f"{minutes}m "
                time_str += f"{seconds}s"

                msg_relatorio = (
                    f"📊 *RELATÓRIO DE RETORNO*\n\n"
                    f"🖥️ *Dispositivo:* `{name}`\n"
                    f"🌐 *IP:* `{host}`\n"
                    f"🔴 *Queda:* {down_time.strftime('%d/%m/%Y às %H:%M:%S')}\n"
                    f"🟢 *Retorno:* {up_time.strftime('%d/%m/%Y às %H:%M:%S')}\n"
                    f"⏱️ *Tempo OFF:* `{time_str}`"
                )
                print(
                    f"[{up_time.strftime('%H:%M:%S')}] 🟢 {name} ({host}) voltou!"
                )
                send_telegram_message(
                    msg_relatorio, thread_id=TOPICO_QUEDA_E_VOLTA
                )
                dev_state["is_down"] = False

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    monitor()
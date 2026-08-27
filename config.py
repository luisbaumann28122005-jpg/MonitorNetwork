# --- CREDENCIAIS DA API ---
TELEGRAM_TOKEN = "8990333973:AAEgcmRoDfuxSwF3gt8zRWfX_aCvP8wmJMM"
CHAT_ID = "-1004324089821"

# --- TÓPICOS ---
TOPICO_QUEDAS = 2
TOPICO_QUEDA_E_VOLTA = 5
TOPICO_LATENCIA = 106  
TOPICO_SISTEMA = 107   

# --- PARÂMETROS DE MONITORAMENTO ---
CHECK_INTERVAL = 10           
MAX_RETRIES = 3               
LATENCY_THRESHOLD_MS = 150    

# --- LISTA DE DISPOSITIVOS PARA MONITORAR ---
DEVICES = [
    {"name": "Pc Luis", "host": "192.168.100.35"},
    {"name": "Roteador Principal", "host": "192.168.100.1"},
    {"name": "Roteador Externo", "host": "192.168.100.15"},
    {"name": "Tv Quarto Luis", "host": "192.168.100.9"},
    {"name": "Câmera Garagem", "host": "192.168.100.40"},
]
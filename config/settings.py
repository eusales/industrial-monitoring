import os

# ===== Limites de variáveis industriais =====
LIMITES = {
    "temperatura": {"alerta": 70, "critico": 80, "min": 20, "max": 90},
    "pressao": {"alerta": 6, "critico": 7, "min": 1, "max": 8},
    "corrente": {"alerta": 25, "critico": 28, "min": 5, "max": 30},
    "tensao": {"alerta": 230, "critico": 240, "min": 210, "max": 240},
    "producao": {"alerta": 200, "critico": 280, "min": 50, "max": 300}
}

# ===== Configurações de Dashboard =====
DASHBOARD = {
    "taxa_atualizacao_padrao": 2,   # segundos
    "janela_mm_padrao": 5,          # amostras para média móvel
    "historico_maximo": 1000        # número máximo de registros no histórico
}

# ===== Cenários de simulação =====
CENARIOS = ["Normal", "Alerta", "Critico"]

# ===== Configurações de Notificações =====
NOTIFICACOES = {
    "telegram": {
        "token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "chat_id": os.getenv("TELEGRAM_CHAT_ID", "")
    },
    "email": {
        "ativo": False,
        "smtp_server": "smtp.exemplo.com",
        "smtp_port": 587,
        "usuario": os.getenv("SMTP_USER", ""),
        "senha": os.getenv("SMTP_PASSWORD", ""),
        "destinatario": os.getenv("SMTP_TO", "")
    },
    "log_file": "logs/eventos.log",
    "min_interval_segundos": 60  # intervalo mínimo entre alertas iguais
}

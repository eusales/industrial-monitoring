import os
import time
import requests
from datetime import datetime
from config.settings import NOTIFICACOES

# Histórico de últimos alertas para evitar spam
ultimo_alerta = {}

# -------- Função Telegram --------
def enviar_telegram(mensagem):
    token = NOTIFICACOES["telegram"]["token"]
    chat_id = NOTIFICACOES["telegram"]["chat_id"]
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensagem}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar Telegram:", e)

# -------- Função Email --------
def enviar_email(mensagem):
    import smtplib
    from email.mime.text import MIMEText

    config = NOTIFICACOES["email"]
    if not config["ativo"]:
        return

    try:
        msg = MIMEText(mensagem)
        msg["Subject"] = "Alerta Industrial"
        msg["From"] = config["usuario"]
        msg["To"] = config["destinatario"]

        with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as server:
            server.starttls()
            server.login(config["usuario"], config["senha"])
            server.sendmail(config["usuario"], config["destinatario"], msg.as_string())
    except Exception as e:
        print("Erro ao enviar Email:", e)

# -------- Função Log --------
def registrar_log(variavel, valor, nivel):
    if not os.path.exists(os.path.dirname(NOTIFICACOES["log_file"])):
        os.makedirs(os.path.dirname(NOTIFICACOES["log_file"]), exist_ok=True)
    with open(NOTIFICACOES["log_file"], "a") as f:
        f.write(f"{datetime.now()} | {nivel} | {variavel} = {valor}\n")

# -------- Função principal de notificação --------
def notificar_alerta(variavel, valor, nivel):
    global ultimo_alerta
    agora = time.time()
    chave = f"{variavel}_{nivel}"

    # Verifica intervalo mínimo entre alertas iguais
    if chave in ultimo_alerta and (agora - ultimo_alerta[chave]) < NOTIFICACOES["min_interval_segundos"]:
        return

    mensagem = f"⚠ ALERTA {nivel}: {variavel} = {valor}"
    registrar_log(variavel, valor, nivel)
    enviar_telegram(mensagem)
    enviar_email(mensagem)

    ultimo_alerta[chave] = agora

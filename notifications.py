import os
import time
import requests
from datetime import datetime
from config.settings import NOTIFICACOES

# Histórico de últimos alertas para evitar spam
ultimo_alerta = {}
ultima_tentativa = {}

# -------- Função Telegram --------
def enviar_telegram(mensagem):
    if not NOTIFICACOES["telegram"].get("ativo", False):
        return False, "Telegram desativado no .env."
    token = NOTIFICACOES["telegram"]["token"]
    chat_id = NOTIFICACOES["telegram"]["chat_id"]
    if not token or not chat_id:
        return False, "Preencha TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no .env."
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensagem}
    try:
        resposta = requests.post(url, data=payload, timeout=(3, 5))
        if resposta.status_code != 200:
            return False, f"Telegram recusou o envio (HTTP {resposta.status_code}). Verifique token, chat e /start."
        if not resposta.json().get("ok"):
            return False, "Telegram não confirmou o envio."
        return True, "Mensagem enviada ao Telegram."
    except (requests.RequestException, ValueError):
        return False, "Falha de conexão ou resposta inválida do Telegram."

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
        return None, "Aguardando intervalo entre alertas."
    if chave in ultima_tentativa and agora - ultima_tentativa[chave] < 10:
        return None, "Aguardando nova tentativa."
    ultima_tentativa[chave] = agora

    mensagem = f"⚠ ALERTA {nivel}: {variavel} = {valor}"
    registrar_log(variavel, valor, nivel)
    sucesso, detalhe = enviar_telegram(mensagem)
    enviar_email(mensagem)

    if sucesso:
        ultimo_alerta[chave] = agora
    with open(NOTIFICACOES["log_file"], "a", encoding="utf-8") as arquivo:
        arquivo.write(f"{datetime.now()} | TELEGRAM | {sucesso} | {detalhe}\n")
    return sucesso, detalhe

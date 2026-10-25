from config.settings import LIMITES, CENARIOS
import random
import pandas as pd
from datetime import datetime

def gerar_dados():
    cenario = random.choices(CENARIOS, weights=[70, 20, 10])[0]

    temperatura = round(random.uniform(LIMITES["temperatura"]["min"], LIMITES["temperatura"]["max"]), 2)
    pressao = round(random.uniform(LIMITES["pressao"]["min"], LIMITES["pressao"]["max"]), 2)
    corrente = round(random.uniform(LIMITES["corrente"]["min"], LIMITES["corrente"]["max"]), 2)
    tensao = round(random.uniform(LIMITES["tensao"]["min"], LIMITES["tensao"]["max"]), 2)
    producao = random.randint(LIMITES["producao"]["min"], LIMITES["producao"]["max"])

    if cenario == "Critico":
        temperatura = round(random.uniform(LIMITES["temperatura"]["critico"], LIMITES["temperatura"]["max"]), 2)

    status = random.choice(["Ligada", "Desligada", "Falha"])

    data = {
        "timestamp": datetime.now(),
        "temperatura": temperatura,
        "pressao": pressao,
        "corrente": corrente,
        "tensao": tensao,
        "status": status,
        "producao": producao
    }

    return pd.DataFrame([data])

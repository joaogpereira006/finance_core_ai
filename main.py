from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_index():
    # Retorna o arquivo index.html que está na mesma pasta do main.py
    return FileResponse('index.html')

# BANCO DE DADOS DE USUÁRIOS
USUARIOS_PERMITIDOS = {
    "joao.pereira": "255092",
    "gabi.recrutaeu": "vaga2026",
    "edu.recrutaeu": "analista2026"
}

class LoginDados(BaseModel):
    usuario: str
    senha: str

# Carregamento do arquivo ZIP
df_api = pd.read_csv('dados_limpos.zip')

@app.post("/login")
def login(dados: LoginDados):
    senha_correta = USUARIOS_PERMITIDOS.get(dados.usuario)
    if senha_correta and senha_correta == dados.senha:
        return {"auth": True, "nome": dados.usuario.split('.')[0].upper()}
    return {"auth": False}

@app.get("/resumo")
def resumo_estratégico():
    return df_api.groupby('score_credito').agg({
        'renda_anual': 'mean',
        'divida_pendente': 'mean',
        'num_emprestimos': 'mean'
    }).round(2).to_dict(orient='index')

@app.get("/simular-complexo")
def simular_complexo(idade: int, renda_mensal: float, divida: float, score_usuario: int, n_parcelas: int):
    # Lógica de cálculo de comprometimento de renda (máximo 30%)
    if divida <= 10000: prazo_ativa = 36
    elif divida <= 50000: prazo_ativa = 48
    else: prazo_ativa = 60
    
    parcela_ativa = divida / prazo_ativa
    perc_ativa = (parcela_ativa / renda_mensal) * 100
    teto_total_mensal = renda_mensal * 0.30
    margem_disponivel = teto_total_mensal - parcela_ativa
    
    i = 0.0175 # Taxa de juros simulada
    fator = (i * (1 + i)**n_parcelas) / (((1 + i)**n_parcelas) - 1)
    
    if margem_disponivel <= 0:
        limite_possivel = 0
        parcela_simulada = 0
    else:
        limite_possivel = margem_disponivel / fator
        parcela_simulada = margem_disponivel

    perc_nova = (parcela_simulada / renda_mensal) * 100
    total_comprometido = perc_ativa + perc_nova
    
    status = "Crédito Liberado"
    cor = "#10b981"
    # Classificação baseada no Score e Comprometimento
    classe = "ALTO POTENCIAL" if score_usuario > 700 else "MÉDIO RISCO"

    if total_comprometido > 30.1:
        status = "Crédito Negado: Limite Excedido"
        cor = "#ef4444"
        classe = "RISCO CRÍTICO"
        limite_possivel = 0
        parcela_simulada = 0
    elif score_usuario < 500:
        status = "Crédito Negado: Score Baixo"
        cor = "#f59e0b"
        classe = "PERFIL CONSERVADOR"
        limite_possivel = 0

    return {
        "classe": classe,
        "status": status,
        "cor": cor,
        "limite_maximo": round(limite_possivel, 2),
        "total_comprometido": round(total_comprometido, 1),
        "dados_detalhados": {
            "p_ativa": round(parcela_ativa, 2),
            "pct_ativa": round(perc_ativa, 1),
            "p_nova": round(parcela_simulada, 2),
            "pct_nova": round(perc_nova, 1),
            "total_rs": round(parcela_ativa + parcela_simulada, 2)
        }
    }
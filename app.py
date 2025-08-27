from flask import Flask, jsonify
import hashlib
import requests
from datetime import datetime

app = Flask(__name__)

# === CONFIGURAÇÕES ===
TOKEN_ORIGINAL = "mRvd11QSxXs5LUL$CfW1"
USER = "02297349289"
API_URL = "https://stou.ifractal.com.br/i9saude/rest/"

# === FUNÇÕES AUXILIARES ===
def gerar_token_sha256(data_formatada):
    token_concatenado = TOKEN_ORIGINAL + data_formatada
    return hashlib.sha256(token_concatenado.encode()).hexdigest()

def get_headers():
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    return {
        "Content-Type": "application/json",
        "User": USER,
        "Token": gerar_token_sha256(data_hoje)
    }

# === ROTA COM TABELA ===
@app.route("/rotatividade_2025_tabela", methods=["GET"])
def rotatividade_2025_tabela():
    body = {
        "pag": "funcionario_rotatividade",
        "cmd": "get",
        "ano": 2025
    }

    try:
        response = requests.post(API_URL, json=body, headers=get_headers())
        data = response.json()

        # Ajusta caso venha dict
        if isinstance(data, dict):
            data = data.get("data", [])

        # Cria tabela
        meses = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto",
                 "Setembro","Outubro","Novembro","Dezembro","2025"]
        
        tabela = {
            "Indicador": [
                "Admissões",
                "Demissões",
                "ROTATIVIDADE",
                "Total funcionários início do mês",
                "Total funcionários fim do mês",
                "Variação",
                "Taxa de variação",
                "TURNOVER",
                "TURNOVER acumulado no ano",
                "Taxa de rotatividade admissional",
                "Taxa de rotatividade demissional"
            ]
        }

        # Para cada indicador, adiciona valores mês a mês
        for indicador in tabela["Indicador"]:
            # Aqui é necessário mapear os dados do JSON para os meses
            # Exemplo simples: pegar data[indicador][mes], ajusta conforme seu JSON real
            valores = []
            for mes in range(1,13):
                valor = next((item["valor"] for item in data if item["indicador"] == indicador and item["mes"] == mes), "-")
                valores.append(valor)
            # Soma total anual ou valor final
            total = sum([v for v in valores if isinstance(v,int)]) if any(isinstance(v,int) for v in valores) else "-"
            valores.append(total)
            tabela[indicador] = valores

        return jsonify(tabela)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# === MAIN ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

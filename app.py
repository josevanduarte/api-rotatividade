from flask import Flask, request, jsonify
import hashlib
import requests
from datetime import datetime

app = Flask(__name__)

# === CONFIGURAÇÕES ===
TOKEN_ORIGINAL = "mRvd11QSxXs5LUL$CfW1"   # Troque pelo Token fornecido pelo suporte
USER = "02297349289"                       # Login de usuário
API_URL = "https://stou.ifractal.com.br/i9saude/rest/"


# === FUNÇÕES AUXILIARES ===
def gerar_token_sha256(data_formatada):
    """Concatena Token original + data e gera SHA256"""
    token_concatenado = TOKEN_ORIGINAL + data_formatada
    return hashlib.sha256(token_concatenado.encode()).hexdigest()


def get_headers():
    """Monta o header da requisição conforme modelo"""
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    return {
        "Content-Type": "application/json",
        "User": USER,
        "Token": gerar_token_sha256(data_hoje)
    }


# === ROTAS ===
@app.route("/")
def home():
    return "✅ API online! Rotas disponíveis: /rotatividade"


@app.route("/rotatividade", methods=["GET"])
def funcionario_rotatividade():
    """
    Exemplo de chamada:
    /rotatividade?ano=2025&cod_empresa=10&dtde=01/01/2025&dtate=31/12/2025
    """
    # Corpo base da requisição
    body = {
        "pag": "funcionario_rotatividade",
        "cmd": "get"
    }

    # Adiciona filtros passados via URL
    for key in request.args:
        val = request.args.get(key)
        if val.lower() == "true":
            val = True
        elif val.lower() == "false":
            val = False
        elif val.isdigit():
            val = int(val)
        body[key] = val

    print("=== BODY ENVIADO PARA API ===")
    print(body)
    print("=============================")

    try:
        response = requests.post(API_URL, json=body, headers=get_headers())
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# === MAIN ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

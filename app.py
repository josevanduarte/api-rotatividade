from flask import Flask, jsonify
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


# === ROTA FIXA PARA 2025 ===
@app.route("/rotatividade_2025", methods=["GET"])
def funcionario_rotatividade_2025():
    """
    Retorna sempre os dados de 2025 já no formato de tabela (array JSON).
    Exemplo: https://sua-api.onrender.com/rotatividade_2025
    """
    body = {
        "pag": "funcionario_rotatividade",
        "cmd": "get",
        "ano": 2025
    }

    try:
        response = requests.post(API_URL, json=body, headers=get_headers())
        data = response.json()

        # Se vier como dict, ajusta para lista
        if isinstance(data, dict):
            if "data" in data:
                data = data["data"]
            else:
                data = [data]

        return jsonify(data)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# === MAIN ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

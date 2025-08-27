from flask import Flask, request, jsonify, render_template_string
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
    token_concatenado = TOKEN_ORIGINAL + data_formatada
    return hashlib.sha256(token_concatenado.encode()).hexdigest()

def get_headers():
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    return {
        "Content-Type": "application/json",
        "User": USER,
        "Token": gerar_token_sha256(data_hoje)
    }

# === TEMPLATE HTML BÁSICO ===
HTML_TABELA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Rotatividade</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1e1e1e; color: #ddd; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #444; padding: 8px; text-align: center; }
        th { background-color: #333; color: #fff; }
        tr:nth-child(even) { background-color: #2a2a2a; }
        .highlight { background: #fdfd96; color: #000; }
    </style>
</head>
<body>
    <h2>📊 Relatório de Rotatividade</h2>
    <table>
        <thead>
            <tr>
                {% for col in dados[0].keys() %}
                    <th>{{ col }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in dados %}
                <tr>
                    {% for col in row.values() %}
                        <td>{{ col }}</td>
                    {% endfor %}
                </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

# === ROTAS ===
@app.route("/")
def home():
    return "✅ API online! Rotas disponíveis: /rotatividade"

@app.route("/rotatividade", methods=["GET"])
def funcionario_rotatividade():
    body = {"pag": "funcionario_rotatividade", "cmd": "get"}

    # Adiciona filtros da URL
    for key in request.args:
        val = request.args.get(key)
        if val.lower() == "true":
            val = True
        elif val.lower() == "false":
            val = False
        elif val.isdigit():
            val = int(val)
        body[key] = val

    try:
        response = requests.post(API_URL, json=body, headers=get_headers())
        data = response.json()

        # se a API retornar lista de registros
        if isinstance(data, list) and len(data) > 0:
            return render_template_string(HTML_TABELA, dados=data)
        else:
            return jsonify(data)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# === MAIN ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

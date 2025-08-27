from flask import Flask, request, jsonify, render_template_string
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

# === TEMPLATE HTML IDÊNTICO ===
HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Rotatividade</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1e1e1e; color: #ddd; padding: 20px; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #444; padding: 8px; text-align: center; }
        th { background-color: #333; color: #fff; }
        tr:nth-child(even) { background-color: #2a2a2a; }
        .highlight { background: #fdfd96; color: #000; font-weight: bold; }
        h1 { color: #fff; }
    </style>
</head>
<body>
    <h1>📊 Relatório de Rotatividade</h1>
    <table>
        <thead>
            <tr>
                <th></th>
                {% for mes in meses %}
                    <th>{{ mes }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            <tr><td>Admissões</td>{% for v in adm %}<td>{{ v }}</td>{% endfor %}</tr>
            <tr><td>Demissões</td>{% for v in dem %}<td>{{ v }}</td>{% endfor %}</tr>
            <tr><td>ROTATIVIDADE</td>{% for v in rot %}<td>{{ v }}</td>{% endfor %}</tr>

            <tr><td>Total funcionários início do mês</td>{% for v in total_ini %}<td>{{ v }}</td>{% endfor %}</tr>
            <tr><td>Total funcionários fim do mês</td>{% for v in total_fim %}<td>{{ v }}</td>{% endfor %}</tr>
            <tr><td>Variação</td>{% for v in variacao %}<td>{{ v }}</td>{% endfor %}</tr>
            <tr><td>Taxa de variação</td>{% for v in taxa_var %}<td>{{ v }}</td>{% endfor %}</tr>

            <tr class="highlight"><td>TURNOVER</td>{% for v in turnover %}<td>{{ v }}%</td>{% endfor %}</tr>
            <tr><td>Taxa de rotatividade admissional</td>{% for v in taxa_adm %}<td>{{ v }}%</td>{% endfor %}</tr>
            <tr><td>Taxa de rotatividade demissional</td>{% for v in taxa_dem %}<td>{{ v }}%</td>{% endfor %}</tr>
        </tbody>
    </table>
</body>
</html>
"""

# === ROTAS ===
@app.route("/rotatividade", methods=["GET"])
def funcionario_rotatividade():
    body = {"pag": "funcionario_rotatividade", "cmd": "get"}

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

        # === MESSES ===
        meses = [row[0] for row in data["taxa_anual"][1:]]  # pega Jan, Fev, Mar...

        # === Admissões, Demissões, Turnover ===
        adm  = [row[1] for row in data["taxa_anual"][1:]]
        dem  = [row[2] for row in data["taxa_anual"][1:]]
        rot  = [a + d for a, d in zip(adm, dem)]  # soma simples para "rotatividade"
        turnover = [row[3] for row in data["taxa_anual"][1:]]

        # === Total funcionários ===
        total_ini = [row[1] for row in data["total_rotatividade_mes"][1:]]
        total_fim = [row[2] for row in data["total_rotatividade_mes"][1:]]
        variacao  = [row[3] for row in data["total_rotatividade_mes"][1:]]
        taxa_var  = [row[4] for row in data["total_rotatividade_mes"][1:]]

        # === Taxas ===
        taxa_adm = [row[2] for row in data["turnover_mes"][1:]]
        taxa_dem = [row[3] for row in data["turnover_mes"][1:]]

        return render_template_string(
            HTML_PAGE,
            meses=meses,
            adm=adm,
            dem=dem,
            rot=rot,
            total_ini=total_ini,
            total_fim=total_fim,
            variacao=variacao,
            taxa_var=taxa_var,
            turnover=turnover,
            taxa_adm=taxa_adm,
            taxa_dem=taxa_dem
        )

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

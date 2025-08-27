from flask import Flask, request, jsonify
import requests
import hashlib
from datetime import datetime

app = Flask(__name__)

# Configurações fixas
TOKEN_ORIGINAL = "mRvd11QSxXs5LUL$CfW1"
USER = "02297349289"
API_URL = "https://stou.ifractal.com.br/i9saude/rest/"

# Função para gerar token SHA256
def gerar_token_sha256(data_formatada):
    token_concat = TOKEN_ORIGINAL + data_formatada
    return hashlib.sha256(token_concat.encode()).hexdigest()

# Headers da API
def get_headers():
    data_formatada = datetime.now().strftime("%d/%m/%Y")
    token_sha256 = gerar_token_sha256(data_formatada)
    return {
        "token": token_sha256,
        "user": USER,
        "Content-Type": "application/json"
    }

# ==============================
# ROTA HTML (visualização igual à imagem)
# ==============================
@app.route("/rotatividade", methods=["GET"])
def funcionario_rotatividade_html():
    body = {"pag": "funcionario_rotatividade", "cmd": "get"}

    # Passa parâmetros da URL para o corpo
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

        # === Monta tabela HTML ===
        tabela_html = """
        <html>
        <head>
            <style>
                table { border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
        <h2>Relatório de Rotatividade</h2>
        <table>
            <tr>
                <th>Mês</th><th>Admissões</th><th>Demissões</th><th>Rotatividade</th>
                <th>Total Início</th><th>Total Fim</th><th>Variação</th><th>% Variação</th>
                <th>Turnover</th><th>% Adm</th><th>% Dem</th>
            </tr>
        """

        for i, row in enumerate(data["taxa_anual"][1:]):  # pula cabeçalho
            mes = row[0]
            adm = row[1]
            dem = row[2]
            rot = adm + dem
            turnover = row[3]

            total_ini = data["total_rotatividade_mes"][i+1][1]
            total_fim = data["total_rotatividade_mes"][i+1][2]
            variacao  = data["total_rotatividade_mes"][i+1][3]
            taxa_var  = data["total_rotatividade_mes"][i+1][4]

            taxa_adm = data["turnover_mes"][i+1][1]
            taxa_dms = data["turnover_mes"][i+1][2]

            tabela_html += f"""
                <tr>
                    <td>{mes}</td>
                    <td>{adm}</td>
                    <td>{dem}</td>
                    <td>{rot}</td>
                    <td>{total_ini}</td>
                    <td>{total_fim}</td>
                    <td>{variacao}</td>
                    <td>{taxa_var}</td>
                    <td>{turnover}</td>
                    <td>{taxa_adm}</td>
                    <td>{taxa_dms}</td>
                </tr>
            """

        tabela_html += "</table></body></html>"
        return tabela_html

    except Exception as e:
        return f"Erro: {str(e)}"


# ==============================
# ROTA JSON (para Power BI)
# ==============================
@app.route("/rotatividade_json", methods=["GET"])
def funcionario_rotatividade_json():
    body = {"pag": "funcionario_rotatividade", "cmd": "get"}

    # Passa parâmetros da URL para o corpo
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

        result = []
        turnover_acumulado = 0

        for i, row in enumerate(data["taxa_anual"][1:]):  # pula cabeçalho
            mes = row[0]
            adm = row[1]
            dem = row[2]
            rot = adm + dem
            turnover = row[3]
            turnover_acumulado += turnover

            total_ini = data["total_rotatividade_mes"][i+1][1]
            total_fim = data["total_rotatividade_mes"][i+1][2]
            variacao  = data["total_rotatividade_mes"][i+1][3]
            taxa_var  = data["total_rotatividade_mes"][i+1][4]

            taxa_adm = data["turnover_mes"][i+1][1]
            taxa_dms = data["turnover_mes"][i+1][2]

            result.append({
                "Mes": mes,
                "Admissoes": adm,
                "Demissoes": dem,
                "Rotatividade": rot,
                "Total_Inicio": total_ini,
                "Total_Fim": total_fim,
                "Variacao": variacao,
                "Taxa_Variacao": taxa_var,
                "Turnover": turnover,
                "Turnover_Acumulado_Ano": turnover_acumulado,
                "Taxa_Adm": taxa_adm,
                "Taxa_Dem": taxa_dms
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    app.run(port=10000, debug=True)

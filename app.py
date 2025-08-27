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
# BUSCA TODAS AS UNIDADES NA API
# ==============================
def get_unidades():
    body = {"pag": "empresa", "cmd": "get"}
    response = requests.post(API_URL, json=body, headers=get_headers())
    return response.json()   # Deve trazer lista de empresas/unidades

# ==============================
# ROTA TESTE: MOSTRAR UNIDADES
# ==============================
@app.route("/unidades", methods=["GET"])
def listar_unidades():
    try:
        unidades = get_unidades()
        return jsonify(unidades)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ==============================
# ROTA JSON (ROTATIVIDADE TODAS)
# ==============================
@app.route("/rotatividade_json", methods=["GET"])
def funcionario_rotatividade_json():
    ano = request.args.get("ano", datetime.now().year)
    result = []

    try:
        unidades = get_unidades()
    except Exception as e:
        return jsonify({"erro": f"Falha ao buscar unidades: {str(e)}"}), 500

    for unidade in unidades:
        cod_empresa = unidade.get("cod_empresa")
        nome_empresa = unidade.get("nome")

        body = {"pag": "funcionario_rotatividade", "cmd": "get", "ano": ano, "cod_empresa": cod_empresa}

        try:
            response = requests.post(API_URL, json=body, headers=get_headers())
            data = response.json()

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
                    "Unidade": nome_empresa,
                    "Ano": ano,
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

        except Exception as e:
            result.append({"Unidade": nome_empresa, "erro": str(e)})

    return jsonify(result)


if __name__ == "__main__":
    app.run(port=10000, debug=True)

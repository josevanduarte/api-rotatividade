# API Flask - Integração i9Saude

API intermediária para consumir os dados do sistema i9Saude, com autenticação via Token SHA256 (Token + Data).

### Rotas disponíveis
- `/` → Teste (status da API)
- `/rotatividade` → Exemplo de consumo da página `funcionario_rotatividade`

### Exemplo de uso
```
GET https://<sua-api>.onrender.com/rotatividade?ano=2025&cod_empresa=10
```

### Deploy no Render
1. Suba este repositório no GitHub
2. Crie um novo **Web Service** no [Render](https://render.com)
3. Conecte ao repositório
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn app:app`

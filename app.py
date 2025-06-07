from flask import Flask, render_template, request, session, redirect, url_for
import gspread
import os
import json
from google.oauth2.service_account import Credentials

app = Flask(__name__)
app.secret_key = 'app_secret_key'

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

credenciais_json = json.loads(os.environ.get('GOOGLE_CREDENTIALS'))
credenciais = Credentials.from_service_account_info(credenciais_json)
credenciais = credenciais.with_scopes([
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
])

cliente = gspread.authorize(credenciais)
ID_SHEET = '1FsDLfIjmcBC8WQGUZ3Fg6VTpr1dtlOeEA8uct5r4LX0'

def obter_dados(nome_aba):
    try:
        sheet = cliente.open_by_key(ID_SHEET)
        aba = sheet.worksheet(nome_aba)
        return aba.get_all_records()
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return []

def paginar(dados, por_pagina=10):
    return [dados[i:i+por_pagina] for i in range(0, len(dados), por_pagina)] if dados else []

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == 'password':
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            error = 'Password incorreta! Tente novamente.'

    # Obter parâmetros de paginação
    params = {
        'veiculos': int(request.args.get('page_veiculos', 1)),
        'alugueres': int(request.args.get('page_alugueres', 1)),
        'clientes': int(request.args.get('page_clientes', 1)),
        'stands': int(request.args.get('page_stands', 1))
    }

    # Obter e paginar dados
    dados = {
        'veiculos': paginar(obter_dados('Veiculos')),
        'alugueres': paginar(obter_dados('Alugueres')),
        'clientes': paginar(obter_dados('Clientes')) if session.get('authenticated') else [],
        'stands': paginar(obter_dados('Stands')) if session.get('authenticated') else []
    }

    contexto = {
        'authenticated': session.get('authenticated', False),
        'error': error,
        'params': params,
        'paginas': {
            tabela: {
                'atual': params[tabela],
                'total': len(dados[tabela]) if dados[tabela] else 0
            } for tabela in ['veiculos', 'alugueres', 'clientes', 'stands']
        }
    }

    for tabela in dados:
        contexto[tabela] = dados[tabela][params[tabela]-1] if dados[tabela] and 1 <= params[tabela] <= len(dados[tabela]) else []

    # Para o mapa dos stands:
    veiculos_lista = obter_dados('Veiculos')
    stands_lista = obter_dados('Stands')
    veiculos_por_stand = {}
    for veiculo in veiculos_lista:
        stand_nome = veiculo.get('Stand', '')
        matricula = veiculo.get('Matrícula', '') or veiculo.get('Matricula', '')
        if stand_nome:
            if stand_nome not in veiculos_por_stand:
                veiculos_por_stand[stand_nome] = []
            veiculos_por_stand[stand_nome].append(matricula)
    stands_mapa = []
    for stand in stands_lista:
        if stand.get('Latitude') and stand.get('Longitude'):
            stands_mapa.append({
                'Nome': stand.get('Stand', ''),
                'Latitude': stand.get('Latitude'),
                'Longitude': stand.get('Longitude'),
                'Matriculas': veiculos_por_stand.get(stand.get('Stand', ''), [])
            })
    contexto['stands_mapa'] = stands_mapa

    return render_template('index.html', **contexto)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

# python app.py (Terminal)

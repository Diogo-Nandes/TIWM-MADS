from flask import Flask, render_template
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# API do Google Sheets
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credenciais = Credentials.from_service_account_file(
    'credenciais.json',
    scopes=SCOPE
)

cliente = gspread.authorize(credenciais)

# ID do Google Sheets
ID_SHEET = '1FsDLfIjmcBC8WQGUZ3Fg6VTpr1dtlOeEA8uct5r4LX0'

def obter_dados(nome_aba):
    sheet = cliente.open_by_key(ID_SHEET)
    aba = sheet.worksheet(nome_aba)
    return aba.get_all_records()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/veiculos')
def veiculos():
    dados = obter_dados('Veiculos')
    return render_template('veiculos.html', veiculos=dados)

@app.route('/clientes')
def clientes():
    dados = obter_dados('Clientes')
    return render_template('clientes.html', clientes=dados)

@app.route('/alugueres')
def alugueres():
    dados = obter_dados('Alugueres')
    return render_template('alugueres.html', alugueres=dados)

if __name__ == '__main__':
    app.run(debug=True)

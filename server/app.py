from flask import Flask, render_template, request, jsonify
from ia import *

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/historique')
def historique():
    return render_template('historique.html')

@app.route('/meteo')
def meteo():
    return render_template('meteo.html')

@app.route('/ai_analysis', methods=['POST'])  # 🚀 point d'entrée pour le JS
def call_ai():
    data = request.get_json()
    meteo = data.get("meteo", "")
    recommendation = analyse_meteo(meteo)
    return jsonify({"recommendation": recommendation})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

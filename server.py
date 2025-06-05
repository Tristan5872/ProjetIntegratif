from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/ai_analysis', methods=['POST'])
def analyse_meteo():
    data = request.get_json()
    meteo = data.get("meteo", "")

    # Écrire les données dans un fichier texte
    with open("meteo.txt", "w", encoding="utf-8") as f:
        f.write(meteo)

    # Construire le prompt
    prompt = f"""
Tu es un assistant spécialisé en prévisions agricoles.

Voici les dernières données météo collectées autour d'une parcelle agricole et de la ville de Limoges. Elles comprennent les conditions actuelles et les prévisions pour aujourd’hui à 15h :

{meteo}

Analyse ces données pour :
- Détecter les **risques météorologiques à venir** (orages, vents violents, fortes pluies, sécheresse, gel, etc.)
- **Prévoir l'évolution probable du temps** sur les prochaines 24-48h à partir des tendances observées.

Ta réponse doit être rédigée en **français clair**, utile, sans mise en forme Markdown, et tenir en **environ 150 mots maximum**.
"""


    try:
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": "Bearer t2ATIIRUknNIxudwTHhrPRjZdExYWbPW",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistral-large-latest",
                "messages": [{"role": "user", "content": prompt}]
            }
        )

        # Débug : afficher toute la réponse brute
        res = response.json()
        print("=== Réponse Mistral ===")
        print(res)

        # Vérification de la présence de 'choices'
        if "choices" in res:
            texte = res["choices"][0]["message"]["content"]
            return jsonify({"recommendation": texte})
        else:
            return jsonify({"recommendation": f"Erreur Mistral : {res}"}), 500

    except Exception as e:
        return jsonify({"recommendation": f"Erreur serveur : {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

import requests, os
from dotenv import load_dotenv

# Charger les variables depuis le fichier .env
load_dotenv()

apiKey = os.getenv("MISTRAL_API")

def analyse_meteo(meteo: str) -> str:
    # Écrire les données dans un fichier texte (optionnel)
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
                "Authorization": apiKey,  # ⚠️ À stocker dans une variable d'environnement en prod
                "Content-Type": "application/json"
            },
            json={
                "model": "mistral-small-latest",
                "messages": [{"role": "user", "content": prompt}]
            }
        )

        res = response.json()
        print("=== Réponse Mistral ===")
        print(res)

        if "choices" in res:
            return res["choices"][0]["message"]["content"]
        else:
            return f"Erreur Mistral : {res}"

    except Exception as e:
        return f"Erreur serveur : {str(e)}"

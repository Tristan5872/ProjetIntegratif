import requests, os
from dotenv import load_dotenv
from markdown import markdown


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

Voici les dernières données météo collectées autour d'une parcelle agricole près de Limoges. Elles comprennent les conditions actuelles et les prévisions pour aujourd’hui à 15h :

{meteo}

Analyse ces données pour :
- Identifier les **risques météorologiques à venir** (orages, vents violents, fortes pluies, sécheresse, gel, etc.)
- **Prévoir l’évolution probable du temps** pour les prochaines 24 à 48h.

Réponds en **français clair**, en utilisant du **Markdown** pour la lisibilité, dans une réponse de **150 mots maximum**. Structure ta réponse comme ceci :

### 🌩️ Risques météorologiques

- ...

### 🌤️ Évolution du temps attendue

- ...

Ne commence pas par « Voici l’analyse : », commence directement avec les titres.
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
            markdown_text = res["choices"][0]["message"]["content"]
            html_output = markdown(markdown_text)
            return html_output

        else:
            return f"Erreur Mistral : {res}"

    except Exception as e:
        return f"Erreur serveur : {str(e)}"

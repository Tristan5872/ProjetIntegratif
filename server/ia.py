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

Voici les données météorologiques collectées autour d'une parcelle agricole près de Limoges. Elles incluent à la fois :
- les **conditions actuelles**,  
- et les **prévisions détaillées sur les prochains jours** (matin, après-midi, soirée).

{meteo}

Analyse attentivement ces informations pour :
- Identifier les **risques météorologiques à venir** (orages, vents violents, fortes pluies, sécheresse, gel, etc.)
- **Prévoir l’évolution probable du temps** sur les **prochaines 24 à 48 heures**, en tenant compte des tendances visibles sur **plusieurs jours**.

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

def analyse_sante(donnees: dict) -> str:
    from markdown import markdown

    # Construction du prompt IA à partir des capteurs
    prompt = f"""
Tu es un assistant agronome spécialisé dans les serres intelligentes.

Voici les dernières mesures de la serre :
- 🌡️ Température intérieure : {donnees['interieur'].get('temperature', 'N/A')} °C
- 💧 Humidité intérieure : {donnees['interieur'].get('humidity', 'N/A')} %
- 🫁 CO₂ intérieur : {donnees['interieur'].get('co2', 'N/A')} ppm
- ☀️ Luminosité intérieure : {donnees['interieur'].get('light', 'N/A')} lux

- 🌡️ Température extérieure : {donnees['exterieur'].get('temperature', 'N/A')} °C
- 💧 Humidité extérieure : {donnees['exterieur'].get('humidity', 'N/A')} %
- ☀️ Luminosité extérieure : {donnees['exterieur'].get('light', 'N/A')} lux

Analyse ces données et indique :
- Si les conditions sont **optimales pour la croissance des plantes**.
- Des **recommandations** d’ajustement simples (chauffage, ventilation, lumière…).
- Utilise un ton **clair et concis**, en **français** (max. 100 mots), en **Markdown**.

Ne reformule pas les données, commence directement par les conseils.
"""

    try:
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": apiKey,
                "Content-Type": "application/json"
            },
            json={
                "model": "mistral-small-latest",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        res = response.json()
        if "choices" in res:
            markdown_text = res["choices"][0]["message"]["content"]
            return markdown(markdown_text)
        else:
            return f"Erreur Mistral : {res}"
    except Exception as e:
        return f"Erreur serveur : {str(e)}"

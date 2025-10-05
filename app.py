from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/data')
def get_data():
    data = []

    # --- Pokémon ---
    try:
        poke_url = "https://pokeapi.co/api/v2/pokemon?limit=5"
        poke_response = requests.get(poke_url)
        poke_response.raise_for_status()
        poke_json = poke_response.json()

        pokemons = []
        for item in poke_json["results"]:
            details_response = requests.get(item["url"])
            details_response.raise_for_status()
            details = details_response.json()
            pokemons.append({
                "type": "Pokemon",
                "name": details["name"].capitalize(),
                "details": f"Height: {details['height']}, Weight: {details['weight']}",
                "image": details["sprites"]["front_default"]
            })
        data.extend(pokemons)
    except requests.exceptions.RequestException as e:
        data.append({"type": "Pokemon", "error": str(e)})

    # --- Los Simpson ---
    try:
        simpson_url = "https://thesimpsonsquoteapi.glitch.me/quotes?count=5"
        simpson_response = requests.get(simpson_url)
        simpson_response.raise_for_status()
        simpson_json = simpson_response.json()

        simpsons = []
        for item in simpson_json:
            simpsons.append({
                "type": "Simpsons",
                "name": item.get("character", "Unknown"),
                "details": item.get("quote", ""),
                "image": item.get("image", "")
            })
        data.extend(simpsons)
    except requests.exceptions.RequestException as e:
        data.append({"type": "Simpsons", "error": str(e)})
    except ValueError:
        # JSON inválido
        data.append({"type": "Simpsons", "error": "Respuesta no es JSON válido"})

    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

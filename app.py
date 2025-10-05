from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/data')
def get_data():
    # Obtener datos de la API de Pokémon
    poke_url = "https://pokeapi.co/api/v2/pokemon?limit=5"
    poke_response = requests.get(poke_url).json()
    pokemons = []
    for item in poke_response["results"]:
        details = requests.get(item["url"]).json()
        pokemons.append({
            "type": "Pokemon",
            "name": details["name"].capitalize(),
            "details": f"Height: {details['height']}, Weight: {details['weight']}",
            "image": details["sprites"]["front_default"]
        })

    # Obtener datos de la API de Los Simpson
    simpson_url = "https://thesimpsonsquoteapi.glitch.me/quotes?count=5"
    simpson_response = requests.get(simpson_url).json()
    simpsons = []
    for item in simpson_response:
        simpsons.append({
            "type": "Simpsons",
            "name": item["character"],
            "details": item["quote"],
            "image": item["image"]
        })

    # Combinar datos
    data = pokemons + simpsons
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

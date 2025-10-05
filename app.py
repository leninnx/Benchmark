from flask import Flask, render_template, jsonify
import requests
import time
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/data')
def get_data():
    data = []

    # --- Pokémon (REST) ---
    poke_info = {}
    start = time.perf_counter()
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
        end = time.perf_counter()
        poke_info = {"type": "Pokemon", "records": len(pokemons), "time": f"{(end-start):.2f} s"}
    except requests.exceptions.RequestException as e:
        poke_info = {"type": "Pokemon", "error": str(e), "records": 0, "time": "0 s"}

    # --- Rick & Morty (GraphQL) ---
    rm_info = {}
    start = time.perf_counter()
    try:
        rick_url = "https://rickandmortyapi.com/graphql"
        query = """
        {
          characters(page:1) {
            results {
              id
              name
              species
              status
              image
            }
          }
        }
        """
        response = requests.post(rick_url, json={'query': query})
        response.raise_for_status()
        data_graphql = response.json()

        for char in data_graphql['data']['characters']['results'][:5]:
            data.append({
                "type": "Rick & Morty",
                "name": char['name'],
                "details": f"{char['species']} - {char['status']}",
                "image": char['image']
            })
        end = time.perf_counter()
        rm_info = {"type": "Rick & Morty", "records": 5, "time": f"{(end-start):.2f} s"}
    except requests.exceptions.RequestException as e:
        rm_info = {"type": "Rick & Morty", "error": str(e), "records": 0, "time": "0 s"}
    except (KeyError, ValueError):
        rm_info = {"type": "Rick & Morty", "error": "Respuesta GraphQL inválida", "records": 0, "time": "0 s"}

    # --- Devolver datos y info ---
    return jsonify({"data": data, "info": [poke_info, rm_info]})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

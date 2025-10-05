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

    # --- Rick & Morty (GraphQL) ---
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

        for char in data_graphql['data']['characters']['results']:
            data.append({
                "type": "Rick & Morty",
                "name": char['name'],
                "details": f"{char['species']} - {char['status']}",
                "image": char['image']
            })
    except requests.exceptions.RequestException as e:
        data.append({"type": "Rick & Morty", "error": str(e)})
    except (KeyError, ValueError):
        data.append({"type": "Rick & Morty", "error": "Respuesta GraphQL inválida"})

    return jsonify(data)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

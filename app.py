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
    poke_times = []
    start_total = time.perf_counter()
    total_bytes = 0
    try:
        poke_url = "https://pokeapi.co/api/v2/pokemon?limit=5"
        response = requests.get(poke_url)
        response.raise_for_status()
        poke_json = response.json()
        total_bytes += len(response.content)
        
        pokemons = []
        for item in poke_json["results"]:
            start = time.perf_counter()
            details_response = requests.get(item["url"])
            details_response.raise_for_status()
            end = time.perf_counter()
            poke_times.append(end - start)
            total_bytes += len(details_response.content)

            details = details_response.json()
            pokemons.append({
                "type": "Pokemon",
                "name": details["name"].capitalize(),
                "details": f"Height: {details['height']}, Weight: {details['weight']}",
                "image": details["sprites"]["front_default"]
            })
        data.extend(pokemons)
        end_total = time.perf_counter()

        poke_info = {
            "type": "Pokemon",
            "records": len(pokemons),
            "time_total": f"{(end_total-start_total):.3f} s",
            "time_avg": f"{(sum(poke_times)/len(poke_times)):.3f} s",
            "time_min": f"{min(poke_times):.3f} s",
            "time_max": f"{max(poke_times):.3f} s",
            "size_bytes": total_bytes
        }
    except requests.exceptions.RequestException as e:
        poke_info = {"type": "Pokemon", "error": str(e), "records": 0, "time_total": "0 s", "size_bytes": 0}

    # --- Rick & Morty (GraphQL) ---
    rm_info = {}
    start_total = time.perf_counter()
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
        end_total = time.perf_counter()
        data_graphql = response.json()

        for char in data_graphql['data']['characters']['results'][:5]:
            data.append({
                "type": "Rick & Morty",
                "name": char['name'],
                "details": f"{char['species']} - {char['status']}",
                "image": char['image']
            })

        rm_info = {
            "type": "Rick & Morty",
            "records": 5,
            "time_total": f"{(end_total-start_total):.3f} s",
            "size_bytes": len(response.content)
        }

    except requests.exceptions.RequestException as e:
        rm_info = {"type": "Rick & Morty", "error": str(e), "records": 0, "time_total": "0 s", "size_bytes": 0}
    except (KeyError, ValueError):
        rm_info = {"type": "Rick & Morty", "error": "Respuesta GraphQL inválida", "records": 0, "time_total": "0 s", "size_bytes": 0}

    return jsonify({"data": data, "info": [poke_info, rm_info]})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

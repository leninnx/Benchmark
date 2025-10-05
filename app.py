from flask import Flask, render_template, jsonify
import requests
import pandas as pd
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
    total_bytes = 0
    calls = 0
    start_total = time.perf_counter()
    try:
        poke_url = "https://pokeapi.co/api/v2/pokemon?limit=5"
        response = requests.get(poke_url)
        response.raise_for_status()
        total_bytes += len(response.content)
        calls += 1
        
        poke_json = response.json()
        pokemons = []
        for item in poke_json["results"]:
            start = time.perf_counter()
            details_response = requests.get(item["url"])
            details_response.raise_for_status()
            end = time.perf_counter()
            poke_times.append(end - start)
            total_bytes += len(details_response.content)
            calls += 1

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
            "size_bytes": total_bytes,
            "calls": calls
        }
    except requests.exceptions.RequestException as e:
        poke_info = {"type": "Pokemon", "error": str(e), "records": 0, "time_total": "0 s", "size_bytes": 0, "calls": calls}

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
            "size_bytes": len(response.content),
            "calls": 1
        }

    except requests.exceptions.RequestException as e:
        rm_info = {"type": "Rick & Morty", "error": str(e), "records": 0, "time_total": "0 s", "size_bytes": 0, "calls": 1}
    except (KeyError, ValueError):
        rm_info = {"type": "Rick & Morty", "error": "Respuesta GraphQL inválida", "records": 0, "time_total": "0 s", "size_bytes": 0, "calls": 1}

    # --- Batch Load CSV/XLS ---
    csv_info = {}
    start_total = time.perf_counter()
    try:
        df = pd.read_csv("archivo.csv")  # si quieres Excel: pd.read_excel("archivo.xlsx")
        df_sample = df.head(5)  # solo 5 registros

        csv_data = []
        for _, row in df_sample.iterrows():
            csv_data.append({
                "type": "CSV",
                "name": row["Nombre"],
                "details": f"Edad: {row['Edad']}, Altura: {row['Altura']}, Peso: {row['Peso']}, Estado: {row['Estado']}",
                "image": ""
            })

        end_total = time.perf_counter()
        csv_info = {
            "type": "CSV",
            "records": len(df_sample),
            "time_total": f"{(end_total-start_total):.3f} s",
            "size_bytes": os.path.getsize("archivo.csv"),
            "calls": 1
        }

        data.extend(csv_data)

    except Exception as e:
        csv_info = {
            "type": "CSV",
            "error": str(e),
            "records": 0,
            "time_total": "0 s",
            "size_bytes": 0,
            "calls": 1
        }

    return jsonify({"data": data, "info": [poke_info, rm_info, csv_info]})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

import requests

API_KEY = "673c957ec774443996bf12bb2d46960f"
BASE_URL = "https://api.rawg.io/api"

def get_similar_games(game_name, count=5):
    search_url = f"{BASE_URL}/games"
    params = {"search": game_name, "key": API_KEY}
    response = requests.get(search_url, params=params)

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} - {response.text}")
    
    results = response.json().get("results", [])
    if not results:
        return []

    game_id = results[0]["id"]
    
    # Fetch game details (to extract genres/tags)
    game_detail_url = f"{BASE_URL}/games/{game_id}"
    detail_resp = requests.get(game_detail_url, params={"key": API_KEY})
    genres = detail_resp.json().get("genres", [])
    if not genres:
        return []
    
    genre_slug = genres[0]["slug"]

    # Find other games in the same genre
    similar_url = f"{BASE_URL}/games"
    similar_params = {"genres": genre_slug, "key": API_KEY, "page_size": count}
    similar_resp = requests.get(similar_url, params=similar_params)
    
    similar_games = similar_resp.json().get("results", [])
    return [
        {"name": game["name"], "rating": game["rating"], "released": game["released"]}
        for game in similar_games if game["name"].lower() != game_name.lower()
    ]
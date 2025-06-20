import requests
import pandas as pd
import time

API_KEY = "" # fetch it from .env
BASE_URL = "https://api.rawg.io/api/games"
PAGE_SIZE = 40  # Max page size allowed
MAX_PAGES = 250  # 1250 * 40 = 50,000 games

def fetch_all_games():
    all_games = []

    for page in range(1, MAX_PAGES + 1):
        print(f"Fetching page {page}/{MAX_PAGES}")
        params = {
            "key": API_KEY,
            "page": page,
            "page_size": PAGE_SIZE,
            "ordering": "-added",  # Order by popularity
        }

        try:
            res = requests.get(BASE_URL, params=params, timeout=10)
            res.raise_for_status()
            results = res.json().get("results", [])
            for game in results:
                all_games.append({
                    "id": game["id"],
                    "name": game["name"],
                    "genres": [g["name"] for g in game.get("genres", [])],
                    "tags": [t["name"] for t in game.get("tags", [])],
                    "platforms": [p["platform"]["name"] for p in game.get("platforms", [])],
                    "rating": game["rating"]
                })
        except Exception as e:
            print(f"Error on page {page}: {e}")
        print(page)
        time.sleep(0.25)  # Be nice to their API
        
    return all_games

def save_games_to_pickle():
    print("start")
    games = fetch_all_games()
    df = pd.DataFrame(games)
    df["features"] = df["genres"] + df["tags"] + df["platforms"]
    df.to_csv("games_df_10k.csv")
    df.to_pickle("games_df_10k.pkl")
    print(f"✅ Saved {len(df)} games to games_df_full.pkl")
    print("end")

if __name__ == "__main__":
    save_games_to_pickle()
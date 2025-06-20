from fastapi import FastAPI, HTTPException, Query
from rawg_client import get_similar_games

app = FastAPI(title="Game Recommender API")

@app.get("/recommend")
def recommend(game_name: str = Query(..., description="Enter the game name")):
    try:
        recommendations = get_similar_games(game_name)
        if not recommendations:
            raise HTTPException(status_code=404, detail="No similar games found.")
        return {"recommendations": recommendations}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
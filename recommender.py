import pandas as pd
import numpy as np
import re
from typing import List, Dict
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize

class GameRecommender:
    def __init__(self, pickle_path: str = "games_df_full.pkl"):
        self.df = pd.read_pickle(pickle_path)
        self.df = self.df.dropna(subset=["features", "rating"]).reset_index(drop=True)

        # Combine all relevant metadata fields into a single searchable column
        self.df["all_text"] = (
            self.df["name"].astype(str) + " " +
            self.df["genres"].astype(str) + " " +
            self.df["tags"].astype(str) + " " +
            self.df["platforms"].astype(str) + " " +
            self.df["features"].astype(str)
        ).str.lower()

        # Vectorize features
        self.vectorizer = CountVectorizer(tokenizer=lambda x: x, lowercase=False)
        self.feature_matrix = self.vectorizer.fit_transform(self.df["features"])
        self.feature_matrix = normalize(self.feature_matrix)  # For cosine similarity

    def find_matching_index(self, game_query: str) -> int:
        query = game_query.lower()
        pattern = re.compile(re.escape(query), re.IGNORECASE)

        # Search using regex in all metadata fields
        matched = self.df[self.df["all_text"].str.contains(pattern)]

        if matched.empty:
            return -1

        # Prefer exact name match if available
        exact_match = matched[matched["name"].str.lower() == query]
        if not exact_match.empty:
            return exact_match.index[0]

        # Otherwise return top-rated match
        return matched.sort_values(by="rating", ascending=False).index[0]

    def recommend_games(self, game_name: str, top_k: int = 5) -> List[Dict[str, float]]:
        idx = self.find_matching_index(game_name)
        if idx == -1:
            print("No relevant game found for:", game_name)
            return []

        query_vector = self.feature_matrix[idx]
        similarities = query_vector @ self.feature_matrix.T  # Sparse dot product
        similarities = similarities.toarray().flatten()

        # Weighted score with rating
        weighted_scores = similarities * (self.df["rating"] / 5.0)
        weighted_scores[idx] = -1  # Exclude the queried game

        top_indices = np.argsort(weighted_scores)[::-1][:top_k]
        return self.df.iloc[top_indices][["name", "rating"]].to_dict(orient="records")

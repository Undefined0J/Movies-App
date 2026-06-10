"""
api_fetcher.py

Handles all HTTP requests to the external OMDb API.
Provides robust error handling and data parsing.
"""

import os
from typing import Optional, Dict, Union
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Replace with your actual OMDb API Key
API_KEY = os.getenv("OMDB_API_KEY")
OMDB_URL = "http://www.omdbapi.com/"


def fetch_movie_data(title: str) -> Optional[Dict[str, Union[str, int, float]]]:
    """
    Fetches movie details from the OMDb API based on the title.

    :param title: The title of the movie to search for.
    :return: A dictionary with movie data, or None if an error occurs/movie not found.
    """
    if not API_KEY:
        print("\nSystem Error: OMDb API key is missing. Please check your .env file.")
        return None

    try:
        response = requests.get(OMDB_URL, params={"apikey": API_KEY, "t": title}, timeout=5)

        # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        response.raise_for_status()

        data = response.json()

        # OMDb API returns "Response": "False" if the movie is not found
        if data.get("Response") == "False":
            print(f"\nAPI Info: {data.get('Error', 'Movie not found.')}")
            return None

        # Safely parse the Year (OMDb sometimes returns strings like '1999–2004')
        try:
            year_str = data.get("Year", "0").split("–")[0]
            year = int(year_str) if year_str.isdigit() else 0
        except ValueError:
            year = 0

        # Safely parse the Rating (OMDb sometimes returns 'N/A')
        try:
            rating_str = data.get("imdbRating", "0.0")
            rating = float(rating_str) if rating_str != "N/A" else 0.0
        except ValueError:
            rating = 0.0

        # Handle missing poster URLs cleanly
        poster_url = data.get("Poster", "")
        if poster_url == "N/A":
            poster_url = ""

        return {
            "title": data.get("Title", title),
            "year": year,
            "rating": rating,
            "poster_url": poster_url
        }

    # Defensive Error Handling for Network Issues
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the API. Please check your internet connection.")
    except requests.exceptions.Timeout:
        print("\nError: The API request timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        print(f"\nError: An unexpected API error occurred: {e}")

    return None

"""
Module for handling persistent storage of movie data in a JSON file.
"""

import json

FILE_PATH = "../data/data.json"


def get_movies():
    """
    Read and return movie data from the JSON storage file.

    Returns:
        dict: A dictionary containing the movies information. If the file
              does not exist or is malformed, an empty dictionary is returned.
    """
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_movies(movies):
    """
    Overwrite the JSON storage file with the provided movie data.

    Args:
        movies (dict): The complete dictionary of movies to be serialized.

    Returns:
        bool: True if saving was successful, False if an IO error occurred.
    """
    try:
        with open(FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(movies, file, indent=4)
        return True
    except IOError as e:
        print(f"Error saving to database: {e}")
        return False


def _get_actual_title(movies, title):
    """
    Helper function to find a case-insensitive match for a movie title.

    Args:
        movies (dict): The dictionary of movies.
        title (str): The search title.

    Returns:
        str or None: The exact key from the dictionary, or None if not found.
    """
    for key in movies:
        if key.lower() == title.lower():
            return key
    return None


def add_movie(title, year, rating):
    """
    Add a new movie to the JSON database if it doesn't already exist.

    Args:
        title (str): The name of the movie.
        year (int): The release year of the movie.
        rating (float): The rating score of the movie (0.0 to 10.0).

    Returns:
        bool: True if added successfully, False if it already exists or saving failed.
    """
    movies = get_movies()

    # Enforce data integrity at the storage level (case-insensitive)
    if _get_actual_title(movies, title) is not None:
        return False

    movies[title] = {
        "year": year,
        "rating": rating
    }
    return save_movies(movies)


def delete_movie(title):
    """
    Delete a movie from the JSON database if it exists.

    Args:
        title (str): The name of the movie to be removed.

    Returns:
        bool: True if deleted successfully, False if not found or saving failed.
    """
    movies = get_movies()
    actual_title = _get_actual_title(movies, title)

    if actual_title:
        movies.pop(actual_title)
        return save_movies(movies)
    return False


def update_movie(title, year, rating):
    """
    Update an existing movie's year and rating in the JSON database.

    Args:
        title (str): The name of the movie to update.
        year (int): The new release year.
        rating (float): The new rating score.

    Returns:
        bool: True if updated successfully, False if not found or saving failed.
    """
    movies = get_movies()
    actual_title = _get_actual_title(movies, title)

    if actual_title:
        movies[actual_title]["year"] = year
        movies[actual_title]["rating"] = rating
        return save_movies(movies)
    return False
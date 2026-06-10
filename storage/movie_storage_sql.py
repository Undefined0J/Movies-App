"""
storage/movie_storage_sql.py

Handles database operations using SQLAlchemy and raw SQL queries.
"""

from typing import Dict, Union
from sqlalchemy import create_engine, text

# Define the database URL
DB_URL = "sqlite:///data/movies.db"

# Create the engine with echo=False for debugging, for cleaner CLI output
engine = create_engine(DB_URL, echo=False)

# Create the movies table if it does not exist
try:
    with engine.connect() as connection:
        # Schema updated: Added poster_url
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL,
                year INTEGER NOT NULL,
                rating REAL NOT NULL,
                poster_url TEXT
            )
        """))
        connection.commit()
except Exception as e:
    print(f"Database initialization error: {e}")


def list_movies() -> Dict[str, Dict[str, Union[int, float]]]:
    """
    Retrieves all movies from the database.

    :return: A dictionary of movies with title as key and year/rating as values.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT title, year, rating, poster_url FROM movies"))
            movies = result.fetchall()

        # Added poster_url to the returned dictionary
        return {
            row[0]: {
                "year": row[1],
                "rating": row[2],
                "poster_url": row[3] if row[3] else ""
            }
            for row in movies
        }
    except Exception as e:
        print(f"Error retrieving movies: {e}")
        return {}


def add_movie(title: str, year: int, rating: float, poster_url: str = "") -> None:
    """
    Adds a new movie to the database.

    :param title: The title of the movie.
    :param year: The release year.
    :param rating: The movie's rating.
    :param poster_url: The URL to the movie poster.
    """
    with engine.connect() as connection:
        try:
            connection.execute(
                text("""
                     INSERT INTO movies (title, year, rating, poster_url)
                     VALUES (:title, :year, :rating, :poster_url)
                     """),
                {
                    "title": title,
                    "year": year,
                    "rating": rating,
                    "poster_url": poster_url
                }
            )
            connection.commit()
            print(f"Movie '{title}' added successfully to the database.")
        except Exception as e:
            # Usually happens if the movie already exists due to UNIQUE constraint
            print(f"Error adding movie (Might already exist): {e}")


def delete_movie(title: str) -> None:
    """
    Deletes a movie from the database by its title.

    :param title: The title of the movie to delete.
    """
    with engine.connect() as connection:
        try:
            connection.execute(
                text("DELETE FROM movies WHERE title = :title"),
                {"title": title}
            )
            connection.commit()
            print(f"Movie '{title}' deleted successfully.")
        except Exception as e:
            print(f"Error deleting movie: {e}")


def update_movie(title: str, rating: float) -> None:
    """
    Updates a movie's rating in the database.

    :param title: The title of the movie to update.
    :param rating: The new rating.
    """
    with engine.connect() as connection:
        try:
            connection.execute(
                text("UPDATE movies SET rating = :rating WHERE title = :title"),
                {"title": title, "rating": rating}
            )
            connection.commit()
            print(f"Movie '{title}' updated successfully.")
        except Exception as e:
            print(f"Error updating movie: {e}")


# --- Sanity Check / Manual Testing ---
if __name__ == "__main__":
    print("\n--- Running Sanity Checks ---\n")

    add_movie("Inception", 2010, 8.8)

    movies_list = list_movies()
    print(movies_list)

    update_movie("Inception", 9.0)
    print(list_movies())

    delete_movie("Inception")
    print(list_movies())

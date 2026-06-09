"""
A modular command-line interface (CLI) application for movie management.
Uses persistent SQL storage via the movie_storage_sql module.
"""

import random
import statistics
from typing import List, Tuple, Optional, Dict, Union

from storage import movie_storage_sql as storage


# --- HELPER FUNCTIONS (INTERNAL) ---

def _pause() -> None:
    """
    Pauses execution and prompts the user to return to the main menu.
    """
    input("\nPress ENTER to return to main menu... ")


def _get_rating(prompt_text: str, allow_empty: bool = False) -> Optional[float]:
    """
    Loops until a valid float rating between 0 and 10 is entered.
    Optionally allows the user to leave the input blank.

    :param prompt_text: The text displayed to request user input.
    :param allow_empty: If True, pressing Enter returns None.
    :return: A validated rating (0.0 to 10.0), or None if left blank.
    """
    while True:
        user_input = input(prompt_text).strip().replace(",", ".")

        if allow_empty and not user_input:
            return None

        try:
            rating = float(user_input)
            if 0 <= rating <= 10:
                return rating
            print("Error: Rating must be between 0 and 10.")
        except ValueError:
            msg = "Error: Invalid rating format. Please enter a number (e.g. 9.8)"
            msg += " or leave blank." if allow_empty else "."
            print(msg)


def _get_year(prompt_text: str, allow_empty: bool = False) -> Optional[int]:
    """
    Loops until a valid integer year is entered.
    Optionally allows the user to leave the input blank.

    :param prompt_text: The text displayed to request user input.
    :param allow_empty: If True, pressing Enter returns None.
    :return: A validated year (1800 to 2100), or None if left blank.
    """
    while True:
        user_input = input(prompt_text).strip()

        if allow_empty and not user_input:
            return None

        try:
            year = int(user_input)
            if 1800 <= year <= 2100:
                return year
            print("Error: Year must be between 1800 and 2100.")
        except ValueError:
            msg = "Error: Invalid year format. Please enter a whole number (e.g. 1994)"
            msg += " or leave blank." if allow_empty else "."
            print(msg)


def _get_matched_movies(movies: Dict[str, Dict[str, Union[int, float]]], query: str) -> List[str]:
    """
    Filters movies by a title substring (case-insensitive).

    :param movies: The dictionary containing movie data.
    :param query: The search string provided by the user.
    :return: A list of movie titles that match the search query.
    """
    return [title for title in movies if query in title.lower()]


def _select_from_list(matches: List[str], action_verb: str) -> Optional[str]:
    """
    Displays a numbered list and returns the user's valid selection.

    :param matches: A list of movie titles to display.
    :param action_verb: The action context (e.g., 'delete', 'update').
    :return: The selected movie title, or None if canceled.
    """
    print("\nMatches found:")
    for index, title in enumerate(matches, 1):
        print(f"{index}. {title}")

    while True:
        choice_str = input(
            f"\nTo {action_verb} a movie, enter the number to make a selection (0 to cancel): "
        ).strip()

        if choice_str.isdigit():
            choice = int(choice_str)
            if choice == 0:
                print("Action canceled.")
                return None

            if 1 <= choice <= len(matches):
                return matches[choice - 1]
        print("Error: Invalid input. Please enter a valid number from the list.")


def _select_movie(
        movies: Dict[str, Dict[str, Union[int, float]]],
        action_verb: str) -> Optional[str]:
    """
    Prompts for a query, finds matches, and delegates to list selection.

    :param movies: The dictionary containing movie data.
    :param action_verb: The action context (e.g., 'delete', 'update').
    :return: The selected movie title, or None if no match/canceled.
    """
    query = input(f"To {action_verb} a movie, "
                  f"enter a title to start the search "
                  f"(or part of it): ").strip().lower()
    matches = _get_matched_movies(movies, query)

    if not matches:
        print(f"No movie found matching '{query}'.")
        return None
    return _select_from_list(matches, action_verb)


def _execute_delete(title: str) -> None:
    """
    Handles the confirmation loop to safely delete a movie.

    :param title: The title of the movie to delete.
    """
    while True:
        confirm = input(f"Delete '{title}'? (y/n): ").strip().lower()
        if confirm == "y":
            storage.delete_movie(title)
            break
        if confirm == "n":
            print("Deletion canceled.")
            break
        print("Error: Please enter 'y' or 'n'.")


def _get_extreme_stats_movies(
        movies: Dict[str, Dict[str, Union[int, float]]],
        find_best: bool = True
) -> List[Tuple[str, Dict[str, Union[int, float]]]]:
    """
    Returns a list of movies with the highest or lowest rating.

    :param movies: The dictionary containing movie data.
    :param find_best: If True, returns top-rated movies; else lowest-rated.
    :return: A list of tuples containing (title, movie_data_dict).
    """
    if not movies:
        return []

    ratings = [float(data["rating"]) for data in movies.values()]
    target = max(ratings) if find_best else min(ratings)
    return [(title, data) for (title, data) in movies.items() if data["rating"] == target]


def _handle_update_menu(current_title: str) -> None:
    """
    Displays a sub-menu to update a movie's attributes interactively.

    :param current_title: The current title of the movie being updated.
    """
    while True:
        movies = storage.list_movies()
        if current_title not in movies:
            break

        current_data = movies[current_title]
        current_rating = current_data["rating"]
        current_year = current_data.get("year", "N/A")

        print(f"\n--- Updating: '{current_title}' "
              f"(Year: {current_year}, Rating: {current_rating}) ---")
        print("1. Update name")
        print("2. Update rating")
        print("0. Return")

        choice = input("\nEnter choice (0-2): ").strip()

        if choice == "1":
            new_title = input(f"Enter new name for '{current_title}': ").strip()
            if not new_title:
                print("Error: Movie title cannot be empty.")
            elif new_title.lower() == current_title.lower():
                print("The name is identical. No changes made.")
            else:
                if new_title not in storage.list_movies():
                    storage.add_movie(new_title, int(current_year), float(current_rating))
                    storage.delete_movie(current_title)
                    current_title = new_title
                else:
                    print(f"Error: A movie named '{new_title}' already exists.")

        elif choice == "2":
            new_rating = _get_rating(f"Enter new rating for '{current_title}' (0-10): ")
            if new_rating is not None:
                storage.update_movie(current_title, float(new_rating))

        elif choice == "0":
            break
        else:
            print("Error: Invalid choice. Please enter 0, 1, or 2.")


def _handle_search_menu(query: str) -> None:
    """
    Displays a sub-menu for acting on search results.

    :param query: The search query used to find the initial matches.
    """
    while True:
        movies = storage.list_movies()
        matches = _get_matched_movies(movies, query)

        if not matches:
            print("\nNo (more) matches left for this search. Returning...")
            break

        print(f"\n--- Search Results for '{query}' ---")
        for title in matches:
            data = movies[title]
            print(f"{title} ({data.get('year', 'N/A')}): {data['rating']}")

        print("\nOptions:")
        print("1. Delete a movie from results")
        print("2. Update a movie from results")
        print("0. Return to main menu")

        choice = input("\nEnter choice (0-2): ").strip()

        if choice == '1':
            movie_to_delete = _select_from_list(matches, "delete")
            if movie_to_delete:
                _execute_delete(movie_to_delete)
        elif choice == '2':
            movie_to_update = _select_from_list(matches, "update")
            if movie_to_update:
                _handle_update_menu(movie_to_update)
        elif choice == '0':
            print("Returning to main menu...")
            break
        else:
            print("Error: Invalid choice.")


# --- CRUD OPERATIONS ---

def list_movies() -> None:
    """
    Fetches and displays all movies in the database.
    """
    movies = storage.list_movies()
    print(f"\n------ {len(movies)} movies in total ------")
    for title, data in movies.items():
        print(f"{title} ({data.get('year', 'N/A')}): {data['rating']}")
    _pause()


def add_movie() -> None:
    """
    Prompts the user for details and adds a new movie to the database.
    """
    while True:
        title = input("Enter new movie title (or 0 to cancel): ").strip()
        if title == '0':
            return
        if not title:
            print("Error: Movie title cannot be empty.")
            continue
        break

    year = _get_year("Enter release year: ")
    if year is None:
        return

    rating = _get_rating("Enter rating (0-10): ")
    if rating is None:
        return

    storage.add_movie(title, int(year), float(rating))


def delete_movie() -> None:
    """
    Entry point to interactively select and delete a movie.
    """
    movies = storage.list_movies()
    movie = _select_movie(movies, "delete")
    if movie:
        _execute_delete(movie)


def update_movie() -> None:
    """
    Entry point to interactively select and update a movie.
    """
    movies = storage.list_movies()
    movie = _select_movie(movies, "update")
    if movie:
        _handle_update_menu(movie)


# --- ANALYSIS & SEARCH ---

def show_stats() -> None:
    """
    Calculates and displays mean, median, and extreme ratings.
    """
    movies = storage.list_movies()
    if not movies:
        print("Database empty.")
        _pause()
        return

    ratings = [float(data["rating"]) for data in movies.values()]
    print(f"\nAverage: {round(statistics.mean(ratings), 1)}")
    print(f"Median:  {round(statistics.median(ratings), 1)}")

    for label, best in [("Best", True), ("Worst", False)]:
        print(f"\n{label} movie(s):")
        for title, data in _get_extreme_stats_movies(movies, best):
            print(f"{title} ({data.get('year', 'N/A')}): {data['rating']}")
    _pause()


def random_movie() -> None:
    """
    Selects and displays a random movie from the database.
    """
    movies = storage.list_movies()
    if movies:
        title = random.choice(list(movies.keys()))
        data = movies[title]
        print(f"\nRandom Pick: {title} ({data.get('year', 'N/A')}) - Rating: {data['rating']}")
    else:
        print("Database empty.")
    _pause()


def search_movie() -> None:
    """
    Prompts the user to search for a movie. Includes a retry loop.
    """
    while True:
        movies = storage.list_movies()
        query = input("Search for: ").strip().lower()
        matches = _get_matched_movies(movies, query)

        if not matches:
            print(f"No matches found for '{query}'.")
            while True:
                retry = input("Do you want to search again? (y/n): ").strip().lower()
                if retry in ['y', 'n']:
                    break
                print("Error: Please enter 'y' or 'n'.")
            if retry == 'n':
                break
        else:
            _handle_search_menu(query)
            break


def sort_movies() -> None:
    """
    Fetches and displays all movies sorted by rating in descending order.
    """
    movies = storage.list_movies()
    sorted_m = sorted(movies.items(), key=lambda item: float(item[1]["rating"]), reverse=True)

    print("\nSorted by Rating:")
    for title, data in sorted_m:
        print(f"{title} ({data.get('year', 'N/A')}): {data['rating']}")
    _pause()


def sort_movies_by_year() -> None:
    """
    Fetches and displays all movies sorted chronologically.
    """
    movies = storage.list_movies()
    if not movies:
        print("Database empty.")
        _pause()
        return

    while True:
        order = input("Do you want the newest movies first? (y/n): ").strip().lower()
        if order in ['y', 'n']:
            break
        print("Error: Please enter 'y' or 'n'.")

    reverse_order = order == 'y'
    sorted_m = sorted(movies.items(), key=lambda
        item: int(item[1].get("year", 0)), reverse=reverse_order)

    print("\nSorted by Year:")
    for title, data in sorted_m:
        print(f"{title} ({data.get('year', 'N/A')}): {data['rating']}")
    _pause()


def filter_movies() -> None:
    """
    Filters movies based on minimum rating, start year, and end year.
    """
    movies = storage.list_movies()
    if not movies:
        print("Database empty.")
        _pause()
        return

    min_rating = _get_rating("Enter minimum rating (leave blank to skip): ", allow_empty=True)
    start_year = _get_year("Enter start year (leave blank to skip): ", allow_empty=True)
    end_year = _get_year("Enter end year (leave blank to skip): ", allow_empty=True)

    print("\nFiltered Movies:")
    matches_found = False

    for title, data in movies.items():
        rating = float(data.get("rating", 0.0))
        year = int(data.get("year", 0))

        if min_rating is not None and rating < min_rating:
            continue
        if start_year is not None and year < start_year:
            continue
        if end_year is not None and year > end_year:
            continue

        print(f"{title} ({year}): {rating}")
        matches_found = True

    if not matches_found:
        print("No movies match your criteria.")
    _pause()


# --- INTERFACE & CONTROL ---

def print_menu() -> None:
    """
    Displays the main menu options to the console.
    """
    print("\n********** My Movies Database **********")
    print("Menu:")
    print("0. Exit")
    print("1. List movies      2. Add movie")
    print("3. Delete movie     4. Update movie")
    print("5. Movie stats      6. Random movie")
    print("7. Search movie     8. Sort by rating")
    print("9. Sort by year    10. Filter movies")


def run_cli() -> None:
    """
    Primary CLI loop managing user interaction and routing.
    """
    actions = {
        "1": list_movies,
        "2": add_movie,
        "3": delete_movie,
        "4": update_movie,
        "5": show_stats,
        "6": random_movie,
        "7": search_movie,
        "8": sort_movies,
        "9": sort_movies_by_year,
        "10": filter_movies,
    }

    while True:
        print_menu()

        while True:
            choice = input("\nEnter choice (0-10): ").strip()
            if choice:
                break

        if choice == "0":
            print("Thanks for using! Bye!\nShoutout to Shoval!")
            break

        if choice in actions:
            actions[choice]()
        else:
            print("Invalid selection. Please try again.")


def main() -> None:
    """
    Application entry point.
    """
    run_cli()


if __name__ == "__main__":
    main()

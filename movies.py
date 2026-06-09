"""
A modular command-line interface (CLI) application for movie management.
Uses persistent storage via the movie_storage module.
"""

import random
import statistics
from storage import movie_storage


# --- HELPER FUNCTIONS (INTERNAL) ---

def _pause():
    """
    Pause execution and prompt the user to return to the main menu.

    Returns:
        None
    """
    input("\nPress ENTER to return to main menu... ")


def _get_rating(prompt_text, allow_empty=False):
    """
    Loop until a valid float rating between 0 and 10 is entered.
    Optionally allows the user to leave the input blank.

    Args:
        prompt_text (str): The text displayed to request user input.
        allow_empty (bool): If True, pressing Enter returns None.

    Returns:
        float or None: A validated rating (0.0 to 10.0), or None if left blank.
    """
    while True:

        # Normalize comma to dot to support European decimal formatting
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


def _get_year(prompt_text, allow_empty=False):
    """
    Loop until a valid integer year is entered.
    Optionally allows the user to leave the input blank.

    Args:
        prompt_text (str): The text displayed to request user input.
        allow_empty (bool): If True, pressing Enter returns None.

    Returns:
        int or None: A validated year (1800 to 2100), or None if left blank.
    """
    while True:
        user_input = input(prompt_text).strip()

        if allow_empty and not user_input:
            return None

        try:
            year = int(user_input)

            # Enforce reasonable historical/future bounds for movie releases
            if 1800 <= year <= 2100:
                return year
            print("Error: Year must be between 1800 and 2100.")
        except ValueError:
            msg = "Error: Invalid year format. Please enter a whole number (e.g. 1994)"
            msg += " or leave blank." if allow_empty else "."
            print(msg)


def _get_matched_movies(movies, query):
    """
    Filter movies by a title substring (case-insensitive).

    Args:
        movies (dict): The dictionary containing movie data.
        query (str): The search string provided by the user.

    Returns:
        list: A list of movie titles that match the search query.
    """
    return [title for title in movies if query in title.lower()]


def _select_from_list(matches, action_verb):
    """
    Display a numbered list and return the user's valid selection.

    Args:
        matches (list): A list of movie titles to display.
        action_verb (str): The action context (e.g., 'delete', 'update').

    Returns:
        str or None: The selected movie title, or None if canceled.
    """
    print("\nMatches found:")
    for index, title in enumerate(matches, 1):
        print(f"{index}. {title}")

    while True:
        choice_str = input(
            f"\nTo continue, to {action_verb} a movie, enter the number to make a selection (0 to cancel): "
        ).strip()
        if choice_str.isdigit():
            choice = int(choice_str)
            if choice == 0:
                print("Action canceled.")
                return None

            # Map the 1-based user input back to the 0-based list index
            if 1 <= choice <= len(matches):
                return matches[choice - 1]
        print("Error: Invalid input. Please enter a valid number from the list.")


def _select_movie(movies, action_verb):
    """
    Prompt for a query, find matches, and delegate to list selection.

    Args:
        movies (dict): The dictionary containing movie data.
        action_verb (str): The action context (e.g., 'delete', 'update').

    Returns:
        str or None: The selected movie title, or None if no match/canceled.
    """
    query = input(f"To {action_verb} a movie, enter a title to start the search (or part of it): ").strip().lower()
    matches = _get_matched_movies(movies, query)
    if not matches:
        print(f"No movie found matching '{query}'.")
        return None
    return _select_from_list(matches, action_verb)


def _execute_delete(title):
    """
    Handle the confirmation loop to safely delete a movie.

    Args:
        title (str): The title of the movie to delete.

    Returns:
        None
    """
    while True:
        confirm = input(f"Delete '{title}'? (y/n): ").strip().lower()
        if confirm == "y":

            # Utilizing the boolean return from storage for direct feedback
            if movie_storage.delete_movie(title):
                print(f"Success: '{title}' deleted.")
            else:
                print(f"Error: Could not delete '{title}'.")
            break
        elif confirm == "n":
            print("Deletion canceled.")
            break
        print("Error: Please enter 'y' or 'n'.")


def _get_extreme_stats_movies(movies, find_best=True):
    """
    Return a list of movies with the highest or lowest rating.

    Args:
        movies (dict): The dictionary containing movie data.
        find_best (bool): If True, returns top-rated movies; else lowest-rated.

    Returns:
        list: A list of tuples containing (title, movie_data_dict).
    """
    if not movies:
        return []

    # Extract all ratings to determine the global minimum or maximum
    ratings = [data["rating"] for data in movies.values()]
    target = max(ratings) if find_best else min(ratings)
    return [(title, data) for (title, data) in movies.items() if data["rating"] == target]


def _handle_update_menu(current_title):
    """
    Display a sub-menu to update a movie's attributes interactively.

    Args:
        current_title (str): The current title of the movie being updated.

    Returns:
        None
    """
    while True:

        # Fetch fresh data to ensure we are working with the latest state
        movies = movie_storage.get_movies()
        if current_title not in movies:
            break

        current_data = movies[current_title]
        current_rating = current_data["rating"]

        # Using .get() to prevent KeyError on legacy data missing the year
        current_year = current_data.get("year", "N/A")

        print(f"\n--- Updating: '{current_title}' (Year: {current_year}, Rating: {current_rating}) ---")
        print("1. Update name")
        print("2. Update year and rating")
        print("0. Return")

        choice = input("\nEnter choice (0-2): ").strip()

        if choice == "1":
            new_title = input(f"Enter new name for '{current_title}': ").strip()
            if not new_title:
                print("Error: Movie title cannot be empty.")
            elif new_title.lower() == current_title.lower():
                print("The name is identical. No changes made.")
            else:
                # Add new entry first. If successful (no duplicate), remove old entry.
                if movie_storage.add_movie(
                    new_title, current_data["year"], current_data["rating"]
                ):
                    movie_storage.delete_movie(current_title)
                    print(f"Success: Name updated to '{new_title}'.")
                    current_title = new_title
                else:
                    print(f"Error: A movie named '{new_title}' already exists.")

        elif choice == "2":
            new_year = _get_year(f"Enter new year for '{current_title}': ")
            new_rating = _get_rating(f"Enter new rating for '{current_title}' (0-10): ")

            if movie_storage.update_movie(current_title, new_year, new_rating):
                print(f"Success: '{current_title}' updated.")
            else:
                print(f"Error: Failed to update '{current_title}'.")

        elif choice == "0":
            break
        else:
            print("Error: Invalid choice. Please enter 0, 1, or 2.")


def _handle_search_menu(query):
    """
    Display a sub-menu for acting on search results.

    Args:
        query (str): The search query used to find the initial matches.

    Returns:
        None
    """
    while True:
        movies = movie_storage.get_movies()
        matches = _get_matched_movies(movies, query)

        # Break out if all previous matches have been deleted or renamed out of scope
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

def list_movies():
    """
    Fetch and display all movies in the database.

    Returns:
        None
    """
    movies = movie_storage.get_movies()
    print(f"\n------ {len(movies)} movies in total ------")
    for title, data in movies.items():
        print(f"{title} ({data.get('year', 'N/A')}): {data['rating']}")
    _pause()


def add_movie():
    """
    Prompt the user for details and add a new movie to the database.
    Includes input validation for title, year, and rating.

    Returns:
        None
    """
    while True:
        title = input("Enter new movie title (or 0 to cancel): ").strip()
        if title == '0':
            return

        # Prevent completely empty inputs
        if not title:
            print("Error: Movie title cannot be empty.")
            continue

        # Delegate existence checks entirely to the storage layer
        break

    year = _get_year("Enter release year: ")
    rating = _get_rating("Enter rating (0-10): ")

    if movie_storage.add_movie(title, year, rating):
        print(f"Added '{title}' ({year}, Rating: {rating}).")
    else:
        print(f"Error: '{title}' already exists in the database or saving failed.")


def delete_movie():
    """
    Entry point to interactively select and delete a movie.

    Returns:
        None
    """
    movies = movie_storage.get_movies()
    movie = _select_movie(movies, "delete")
    if movie:
        _execute_delete(movie)


def update_movie():
    """
    Entry point to interactively select and update a movie.

    Returns:
        None
    """
    movies = movie_storage.get_movies()
    movie = _select_movie(movies, "update")
    if movie:
        _handle_update_menu(movie)


# --- ANALYSIS & SEARCH ---

def show_stats():
    """
    Calculate and display mean, median, and extreme ratings.

    Returns:
        None
    """
    movies = movie_storage.get_movies()
    if not movies:
        print("Database empty.")
        _pause()
        return

    ratings = [data["rating"] for data in movies.values()]
    print(f"\nAverage: {round(statistics.mean(ratings), 1)}")
    print(f"Median:  {round(statistics.median(ratings), 1)}")

    for label, best in [("Best", True), ("Worst", False)]:
        print(f"\n{label} movie(s):")
        for title, data in _get_extreme_stats_movies(movies, best):
            print(f"{title} ({data.get('year', 'N/A')}): {data['rating']}")
    _pause()


def random_movie():
    """
    Select and display a random movie from the database.

    Returns:
        None
    """
    movies = movie_storage.get_movies()
    if movies:
        title = random.choice(list(movies.keys()))
        data = movies[title]
        print(f"\nRandom Pick: {title} ({data.get('year', 'N/A')}) - Rating: {data['rating']}")
    else:
        print("Database empty.")
    _pause()


def search_movie():
    """
    Prompt the user to search for a movie. Includes a retry loop
    and delegates to a sub-menu if matches are found.

    Returns:
        None
    """
    while True:
        movies = movie_storage.get_movies()
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


def sort_movies():
    """
    Fetch and display all movies sorted by rating in descending order.

    Returns:
        None
    """
    movies = movie_storage.get_movies()

    # Sort tuples based on the 'rating' value nested within the movie's data dictionary
    sorted_m = sorted(movies.items(), key=lambda item: item[1]["rating"], reverse=True)

    print("\nSorted by Rating:")
    for title, data in sorted_m:
        print(f"{title} ({data.get('year', 'N/A')}): {data['rating']}")
    _pause()


def sort_movies_by_year():
    """
    Fetch and display all movies sorted chronologically based on user preference.

    Returns:
        None
    """
    movies = movie_storage.get_movies()
    if not movies:
        print("Database empty.")
        _pause()
        return

    while True:
        order = input("Do you want the newest movies first? (y/n): ").strip().lower()
        if order in ['y', 'n']:
            break
        print("Error: Please enter 'y' or 'n'.")

    # Evaluate user preference to set the sort direction (True for descending)
    reverse_order = (order == 'y')

    # Use 0 as a safe fallback key if the 'year' attribute is missing in any record
    sorted_m = sorted(movies.items(), key=lambda item: item[1].get("year", 0), reverse=reverse_order)

    print("\nSorted by Year:")
    for title, data in sorted_m:
        print(f"{title} ({data.get('year', 'N/A')}): {data['rating']}")
    _pause()


def filter_movies():
    """
    Filter movies based on user-defined minimum rating, start year, and end year.
    Empty inputs are ignored during filtering.

    Returns:
        None
    """
    movies = movie_storage.get_movies()
    if not movies:
        print("Database empty.")
        _pause()
        return

    min_rating = _get_rating(
        "Enter minimum rating (leave blank for no minimum rating): ", allow_empty=True
    )
    start_year = _get_year(
        "Enter start year (leave blank for no start year): ", allow_empty=True
    )
    end_year = _get_year(
        "Enter end year (leave blank for no end year): ", allow_empty=True
    )
    print("\nFiltered Movies:")
    matches_found = False

    for title, data in movies.items():

        # Define safe defaults for logic comparison if data points are missing
        rating = data.get("rating", 0.0)
        year = data.get("year", 0)

        # 'is not None' ensures a legitimate 0.0 rating isn't skipped by truthy evaluation
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

def print_menu():
    """
    Display the main menu options to the console.

    Returns:
        None
    """
    print("\n********** My Movies Database **********")
    print("Menu:")
    print("0. Exit")
    print("1. List movies      2. Add movie")
    print("3. Delete movie     4. Update movie")
    print("5. Movie stats      6. Random movie")
    print("7. Search movie     8. Sort by rating")
    print("9. Sort by year    10. Filter movies")


def run_cli():
    """
    Primary CLI loop managing user interaction and routing.

    Returns:
        None
    """

    # Dictionary dispatch pattern for cleaner routing than multiple if/else blocks
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

        # Inner loop to suppress empty inputs (e.g., buffered newlines from terminal)
        # without repeatedly printing the full main menu.
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


def main():
    """
    Application entry point.

    Returns:
        None
    """
    run_cli()


if __name__ == "__main__":
    main()

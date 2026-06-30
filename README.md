# Movies App

## My Movies Database - CLI to Web

A modular Python-based command-line application that manages a personal movie collection using a relational SQLite database, fetches live movie data from an external API, and generates a beautifully styled HTML webpage.

## Description

This project demonstrates a clean separation of concerns by splitting presentation logic, database storage, and external API communication into distinct modules. It fetches real-time movie information (including release years, ratings, and posters) from the [OMDb API](https://www.omdbapi.com/) and stores it persistently using SQLAlchemy. 

Features include:
* Interactive Command-Line Interface (CLI) for full CRUD operations, filtering, and statistical analysis.
* Dynamic API integration using the `requests` library in a dedicated `api_fetcher.py` module.
* Relational database management using SQLAlchemy (`movie_storage_sql.py`) with auto-generated schemas.
* Secure environment variable management for API keys via `python-dotenv`.
* Dynamic HTML generation engine that injects database records into a responsive CSS template.

## Prerequisites

* Python 3.x
* An active API key from the OMDb API.

## Installation

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/Undefined0J/Movies-App
2. Navigate into the project directory:
   ```bash
   cd Movies-App
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
4. Create a `.env` file in the root directory and add your OMDb API key:
   ```bash
   OMDB_API_KEY=your_actual_api_key_here

## Usage

1. Run the main application via the terminal:
   ```bash
   python app.py
2. Navigate the menu by entering a number (0-11).
3. Select Option 2 (Add movie) and simply type a title. The app will automatically fetch the year, rating, and poster from the OMDb API and save it to the database.
4. Select Option 11 (Generate website) to compile your database into a visual grid.
5. Open `web/index.html` in any web browser to view your generated movie collection.

## Have Fun!
### Best regards,   
#### Undefined0J
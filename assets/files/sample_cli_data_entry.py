"""Collect and save a small, curated movie dataset in the terminal."""
# Import required Python modules.
import json
from pathlib import Path
# Import Rich modules for terminal output.
from rich.console import Console
from rich.table import Table

# Create a Rich console for output and define the output file path.
console = Console()
output_file = Path("curated_movies.json")

# These records give the user examples of the fields and the level of detail expected before they enter another movie.
movies = [
    {
        "title": "The Matrix",
        "release_year": 1999,
        "genre": "science fiction",
        "curator_note": "Uses simulated reality to question how people know what is real.",
    },
    {
        "title": "Star Wars",
        "release_year": 1977,
        "genre": "space opera",
        "curator_note": "Combines science-fiction imagery with mythic storytelling.",
    },
]


def display_movies(movie_records):
    """Display the current movie records as a Rich table."""
    # Create a Rich table with columns for title, year, genre, and curator note.
    table = Table(title="Curated Movies")
    table.add_column("Title", style="magenta")
    table.add_column("Year", style="cyan")
    table.add_column("Genre", style="green")
    table.add_column("Curator Note")
    # Add each movie record to the table.
    for movie in movie_records:
        table.add_row(
            movie["title"],
            str(movie["release_year"]),
            movie["genre"],
            movie["curator_note"],
        )

    console.print(table)


def collect_movie():
    """Collect and return one movie record."""

    # Ask the user to enter a value for each field in the movie record.
    title = console.input("[bold]Movie title:[/bold] ").strip()
    release_year = console.input("[bold]Release year:[/bold] ").strip()
    genre = console.input("[bold]Genre:[/bold] ").strip()
    curator_note = console.input(
        "[bold]What makes this movie culturally interesting?[/bold] "
    ).strip()

    movie = {
        "title": title,
        "release_year": int(release_year),
        "genre": genre,
        "curator_note": curator_note,
    }

    return movie


def review_movie(movie):
    """Display one movie and return whether the user confirms it."""
	# Display the movie record and ask the user to confirm it.
    console.print("\n[bold cyan]Please review your entry:[/bold cyan]")
    display_movies([movie])
    confirmation = console.input("Is this correct? Enter yes or no: ").strip().lower()
    return confirmation in ["yes", "y"]


console.print("[bold cyan]Current example data:[/bold cyan]")
display_movies(movies)

# A for loop lets the user enter two records. The user can confirm or reject each entry, and they have one chance to replace an incorrect entry.
for entry_number in range(2):
    console.print(f"\n[bold cyan]Add movie {entry_number + 1} of 2[/bold cyan]")
    new_movie = collect_movie()
    confirmed = review_movie(new_movie)

    # If the first entry is incorrect, give the user one chance to replace it.
    if confirmed is False:
        console.print("[yellow]Let's enter the movie again.[/yellow]\n")
        new_movie = collect_movie()
        confirmed = review_movie(new_movie)

    # Only add a record to the dataset after the user confirms it.
    if confirmed:
        movies.append(new_movie)
        console.print("[green]Movie added.[/green]")
    else:
        console.print("[yellow]This movie will not be saved.[/yellow]")

# json.dumps() turns the list of dictionaries into formatted JSON text.
output_file.write_text(json.dumps(movies, indent=4), encoding="utf-8")

console.print("\n[bold green]Your movie data has been saved.[/bold green]")
# Provide a clickable link to the saved file in the terminal.
console.print(f"File saved at {output_file.resolve()}")

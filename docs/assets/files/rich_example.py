"""Completed Rich examples from the Virtual Environments lesson."""

from rich import print
from rich.console import Console
from rich.table import Table


print("Hello, [bold magenta]World[/bold magenta]!")
console = Console()

movies = [
    {"Released": "Dec 20, 2019", "Title": "Star Wars: The Rise of Skywalker", "Box Office": "$952,110,690"},
    {"Released": "May 25, 2018", "Title": "Solo: A Star Wars Story", "Box Office": "$393,151,347"},
    {"Released": "Dec 15, 2017", "Title": "Star Wars Ep. VIII: The Last Jedi", "Box Office": "$1,332,539,889"},
    {"Released": "Dec 16, 2016", "Title": "Rogue One: A Star Wars Story", "Box Office": "$1,332,439,889"},
]

table = Table(title="Star Wars Movies")
table.add_column("Released", style="cyan", no_wrap=True)
table.add_column("Title", style="magenta")
table.add_column("Box Office", justify="right")

for movie in movies:
    table.add_row(movie["Released"], movie["Title"], movie["Box Office"])

console.print(table)

for movie in movies:
    console.print("\n[bold cyan]Reviewing movie information:[/bold cyan]")
    for field, value in movie.items():
        console.print(f"[magenta]{field}[/magenta]: {value}")

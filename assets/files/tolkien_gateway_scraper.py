"""
Scraping Tolkien Gateway: how much published text stands behind each
Rings of Power character?

IS310 Computing in the Humanities

This script scrapes https://tolkiengateway.net, an independent community-run
Tolkien wiki. Tolkien Gateway's robots.txt permits this kind of small-scale
scraping but explicitly asks crawlers not to go too fast, so every request
goes through get_soup(), which sleeps for a second afterwards.

Run with:
    pip install requests beautifulsoup4 rich
    python tolkien_gateway_scraper.py
"""

import csv
import time

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table

console = Console()

BASE = "https://tolkiengateway.net"
# Identify yourself honestly. Put your own email here.
HEADERS = {"User-Agent": "is310-course-scraper/1.0 (student project; netid@illinois.edu)"}

# Characters the show takes from Tolkien's published writing. The wiki has no
# category for these (they're filed under their own Tolkien categories), so we
# list them ourselves from the show's principal cast.
CANON_CHARACTERS = [
	"Galadriel", "Elrond", "Sauron", "Celebrimbor", "Gil-galad", "Isildur",
	"Elendil", "Tar-Míriel", "Durin IV", "Círdan", "Ar-Pharazôn",
]

# This category contains only the characters invented for the show.
INVENTED_CATEGORY = "Category:The Rings of Power (TV series) characters"


def get_soup(url):
	"""Fetch a page and return its soup, or None if the request failed."""
	try:
		response = requests.get(url, headers=HEADERS, timeout=10)
	except requests.RequestException as error:
		console.print(f"[red]✗ Could not reach {url}: {error}[/red]")
		return None

	if response.status_code != 200:
		console.print(f"[red]✗ {url} returned {response.status_code}[/red]")
		return None

	time.sleep(1)  # the robots.txt asked us to be slow, so we are
	return BeautifulSoup(response.text, "html.parser")


def get_character_details(character_link):
	"""Count the references and categories on a single character page."""
	soup = get_soup(BASE + character_link)
	if soup is None:
		return {"reference_count": 0, "categories": [], "category_count": 0}

	references = soup.select("ol.references li")
	categories = [category.get_text() for category in soup.select("#mw-normal-catlinks li a")]
	return {
		"reference_count": len(references),
		"categories": categories,
		"category_count": len(categories),
	}


def fetch_category_characters(category, source):
	"""Get every page listed in a MediaWiki category, with its details."""
	soup = get_soup(f"{BASE}/wiki/{category.replace(' ', '_')}")
	if soup is None:
		return []

	characters_data = []
	# #mw-pages / .mw-category-group is standard MediaWiki markup, so this
	# same selector works on most wikis, not just this one.
	for character in soup.select("#mw-pages .mw-category-group li a"):
		console.print(f"Processing {character.get_text()}...")
		character_data = {
			"character": character.get_text(),
			"character_link": character.get("href"),
			"source": source,
		}
		character_data.update(get_character_details(character.get("href")))
		characters_data.append(character_data)
	return characters_data


def fetch_named_characters(names, source):
	"""Get details for a hand-picked list of character names."""
	characters_data = []
	for name in names:
		console.print(f"Processing {name}...")
		character_link = "/wiki/" + name.replace(" ", "_")
		character_data = {
			"character": name,
			"character_link": character_link,
			"source": source,
		}
		character_data.update(get_character_details(character_link))
		characters_data.append(character_data)
	return characters_data


# Gather both groups. This takes a few minutes because we pause between
# requests -- that is the correct behavior, not a bug.
invented_characters = fetch_category_characters(INVENTED_CATEGORY, "Created for the show")
canon_characters = fetch_named_characters(CANON_CHARACTERS, "From Tolkien's writings")

all_characters = canon_characters + invented_characters
all_characters.sort(key=lambda character: character["reference_count"], reverse=True)

# Show the top of the list
table = Table(title="Textual Evidence Behind Rings of Power Characters")
table.add_column("Character", style="cyan")
table.add_column("References", style="magenta")
table.add_column("Categories", style="yellow")
table.add_column("Source", style="green")

for character in all_characters[:12]:
	table.add_row(
		character["character"],
		str(character["reference_count"]),
		str(character["category_count"]),
		character["source"],
	)

console.print(table)

# Compare the two groups
for group, label in [(canon_characters, "From Tolkien"), (invented_characters, "Created for show")]:
	average = sum(character["reference_count"] for character in group) / len(group)
	console.print(f"{label:18} n={len(group):3}  average references={average:.1f}")

# Save the data so we can use it later
with open("rings_of_power_characters.csv", "w", newline="") as file:
	writer = csv.writer(file)
	writer.writerow(["character", "character_link", "source", "reference_count", "category_count"])
	for character in all_characters:
		writer.writerow([
			character["character"],
			character["character_link"],
			character["source"],
			character["reference_count"],
			character["category_count"],
		])

console.print(f"[green]✓ Wrote {len(all_characters)} rows to rings_of_power_characters.csv[/green]")

# A caution worth keeping attached to the data: this counts citations that
# wiki editors added, not words that Tolkien wrote. Popular characters attract
# more editors, and more editors add more citations. The number is a proxy.

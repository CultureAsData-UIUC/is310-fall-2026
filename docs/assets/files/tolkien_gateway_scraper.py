"""
Compare how Tolkien Gateway documents characters from The Lord of the Rings and characters created for The Rings of Power.

The script follows character links from two category pages and then visits every character page it discovers. Word counts, character counts, and internal-link counts serve as proxies for how much attention each character page has received.

After activating your virtual environment, install the required packages:
    pip install requests beautifulsoup4 rich

Then replace the email address in `HEADERS` below and run:
    python tolkien_gateway_scraper.py
"""
# Import Python Standard Library modules first, then third-party packages. This order is a common convention, and it helps us see which packages we need to install.
import csv  # Writes the final list of dictionaries to a CSV file.
import time  # Pauses between requests so we do not overwhelm the website.

import requests  # Downloads the HTML for each webpage.
from bs4 import BeautifulSoup  # Makes the downloaded HTML searchable.
from rich.console import Console  # Formats messages printed in the terminal.
from rich.table import Table  # Creates the terminal preview table.


# These constants configure the script and stay the same as it moves from one character to the next. Uppercase names signal that we do not plan to change these values while the script is running.
BASE_URL = "https://tolkiengateway.net" # The main address of the wiki, which we prepend to local links.
LITERARY_CATEGORY_URL = f"{BASE_URL}/wiki/Category:Characters_in_The_Lord_of_the_Rings" # The category containing characters from The Lord of the Rings.
ADAPTATION_CATEGORY_URL = f"{BASE_URL}/wiki/Category:The_Rings_of_Power_(TV_series)_characters" # The category containing characters created for The Rings of Power.
RINGS_OF_POWER_PATH = "/wiki/The_Lord_of_the_Rings:_The_Rings_of_Power" # The internal link used when a character page discusses the television series.
# Change the email address to your own so the wiki can contact you if your scraper causes problems. The wiki's Terms of Use require a valid email address in the User-Agent header.
HEADERS = {
	"User-Agent": "is310-course-scraper/1.0 (student project; netid@illinois.edu)"
}
REQUEST_DELAY = 1.0 # Pause between requests to avoid overwhelming the wiki's servers.
RESULTS_OUTPUT = "tolkien_gateway_characters.csv" # The CSV file where we save the final list of character records.

# We create one Rich console and reuse it for every message and table.
console = Console()

def fetch_soup(url):
	"""
	This function downloads one webpage and turns its HTML into Beautiful Soup.
	
	The url parameter is the only thing that changes between requests, so we pass it into the function. The function returns a Beautiful Soup object that represents the page's HTML, or None if the page could not be downloaded."""
	# The URL changes with every request, so it is a function parameter. The headers and delay remain fixed, so the function reads their constants.

	# If the URL is empty, we cannot download anything, so we return None to signal that the caller should skip this page.
	if not url:
		console.print("[yellow]No URL was found for this page.[/yellow]")
		return None
	# Pass the URL and headers to requests.get() to download the page. The timeout prevents the script from hanging if the wiki is slow to respond.
	response = requests.get(url, headers=HEADERS, timeout=30)
	# Pause for a moment to avoid overwhelming the wiki's servers. The delay is long enough to be polite but short enough that the script does not take forever to run.
	time.sleep(REQUEST_DELAY)
	# If the server did not return a 200 OK response, we cannot parse the page, so we print a warning and return None.
	if response.status_code != 200:
		console.print(f"[red]Could not download {url}: HTTP {response.status_code}[/red]")
		return None

	# Beautiful Soup turns the response's HTML string into searchable elements.
	return BeautifulSoup(response.text, "html.parser")


def scrape_characters(category_page, source_url):
	"""
	This function collects the character names and links listed on one category page.
	
	The category_page parameter is the Beautiful Soup object representing the category page's HTML. The source_url parameter records the category page where we found each character. The function returns a list of dictionaries containing each character's name, type, source URL, and character URL.
	"""
	# The parsed page and its source URL change between the two character groups, so we pass both into the function.
	characters = []
	# If the category page is None, we cannot scrape any characters, so we return an empty list.
	if category_page is None:
		return characters

	# MediaWiki puts category members inside the element with the id mw-pages.
	characters_section = category_page.find(id="mw-pages")
	if characters_section is None:
		return characters

	# We derive the character type from the category page where the character was found.
	if source_url == LITERARY_CATEGORY_URL:
		character_type = "literary"
	else:
		character_type = "adaptation"

	# Each character appears in a list item. We find its link and turn it into one row for our final CSV file.
	character_items = characters_section.find_all("li")
	for item in character_items:
		link = item.find("a", href=True)
		if link is None:
			continue
		# We save the character's visible name, the category page where we found it, and the full URL to the character page.
		characters.append({
			"character": link.get_text(" ", strip=True),
			"character_type": character_type,
			"source_url": source_url,
			"character_url": f"{BASE_URL}{link['href']}",
		})

	return characters


def get_internal_links(content):
	"""
	This function collects internal wiki links from the article content.
	
	The content parameter is the Beautiful Soup object representing the article content. The function returns a list of relative internal wiki paths, including repeated links.
	"""

	# If the content is None, we cannot collect any links, so we return an empty list.
	if content is None:
		return []
	# We use a list so repeated links remain visible in the data.
	links = []
	for link in content.find_all("a", href=True):
		href = link["href"]
		# We retain only relative wiki links and exclude links to page fragments.
		if href.startswith("/wiki/") and "#" not in href:
			links.append(href)
	return links


def analyze_character(character):
	"""
	This function adds page-level text and internal-link counts to one character.
	
	The character parameter is a dictionary containing the character's name, type, source URL, and character URL. The function returns a new dictionary with the same attributes plus word count, character count, total and unique internal-link counts, and a boolean indicating whether a literary character page links to The Rings of Power.
	"""
	# The character dictionary changes with every character, so we pass it into the function fetch_soup() to download the page and parse its HTML into a Beautiful Soup object.
	soup = fetch_soup(character["character_url"])
	# copy() preserves the original discovery data while letting us add measures.
	record = character.copy()
	record["word_count"] = 0
	record["character_count"] = 0
	record["internal_link_count"] = 0
	record["unique_internal_link_count"] = 0
	record["rings_of_power_link"] = False
	# If the soup is None, we cannot analyze the page, so we return the record with zero counts.
	if soup is None:
		return record

	# This selector isolates the article from the site's navigation and footer.
	content = soup.select_one("#mw-content-text .mw-parser-output")
	if content is None:
		return record

	# get_text() extracts visible article text. We count both its characters and its whitespace-separated words.
	article_text = content.get_text(" ", strip=True)
	word_count = len(article_text.split())
	character_count = len(article_text)
	# get_internal_links() gives us every qualifying internal-link occurrence.
	internal_links = get_internal_links(content)
	# We build a second list that keeps each destination only once.
	unique_internal_links = []
	for href in internal_links:
		if href not in unique_internal_links:
			unique_internal_links.append(href)

	# We add the counts to the record dictionary and return it.
	record["word_count"] = word_count
	record["character_count"] = character_count
	record["internal_link_count"] = len(internal_links)
	record["unique_internal_link_count"] = len(unique_internal_links)
	# We only check literary characters for overlap. Adaptation characters already come from the show's original-character category.
	if record["character_type"] == "literary":
		record["rings_of_power_link"] = RINGS_OF_POWER_PATH in internal_links

	return record


def save_csv(records, output_path):
	"""
	This function saves a list of dictionaries as a CSV file.
	
	The records parameter is a list of dictionaries containing character provenance, page measurements, and a possible Rings of Power link. The output_path parameter is the file path where the CSV will be saved. The function does not return anything.
	"""
	# If the records list is empty, we cannot save anything, so we print a warning and return early.
	if not records:
		console.print(f"[yellow]No records to save to {output_path}[/yellow]")
		return

	# newline="" avoids blank rows on Windows, while UTF-8 preserves accented characters returned by the wiki.
	with open(output_path, "w", newline="", encoding="utf-8") as file:
		writer = csv.DictWriter(file, fieldnames=records[0].keys())
		writer.writeheader()
		writer.writerows(records)


def print_results_table(records):
	"""
	This function displays the page-level comparison in the terminal.

	The records parameter is a list of dictionaries containing character provenance, page measurements, and a possible Rings of Power link. The function does not return anything.
	"""
	# Rich Table makes it easy to display a formatted table in the terminal. We create one table with our columns, and then add a row for each record in the for loop below. The table is sorted by word count in descending order so the most documented characters appear first.
	table = Table(title="Literary and Adaptation Character Pages")
	table.add_column("Character", style="cyan")
	table.add_column("Type", style="green")
	table.add_column("Literary Character in Rings of Power", style="magenta")
	table.add_column("Words", justify="right")
	table.add_column("Characters", justify="right")
	table.add_column("All Links", justify="right")
	table.add_column("Unique Links", justify="right")

	# sorted() creates a display order without changing the original CSV order.
	for record in sorted(records, key=lambda record: record["word_count"], reverse=True):
		table.add_row(
			record["character"],
			record["character_type"],
			str(record["rings_of_power_link"]),
			str(record["word_count"]),
			str(record["character_count"]),
			str(record["internal_link_count"]),
			str(record["unique_internal_link_count"]),
		)

	console.print(table)


def main():
	"""
	This function orchestrates the scraping and analysis of character pages from the Tolkien Gateway. `main()` is the entry point of the script, does not take any parameters, and does not return anything, but it prints progress messages to the terminal and saves the final results to a CSV file. We commonly use a `main()` function to encapsulate the script's logic and make it easier to read and maintain.
	"""
	# First we download the literary category page and collect all of its character links.
	console.print("[cyan]Finding The Lord of the Rings characters...[/cyan]")
	literary_page = fetch_soup(LITERARY_CATEGORY_URL)
	literary_characters = scrape_characters(
		literary_page,
		LITERARY_CATEGORY_URL,
	)

	# Then we download the adaptation category page and collect all of its character links.
	console.print("[cyan]Finding The Rings of Power characters...[/cyan]")
	adaptation_character_page = fetch_soup(ADAPTATION_CATEGORY_URL)
	adaptation_characters = scrape_characters(
		adaptation_character_page,
		ADAPTATION_CATEGORY_URL,
	)

	# Combining the lists gives us one consistent set of records to process.
	all_characters = literary_characters + adaptation_characters
	console.print(f"[green]Found {len(all_characters)} character pages.[/green]")
	# We then visit each character page to count words and internal links, which serve as proxies for how much attention the wiki has given to each character.
	results = []
	for number, character in enumerate(all_characters, start=1):
		console.print(f"Processing {number}/{len(all_characters)}: {character['character']}")
		results.append(analyze_character(character))
	# Finally, we display the results in a table and save them to a CSV file.
	print_results_table(results)
	save_csv(results, RESULTS_OUTPUT)
	console.print(f"[green]Saved {len(results)} analyzed character pages to {RESULTS_OUTPUT}[/green]")

# The script's entry point. When the script is run directly, the main() function is called to start the scraping and analysis process. The use of `if __name__ == "__main__":` is common in Python scripts to allow the file to be imported as a module without executing the main logic and also because Python sets the `__name__` variable to `"__main__"` when the script is run directly.
if __name__ == "__main__":
	main()

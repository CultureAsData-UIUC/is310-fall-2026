import re
import cloudscraper
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table

console = Console()

# Create a cloudscraper instance to handle Cloudflare bot protection
scraper = cloudscraper.create_scraper()

def get_character_languages(url):
    try:
        response = scraper.get(url, timeout=10)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        languages = soup.find_all('a', attrs={'data-tracking-label': re.compile(r'lang-')})
        return [{"language": language.get('data-tracking-label'), "language_name": language.get_text()} for language in languages]
    except Exception as e:
        console.print(f"[red]✗ Error getting languages from {url}: {e}[/red]")
        return []

def fetch_characters(url, category):
    try:
        response = scraper.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        characters = soup.find_all('a', class_='category-page__member-link')
        characters_data = []

        for character in characters:
            console.print(f"Processing {character.get_text()}...")
            character_data = {
                "character": character.get_text(),
                "character_link": character.get('href'),
                "category": category
            }
            character_data['languages'] = get_character_languages("https://lotr.fandom.com" + character_data['character_link'])
            character_data['languages_count'] = len(character_data['languages'])
            characters_data.append(character_data)

        return characters_data
    except Exception as e:
        console.print(f"[red]✗ Error in fetch_characters: {e}[/red]")
        return []

# Fetch characters from the given URLs
canon_characters_data = fetch_characters("https://lotr.fandom.com/wiki/Category:Canon_characters_in_The_Rings_of_Power", "Canon")
new_characters_data = fetch_characters("https://lotr.fandom.com/wiki/Category:Characters_created_for_The_Rings_of_Power", "New")

# Combine and sort characters by language count
all_characters_data = canon_characters_data + new_characters_data
sorted_characters = sorted(all_characters_data, key=lambda x: x['languages_count'], reverse=True)

# Display the sorted characters in a table
table = Table(title="Translations of LOTR Canon Characters VS New Characters")
table.add_column("Character", style="cyan")
table.add_column("Language Count", style="magenta")
table.add_column("Category", style="green")

for character in sorted_characters:
    table.add_row(character['character'], str(character['languages_count']), character['category'])

console.print(table)
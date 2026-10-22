"""Examples from the Getting Cultural Data From APIs lesson.

Install the required packages inside your activated virtual environment:

    python -m pip install requests beautifulsoup4 rich apikey nrh-lotr==0.0.3 internetarchive

Replace the placeholder information in HEADERS and save your API key before running the script.
"""
# Import the Python Standard Libraries first
import time
# Import the third-party libraries
import apikey
import internetarchive
import requests
from bs4 import BeautifulSoup
from lotr import LOTR
from rich.console import Console


console = Console()


# Always identify yourself honestly when an API asks for a User-Agent. Replace these placeholders with your own GitHub Pages URL and Illinois email address.
HEADERS = {
	"User-Agent": "is310-course/1.0 (https://YOUR-USERNAME.github.io; YOUR_NETID@illinois.edu)"
}

API_URL = "https://lotr.fandom.com/api.php"
BOOKS_URL = "https://the-one-api.dev/v2/book"
CHARACTERS_URL = "https://the-one-api.dev/v2/character"


# ---------------------------------------------------------------------------
# 1. Querying the LOTR Fandom MediaWiki API
# ---------------------------------------------------------------------------

# action=query asks MediaWiki for structured information. The categorymembers list module returns pages assigned to the selected category.
params = {
	"action": "query",
	"list": "categorymembers",
	"cmtitle": "Category:Canon_characters_in_The_Rings_of_Power",
	"cmtype": "page",
	"cmlimit": "max",
	"format": "json",
}
# We pass our params dictionary to requests.get() so that it is automatically encoded into the URL's query string. The headers dictionary is passed to identify our script honestly. We also set a timeout to avoid waiting indefinitely for a response.
category_response = requests.get(
	API_URL,
	params=params,
	headers=HEADERS,
	timeout=15,
)

console.print("MediaWiki category request:", category_response.status_code)
# If the request is successful, we can parse the JSON response and print the titles of the pages in the category.
if category_response.status_code == 200:
	category_data = category_response.json()
	for page in category_data["query"]["categorymembers"]:
		console.print(page["title"])

# We create a function to analyze one character page, returning the page length and link measures. The function uses the parse action to retrieve the rendered HTML, internal links, and language links for the specified page title. It counts the number of words, characters, internal links, unique internal links, and language links on the page.
def analyze_fandom_page(title):
	"""Return page-length and link measures for one Fandom character page."""

	# action=parse asks MediaWiki to process one page. The pipe character lets us request rendered text, internal links, and language links together.
	response = requests.get(
		API_URL,
		params={
			"action": "parse",
			"page": title,
			"prop": "text|links|langlinks",
			"format": "json",
		},
		headers=HEADERS,
		timeout=15,
	)

	if response.status_code != 200:
		console.print(f"Could not retrieve {title}: {response.status_code}")
		return None

	data = response.json()
	if "error" in data:
		console.print(f"Could not parse {title}: {data['error']['info']}")
		return None

	page = data["parse"]
	# MediaWiki stores the rendered HTML under the literal dictionary key "*".
	html = page["text"]["*"]
	soup = BeautifulSoup(html, "html.parser")
	article_text = soup.get_text(" ", strip=True)

	# Count every internal wiki link that does not point to a page fragment.
	internal_links = []
	for link in soup.find_all("a", href=True):
		href = link["href"]
		if href.startswith("/wiki/") and "#" not in href:
			internal_links.append(href)

	# Build a second list that keeps each destination only once.
	unique_internal_links = []
	for href in internal_links:
		if href not in unique_internal_links:
			unique_internal_links.append(href)

	return {
		"character": page["title"],
		"word_count": len(article_text.split()),
		"character_count": len(article_text),
		"internal_link_count": len(internal_links),
		"unique_internal_link_count": len(unique_internal_links),
		"language_link_count": len(page.get("langlinks", [])),
	}


# Compare one literary character with characters created for the adaptation. Rather than defining the character pages, we could update the script to retrieve the list of pages from the categorymembers request above. We could also save the results to a CSV file for later analysis. 
CHARACTERS = ["Galadriel", "Arondir", "Halbrand", "Disa"]

for character in CHARACTERS:
	result = analyze_fandom_page(character)
	if result is not None:
		console.print(result)


# ---------------------------------------------------------------------------
# 2. Public and authenticated requests to The One API
# ---------------------------------------------------------------------------

# The books endpoint is public and introduces the JSON response structure.
books_response = requests.get(BOOKS_URL, timeout=15)

console.print("The One API books request:", books_response.status_code)
if books_response.status_code == 200:
	books_data = books_response.json()
	console.print(books_data)
	console.print("Response keys:", books_data.keys())


# The character endpoint demonstrates what happens without authentication.
unauthenticated_response = requests.get(CHARACTERS_URL, timeout=15)
console.print("Unauthenticated character request:", unauthenticated_response.status_code)


# First save the key once in a terminal or short setup script:
#
# import apikey
# apikey.save("THE_ONE_API_KEY", "YOUR_API_KEY_HERE")
#
# The key is loaded from protected local storage rather than written here.
THE_ONE_API_KEY = apikey.load("THE_ONE_API_KEY")
AUTHORIZATION_HEADERS = {
	"Authorization": "Bearer " + THE_ONE_API_KEY,
}

# Request all character records and inspect the response structure.
characters_response = requests.get(
	CHARACTERS_URL,
	headers=AUTHORIZATION_HEADERS,
	timeout=15,
)

if characters_response.status_code == 200:
	characters_data = characters_response.json()
	console.print(characters_data.keys())
	console.print("Total characters:", characters_data["total"])

	# Filter the downloaded records locally in Python.
	for character in characters_data["docs"]:
		if character["name"] == "Galadriel":
			console.print(character)

# Ask the server to return only Galadriel by passing a query parameter.
params = {"name": "Galadriel"}

galadriel_response = requests.get(
	CHARACTERS_URL,
	headers=AUTHORIZATION_HEADERS,
	params=params,
	timeout=15,
)

if galadriel_response.status_code == 200:
	galadriel_data = galadriel_response.json()
	console.print(galadriel_response.url)
	console.print(galadriel_data)

	# Use Galadriel's identifier to request the related quote endpoint.
	galadriel_id = galadriel_data["docs"][0]["_id"]
	quote_url = f"{CHARACTERS_URL}/{galadriel_id}/quote"
	quote_response = requests.get(
		quote_url,
		headers=AUTHORIZATION_HEADERS,
		timeout=15,
	)
	console.print(quote_response.json())

# Multiple query parameters can filter on more than one condition.
params = {
	"name!": "Galadriel",
	"race": "Elf",
}

elves_response = requests.get(
	CHARACTERS_URL,
	headers=AUTHORIZATION_HEADERS,
	params=params,
	timeout=15,
)

if elves_response.status_code == 200:
	console.print(elves_response.url)
	console.print(
		"Total number of elves besides Galadriel:",
		elves_response.json()["total"],
	)

# Pausing between repeated requests helps us respect an API's rate limits.
time.sleep(10)


# ---------------------------------------------------------------------------
# 3. Using a third-party API wrapper
# ---------------------------------------------------------------------------

lotr = LOTR(THE_ONE_API_KEY)

# The quotes method currently works. The lesson explains why the wrapper's movies method fails when its Pydantic types do not match the live API.
quotes = lotr.quotes(limit=5)
console.print(quotes)


# ---------------------------------------------------------------------------
# 4. Searching a cultural collection with the Internet Archive library
# ---------------------------------------------------------------------------

INTERNET_ARCHIVE_QUERY = 'title:"Lord of the Rings" AND mediatype:texts'

search = internetarchive.search_items(
	INTERNET_ARCHIVE_QUERY,
	fields=["identifier", "title", "date"],
)

# Keep three compact search results rather than downloading every match.
results = []
for result in search:
	results.append(result)
	if len(results) == 3:
		break

for result in results:
	console.print(result.get("identifier"), result.get("title"))

if len(results) > 0:
	first_identifier = results[0]["identifier"]
	item = internetarchive.get_item(first_identifier)
	metadata = item.metadata

	console.print("Title:", metadata.get("title"))
	console.print("Creator:", metadata.get("creator"))
	console.print("Date:", metadata.get("date"))
	console.print("Media type:", metadata.get("mediatype"))
	console.print("Collection:", metadata.get("collection"))
	console.print("License:", metadata.get("licenseurl"))

	# An item can contain an original upload and several derived files.
	for file in list(item.files)[:10]:
		console.print(file.get("name"), file.get("format"))

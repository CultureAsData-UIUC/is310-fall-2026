import csv
import time

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.gutenberg.org"
TOP_BOOKS_URL = f"{BASE_URL}/browse/scores/top"
HEADERS = {
	"User-Agent": "is310-course-scraper/1.0 (student project; netid@illinois.edu)"
}
REQUEST_DELAY = 1


def check_gutenberg_page_exists(relative_url):
	"""Check whether a relative Project Gutenberg link returns a webpage."""

	full_url = f"{BASE_URL}{relative_url}"
	response = requests.get(full_url, headers=HEADERS, timeout=30)
	time.sleep(REQUEST_DELAY)

	if response.status_code == 200:
		return True
	else:
		return False


def save_csv(records, filename, fieldnames):
	"""Save a list of dictionaries as a CSV file."""

	with open(filename, "w", newline="", encoding="utf-8") as file:
		writer = csv.DictWriter(file, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(records)


# Request the Top 100 page and inspect the server's response before parsing it.
response = requests.get(TOP_BOOKS_URL, headers=HEADERS, timeout=30)
print("Status code:", response.status_code)

if response.status_code == 200:
	# Parse the returned HTML into a Beautiful Soup object.
	soup = BeautifulSoup(response.text, "html.parser")
	top_lists = soup.find_all("h2")

	books = []
	authors = []

	# Each relevant h2 names a Top list. Its next ordered list contains the items.
	for top_list in top_lists:
		top_list_name = top_list.get_text(" ", strip=True)
		if "Top" not in top_list_name:
			continue

		ordered_list = top_list.find_next("ol")
		if ordered_list is None:
			continue

		top_list_items = ordered_list.find_all("li")
		for item in top_list_items:
			link = item.find("a", href=True)
			if link is None:
				continue

			relative_url = link.get("href")
			full_url = f"{BASE_URL}{relative_url}"
			page_exists = check_gutenberg_page_exists(relative_url)

			if "EBooks" in top_list_name:
				books.append({
					"top_list": top_list_name,
					"book_title": item.get_text(" ", strip=True),
					"book_link": full_url,
					"webpage_exists": page_exists,
				})
			else:
				authors.append({
					"top_list": top_list_name,
					"author_name": item.get_text(" ", strip=True),
					"author_link": full_url,
					"webpage_exists": page_exists,
				})

	save_csv(
		books,
		"top_100_ebooks.csv",
		["top_list", "book_title", "book_link", "webpage_exists"],
	)
	save_csv(
		authors,
		"top_100_authors.csv",
		["top_list", "author_name", "author_link", "webpage_exists"],
	)

	print(f"Saved {len(books)} book records to top_100_ebooks.csv")
	print(f"Saved {len(authors)} author records to top_100_authors.csv")
else:
	print("Project Gutenberg did not return the expected page, so no data was saved.")

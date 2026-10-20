import requests
from bs4 import BeautifulSoup

html_doc = """
<html>
  <head><title>The Dormouse's story</title></head>
  <body>
    <p class="title"><b>The Dormouse's story</b></p>
	<a href="http://example.com/elsie" class="sister">Elsie</a>
    <p class="story">
      Once upon a time there were three little sisters:
      <a href="http://example.com/elsie" class="sister">Elsie</a>,
      <a href="http://example.com/lacie" class="sister">Lacie</a>, and
      <a href="http://example.com/tillie" class="sister">Tillie</a>.
    </p>
  </body>
</html>
"""
# print(type(html_doc))
# soup = BeautifulSoup(html_doc, "html.parser")
# links = soup.find_all('a')

# for link in links:
# 	print(link.get('href'), link.get_text())

# with open("Top100_ProjectGutenberg.html", "r") as html_file:
# 	html_content = html_file.read()

response = requests.get("https://www.gutenberg.org/browse/scores/top")
# print(response.text)
print(response.status_code)
print(response.headers)

soup = BeautifulSoup(response.text, "html.parser")
top100_yesterday_header = soup.find(id="books-last1")
top100_yesterday_ebooks = top100_yesterday_header.find_next().find_all("a")
processed_top100_ebooks = []
for link in top100_yesterday_ebooks[0:10]:
	print(link.get('href'), link.get_text())
	link_dict = {}
	link_dict["top100ebook_title"] = link.get_text()
	link_dict["top100ebook_link"] = "https://www.gutenberg.org" + link.get('href')
	book_page = requests.get(link_dict["top100ebook_link"])
	book_soup = BeautifulSoup(book_page.text, "html.parser")
	book_table = book_soup.find(id="about_book_table")
	book_table_rows = book_table.find_all("tr")
	link_dict["book_author"] = ""
	link_dict["book_author_link"] = ""
	link_dict["book_translator"] = ""
	link_dict["book_translator_link"] = ""
	link_dict["isbn"] = ""
	for row in book_table_rows:
		table_header = row.find("th").get_text()
		if table_header == "Author":
			link_dict["book_author"] = row.find("a").get_text()
			link_dict["book_author_link"] = row.find("a").get("href")
		elif table_header == "Translator":
			link_dict["book_translator"] = row.find("a").get_text()
			link_dict["book_translator_link"] = row.find("a").get("href")
		elif table_header == "ISBN (HTML)":
			link_dict["isbn"] = row.find("td").get_text()
	processed_top100_ebooks.append(link_dict)
print(processed_top100_ebooks)

import csv

with open('top_100_ebooks_yesterday.csv', 'w') as file:
    writer = csv.writer(file)
    # Write the headers
    writer.writerow(['top100ebook_title', 'top100ebook_link', 'book_author', 'book_author_link', 'book_translator', 'book_translator_link', 'isbn'])
    for book in processed_top100_ebooks:
        writer.writerow([book['top100ebook_title'], book['top100ebook_link'], book['book_author'], book['book_author_link'], book['book_translator'], book['book_translator_link'], book['isbn']])

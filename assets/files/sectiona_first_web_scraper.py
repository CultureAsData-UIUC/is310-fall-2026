import requests
from bs4 import BeautifulSoup
import csv
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

# soup = BeautifulSoup(html_doc, "html.parser")
# print(soup.prettify())
# print(soup.title)
# links = soup.find_all("a")

# for link in links:
# 	link_text = link.get_text()
# 	link_href = link.get("href")
# 	print("link text:", link_text)
# 	print("link href:", link_href)

# with open("Top100_ProjectGutenberg.html", "r") as html_file:
# 	top100_html = html_file.read()

response = requests.get("https://www.gutenberg.org/browse/scores/top")
print(response.status_code)
print(response.headers)
# print(response.text)

soup = BeautifulSoup(response.text, "html.parser")
top100_yesterday_header = soup.find(id="books-last1")
print(top100_yesterday_header)
ol_links = top100_yesterday_header.find_next("ol").find_all("a")
# print("ol_links", ol_links)
top100_yesterday_links = []
for link in ol_links:
	print("link", link)
	link_dict = {}
	link_dict["book_link"] = "https://www.gutenberg.org" +link.get("href")
	link_dict["book_title"] = link.get_text()
	page_response = requests.get(link_dict["book_link"])
	table_response = BeautifulSoup(page_response.text, "html.parser")
	table_html = table_response.find_all(id="about_book_table")
	# print(table_html, type(table_html))
	table_row = table_html[0].find("tr")
	table_header = table_row.find("th").get_text()
	table_link = table_row.find("a")
	link_dict["book_author"] = ""
	link_dict["book_author_link"] = ""
	link_dict["book_translator"] = ""
	link_dict["book_translator_link"] = ""
	if table_header == "Author":
		link_dict["book_author"] = table_link.get_text()
		link_dict["book_author_link"] = table_link.get("href")
	else:
		link_dict["book_translator"] = table_link.get_text()
		link_dict["book_translator_link"] = table_link.get("href")
	# print(link_dict)
	top100_yesterday_links.append(link_dict)
print(top100_yesterday_links)

with open("top100_ebooks_yesterday.csv", "w") as csv_file:
	writer = csv.writer(csv_file)
	# Write the headers
	writer.writerow(['book_author', 'book_title', 'book_author_link', 'book_link', 'book_translator', 'book_translator_link'])
	for book in top100_yesterday_links:
		writer.writerow([book['book_author'], book['book_title'], book['book_link'], book['book_author_link'], book['book_translator'], book['book_translator_link']])
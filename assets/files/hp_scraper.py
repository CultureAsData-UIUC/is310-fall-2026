import cloudscraper
from bs4 import BeautifulSoup
import time

start = time.time()
scraper = cloudscraper.create_scraper()
response = scraper.get("https://harrypotter.fandom.com/wiki/Harry_Potter")

if response.status_code != 200:
	print("Script not working")

soup = BeautifulSoup(response.text, "html.parser")
# div = soup.find_all("div", class_="wds-dropdown__content")

# # language_links = div.find_all("li")
# for link in div:
# 	print("#####")
# 	print(link)

links = soup.find_all("a")
data = []
for link in links:
	if link.get("data-tracking-label"):
		data_tracking_label = link.get("data-tracking-label")
		# print(data_tracking_label)
		if "lang" in data_tracking_label:
			language_link = link.get("href")
			language_name = link.get_text()
			data.append({"language_link": language_link, "language_name": language_name})
print(data)
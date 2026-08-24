from bs4 import BeautifulSoup
import requests

response = requests.get("https://www.gutenberg.org/browse/scores/top")
print("Status code:", response.status_code)
print("Headers:", response.headers)
print("Content:", response.text[:500])  # Print the first 500 characters of the content
soup = BeautifulSoup(response.text, 'html.parser')
# print(soup.prettify()[:500])  # Print the first 500 characters of the prettified HTML
# links = soup.find_all('a')
# # for link in links:
# # 	if 'ebooks' in link.get('href'):
# # 		print(link.get('href'))
# # 		print(link.get_text())

data = [
]
headers = soup.find_all('h2')
for header in headers:
	if 'Top' in header.get_text():
		top_header = header.get_text()
		data.append({"title": top_header, "items": []})
		list_of_links = header.find_next_sibling('ol').find_all('a')
		for link in list_of_links:
			if 'ebooks' in link.get('href'):
				data[-1]["items"].append({"link": link.get('href'), "title": link.get_text()})
print(data[0])
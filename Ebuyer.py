import requests
from bs4 import BeautifulSoup

Shop = "https://www.ebuyer.com"
URL = "https://www.ebuyer.com/search?q="
search = input("Product search: ")
page = requests.get(URL+search)

soup = BeautifulSoup(page.content, "html.parser")

results = soup.find(id="main-content")

job_elements = results.find_all("div", class_="grid-item js-listing-product")

for job_element in job_elements:
    name_element = job_element.find("h3", class_="grid-item__title")
    price_element = job_element.find("p", class_="price")
    for a in name_element.find_all('a', href=True):
        link = a['href']
    if price_element is not None:
        print("Product_name: ", name_element.text.strip())
        print("Link: ", Shop+link)
        print("Price: ", price_element.text.strip())
        print()






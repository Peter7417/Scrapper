import requests
from bs4 import BeautifulSoup
from duckduckgo_search import ddg


user_search = input("Product search: ")
box_search = user_search + " box co uk"
search_matrix = ddg(box_search, max_results=15)

for response in search_matrix:
    title = response["title"]
    if title.find("Box.co.uk") > 0:
        URL = (response["href"])
        break

page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

results = soup.find(class_="wrapper")
job_elements = results.find_all("div", class_="product-list-item")
job_elements_middle = results.find_all("div", class_="product-list-item middle")
job_elements_direct = results.find_all("div", class_="p-wrapper form-wait")


for job_element in job_elements:
    name_element = job_element.find("div", class_="p-list-title-wrapper")
    price_element = job_element.find("div", class_="p-list-price")
    for a in name_element.find_all('a', href=True):
         link = a['href']
    if price_element is not None:
        print("Product_name: ", name_element.text.strip())
        print("Link: ", link)
        print("Price: ", price_element.text.strip())
        print()

for job_element_middle in job_elements_middle:
    name_element = job_element_middle.find("div", class_="p-list-title-wrapper")
    price_element = job_element_middle.find("div", class_="p-list-price")
    for a in name_element.find_all('a', href=True):
         link = a['href']
    if price_element is not None:
        print("Product_name: ", name_element.text.strip())
        print("Link: ", link)
        print("Price: ", price_element.text.strip())
        print()


for job_element_direct in job_elements_direct:
    name_element = job_element_direct.find("h2", class_="p-title-desc")
    price_element = job_element_direct.find("p", class_="p-price-inc")
    if price_element is not None:
        print("Product_name: ", name_element.text.strip())
        print("Link: ", URL)
        print("Price: ", price_element.text.strip())
        print()

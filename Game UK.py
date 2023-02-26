import requests
from bs4 import BeautifulSoup
from duckduckgo_search import ddg
import search


user_search = input("Product search: ")
game_search = user_search + " game co uk"
print(game_search)
search_matrix = ddg(game_search, max_results=5)

for response in search_matrix:
    title = response["title"]
    print(title)
    if title.find("game") > 0:
        URL = (response["href"])
        print(URL)
        break

page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

results = soup.find(id="plp")
job_elements = results.find_all("div", class_="product")
# job_elements_middle = results.find_all("div", class_="product-list-item middle")


for job_element in job_elements:
    # name_element = job_element.find("div", class_="p-list-title-wrapper")
    price_element = job_element.find("a", class_="mintPrice row")
    # for a in name_element.find_all('a', href=True):
    #      link = a['href']
    if price_element is not None:
        # print("Product_name: ", name_element.text.strip())
        # print("Link: ", link)
        print("Price: ", price_element.text.strip())
        print()

# for job_element_middle in job_elements_middle:
#     name_element = job_element_middle.find("div", class_="p-list-title-wrapper")
#     price_element = job_element_middle.find("div", class_="p-list-price")
#     for a in name_element.find_all('a', href=True):
#          link = a['href']
#     if price_element is not None:
#         print("Product_name: ", name_element.text.strip())
#         print("Link: ", link)
#         print("Price: ", price_element.text.strip())
#         print()

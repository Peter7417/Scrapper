import requests
from bs4 import BeautifulSoup
from googlesearch import search


user_search = input("Product search: ")
matrix = search(user_search + "Game uk")
URL = []
for result in matrix:
    URL.append(result)

page = requests.get(URL[0])

soup = BeautifulSoup(page.content, "html.parser")

# from googlesearch import search
#
# list = search("5800x3d BOX computer store uk",num_results=100)
# matrix = []
# for i in list:
#     print(i)

from duckduckgo_search import ddg

s = "ryzen 5800x3d box uk"
a = ddg(s,max_results=5)
word = "BOX.co.uk"
l =[]
for i in a:
    l.append(i)

v = a[1]
print(v)

x = l.get('title')
print(x)


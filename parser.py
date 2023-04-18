import requests
from bs4 import BeautifulSoup

url = 'https://inside.bard.edu/academic/courses/current/africana.html'
response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')
print(soup.prettify())

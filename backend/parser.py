import requests
from bs4 import BeautifulSoup
import re

url = 'https://inside.bard.edu/academic/courses/current/film.html'
# url = 'https://inside.bard.edu/academic/courses/spring2019/photography.html'
# url = 'https://inside.bard.edu/academic/courses/fall2013/mathematics.html'
# url = 'https://inside.bard.edu/academic/courses/spring2010/classic.html'
# url = 'https://inside.bard.edu/academic/courses/fall2001/economics.html'
# url = 'https://inside.bard.edu/academic/courses/fall96/paint.htm'
response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')

text = soup.get_text()

scrapes = {
	"crn": re.findall(r'\d{5}', text),
	"credits": re.findall(r'redits[\S\s]*?(\d)', text),
	"course": re.findall(r'[A-Z\/]{2,9}\s[0-9]{3,4}[ \S]*', text),
	"professor": re.findall(r'ofessor[\S\s]*?(\w.+)', text),
}

with open('scrape.txt', 'w') as f:
    f.write(text)


# print(scrapes)

print("crn\tcourse\tcredits\tprofessor")

for i in range(len(scrapes["crn"])):
	print("{0}\t{1}\t{2}\t{3}".format(
		scrapes["crn"][i],
		scrapes["course"][i],
		scrapes["credits"][i],
		scrapes["professor"][i],
	))
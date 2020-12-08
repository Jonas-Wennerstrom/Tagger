import numpy as np

import requests
from requests import get
from bs4 import BeautifulSoup

from time import sleep
from random import randint

from scraperdb import *
from scrapersql import *

from sqlalchemy import create_engine, func, asc
from sqlalchemy.orm import sessionmaker

length = []
title = []
link = []
tag = []

headers = {'Accept-Language': 'en-US, en;q=0.5'}

pages = np.arange(1, 1001, 50)

for page in pages:
    # Getting the contents from the each url
    page = requests.get('https://www.imdb.com/search/title/?groups=top_1000&start=' + str(page) + '&ref_=adv_nxt', headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    # Aiming the part of the html we want to get the information from
    movie_div = soup.find_all('div', class_='lister-item mode-advanced')
    
    # Controling the loop’s rate by pausing the execution of the loop for a specified amount of time
    # Waiting time between requests for a number between 2-10 seconds
    sleep(randint(2,10))
    
    for container in movie_div:
        # Scraping the movie's name
        name = container.h3.a.text
        title.append(name)
        
        # Scraping the movie's length
        runtime = container.find('span', class_='runtime').text if container.p.find('span', class_='runtime') else '-'
        length.append(runtime)
        
        #Scrapin categories
        genre = container.find('span', class_='genre').text
        tag.append(genre)
        
        url = container.h3.a['href']
        link.append('https://www.imdb.com'+url)
        
#Scraping done
db_name = "imdb1000.db"
make_new_db(db_name)
engine = create_engine("sqlite:///"+db_name)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

for i in range(len(title)):
    tagword = tag[i]
    tagword = tagword.strip()
    taglist = tagword.split(", ")
    insert_both(session, [length[i], title[i], link[i]], taglist)

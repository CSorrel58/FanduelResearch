import logging
import re
import os
from bs4 import BeautifulSoup
import requests
from datetime import date

def nba_url_creator(day,month,year,urls):
    # Do need to update this fr each season
    years = [2020, 2021]
    months = list(range(1, 13, 1))
    days = list(range(1, 32, 1))
    for year in years:
        for month in months:
            for day in days:
                urls.append(str('http://rotoguru1.com/cgi-bin/hyday.pl?game=fd&mon=' + str(month) + '&day=' + str(
                    day) + '&year=' + str(year)))
    #hardcoded for opening day - need to update each season
    opening_day = urls.index('http://rotoguru1.com/cgi-bin/hyday.pl?game=fd&mon=12&day=22&year=2020')
    current_day = urls.index(
        f'http://rotoguru1.com/cgi-bin/hyday.pl?game=fd&mon={str(month)}&day={str(day)}&year={str(year)}')
    urls = urls[opening_day:current_day]
    return urls

def nba_url_scraper(urls,output):
    for url in urls:
        webpage = requests.get(url)
        webpage_content = webpage.content
        soup = BeautifulSoup(webpage_content,'html.parser')
        table_rows = soup.find_all('td')
    #pulling just the player data, which starts on the 24th entry.
        for row in table_rows[24:]:
            output.append([row.get_text(),url])
    return output

def nba_player_split(data,rows_per_player,output):
    players = [data[x:x + rows_per_player] for x in range(0, len(data), rows_per_player)]
    for player in players:
        logging.info(player)
        player.insert(0, player[0].split('|')[1])
        output.append([player[0],
                            player[1].split('|')[0],
                            player[2].split('|')[0],
                            player[3].split('|')[0],
                            player[4].split('|')[0],
                            player[5].split('|')[0],
                            player[6].split('|')[0],
                            player[7].split('|')[0],
                            player[8].split('|')[0],
                            player[9].split('|')[0]])

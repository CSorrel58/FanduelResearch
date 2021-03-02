from bs4 import BeautifulSoup
import logging
import requests


def url_creator(time_entry, urls):
    #NFL does url by week number
    time_entry = time_entry
    weeks = int(time_entry[0])
    for week in range(1,weeks):
        urls.append(str('http://rotoguru1.com/cgi-bin/fyday.pl?week=' + str(week) + '&game=fd'))
    return urls

def url_scraper(urls, output):
    for url in urls:
        webpage = requests.get(url)
        webpage_content = webpage.content
        soup = BeautifulSoup(webpage_content, 'html.parser')
        table_rows = soup.find_all('td')
        # pulling just the player data, which starts on the 20th entry.
        # We also want to add some kind of date identifier so for now im doing the url since it has the week in it
        for row in table_rows[20:]:
            output.append([row.get_text(), url])
    return output

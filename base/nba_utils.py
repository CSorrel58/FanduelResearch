import logging
from bs4 import BeautifulSoup
import requests

def nba_url_creator(day,month,year,urls):
    # Do need to update this for each season's opening day/years
    day = day
    month= month
    year = year
    dates = []
    years = [2020, 2021]
    months = list(range(1, 13, 1))
    days = list(range(1, 32, 1))
    opening_day = {"day": 22,
                   'year': 2020,
                   'month': 12,
                   'url': f"http://rotoguru1.com/cgi-bin/hyday.pl?game=fd&mon=12&day=22&year=2020"
                   }
    current_day = {"day": day,
                   "month": month,
                   "year": year}
    for year in years:
        for month in months:
            for day in days:
                date = dict(day=day, month=month, year=year,
                            url=f"http://rotoguru1.com/cgi-bin/hyday.pl?game=fd&mon={str(month)}&day={str(day)}&year={str(year)}")
                dates.append(date)

    for entry in dates:
        if entry['year'] == opening_day['year']:
            if entry['month'] > current_day['month']:
                urls.append(entry['url'])
        elif entry['year'] == current_day['year']:
            if entry['month'] <= current_day['month']:
                urls.append(entry["url"])
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

def word_cleaner(frame,string):
    #only meant to be used with nba/nfl scraper that always has 'Data' column
    df = frame
    string = str(string)
    data_column = df['Data']
    # create series that has 0 for what matches the ads
    string_found = data_column.str.find(string)
    # add column to table with 0's
    df['Remove'] = string_found
    # create new table with those rows with zero gone
    output_frame = df[df['Remove'] != 1].reset_index(drop=True)
    return output_frame
import pandas as pd
from base import (
        google_drive_upload,
        add_position_nfl,
        clean_column,
        url_creator,
        url_scraper,
        nfl_player_split
    )

def run_nba(day,month,year):
#realized the url just updated based on dates, so wrote a loop to accumulate all of the urls
        years = [2020,2021]
        months = list(range(1,13,1))
        days = list(range(1,32,1))

        urls = []
        for year in years:
                for month in months:
                        for day in days:
                                urls.append(str('http://rotoguru1.com/cgi-bin/hyday.pl?game=fd&mon='+str(month)+'&day='+str(day)+'&year='+str(year)))
        opening_day = urls.index('http://rotoguru1.com/cgi-bin/hyday.pl?game=fd&mon=12&day=22&year=2020')
        current_day = urls.index(f'http://rotoguru1.com/cgi-bin/hyday.pl?game=fd&mon={str(month)}&day={str(day)}&year={str(year)}')
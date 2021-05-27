from bs4 import BeautifulSoup
import requests
import pandas as pd
import logging
import time


def nba_url_creator(day, month, year, urls):
    # Do need to update this for each season's opening day/years
    logging.info("Creating possible urls")
    day = day
    month = month
    year = year
    dates = []
    years = [2020, 2021]
    months = list(range(1, 13, 1))
    days = list(range(1, 32, 1))
    opening_day = {
        "day": 22,
        "year": 2020,
        "month": 12,
        "url": f"http://rotoguru1.com/cgi-bin/hyday.pl?game=fd&mon=12&day=22&year=2020",
    }
    current_day = {"day": day, "month": month, "year": year}
    for year in years:
        for month in months:
            for day in days:
                date = dict(
                    day=day,
                    month=month,
                    year=year,
                    url=f"http://rotoguru1.com/cgi-bin/hyday.pl?game=fd&mon={str(month)}&day={str(day)}&year={str(year)}",
                )
                dates.append(date)

    for entry in dates:
        if entry["year"] == opening_day["year"]:
            if entry["month"] > current_day["month"]:
                urls.append(entry["url"])
        elif entry["year"] == current_day["year"]:
            if entry["month"] <= current_day["month"]:
                urls.append(entry["url"])
    logging.info(f"Created {len(urls)} urls to scrape")
    return urls


def nba_table_grabber(urls):
    logging.info(
        "Grabbing tables using pandas.from_html - this will take a few minutes"
    )
    # Grabbing the first player table to create our dataframe - we will append to this
    first_page_tables = pd.read_html(urls[0])
    player_table = first_page_tables[-2]
    # adding the url as a column since it has the date - the table itself doesn't give you that
    player_table["URL"] = urls[0]
    for url in urls:
        page_tables = pd.read_html(url)
        page_table = page_tables[-2]
        page_table["URL"] = url
        # adding filter for if the table is clearly not player data
        if len(page_table) > 10:
            player_table = player_table.append(page_table)
            if len(player_table) > 30000 and len(player_table) < 30300:
                logging.info("Almost done")
            elif len(player_table) > 20000 and len(player_table) < 20200:
                logging.info("Working on it - over halfway")
            elif len(player_table) > 10000 and len(player_table) < 10200:
                logging.info("Making progress - over 10000 records!")
            elif len(player_table) > 500 and len(player_table) < 700:
                logging.info("Just getting started")
    logging.info(f"Grabbed all tables. Total rows: {len(player_table)}")
    return player_table


def nba_player_split(data, rows_per_player, output):
    players = [
        data[x : x + rows_per_player] for x in range(0, len(data), rows_per_player)
    ]
    for player in players:
        player.insert(0, player[0].split("|")[1])
        output.append(
            [
                player[0],
                player[1].split("|")[0],
                player[2].split("|")[0],
                player[3].split("|")[0],
                player[4].split("|")[0],
                player[5].split("|")[0],
                player[6].split("|")[0],
                player[7].split("|")[0],
                player[8].split("|")[0],
                player[9].split("|")[0],
            ]
        )


def word_cleaner(frame, string):
    # only meant to be used with nba/nfl scraper that always has 'Data' column
    df = frame
    string = str(string)
    data_column = df["Position"]
    # create series that has 0 for what matches the ads
    string_found = data_column.str.find(string)
    # add column to table with 0's
    df["Remove"] = string_found
    # create new table with those rows with zero gone
    output_frame = df[df["Remove"] < 0].reset_index(drop=True)
    return output_frame

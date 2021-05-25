from bs4 import BeautifulSoup
import requests


def nfl_url_creator(time_entry, urls):
    # NFL does url by week number
    time_entry = time_entry
    weeks = int(time_entry)
    for week in range(1, weeks):
        urls.append(
            str("http://rotoguru1.com/cgi-bin/fyday.pl?week=" + str(week) + "&game=fd")
        )
    return urls


def nfl_url_scraper(urls, output):
    for url in urls:
        webpage = requests.get(url)
        webpage_content = webpage.content
        soup = BeautifulSoup(webpage_content, "html.parser")
        table_rows = soup.find_all("td")
        # pulling just the player data, which starts on the 20th entry.
        # We also want to add some kind of date identifier so for now im doing the url
        for row in table_rows[20:]:
            output.append([row.get_text(), url])
    return output


def add_position_nfl(df):
    df = df
    Result = ["QB"]
    Positions = list(["QB", "RB", "WR", "TE", "Def"])
    # creating list of my positions
    # setting index as 0 to start with QB
    Role = 0
    # loop checking for week number and points scored
    for i in range(1, len(df)):
        # if week for new row matches week for last row, and points for new row <= last row, then same position as last row
        if (
            int(df.Week[i]) == int(df.Week[i - 1])
            and df.Fanduel_Points[i] <= df.Fanduel_Points[i - 1]
        ):
            Result.append(Positions[Role])
        # if week for new row matches week for last row, and points for new row > last row, then next position in list
        elif (
            int(df.Week[i]) == int(df.Week[i - 1])
            and df.Fanduel_Points[i] > df.Fanduel_Points[i - 1]
        ):
            Role += 1
            Result.append(Positions[Role])
        # if new week, reset and begin from Positions[0] to begin labeling as QB again
        elif int(df.Week[i]) > int(df.Week[i - 1]):
            Role = 0
            Result.append(Positions[Role])
    df["Position"] = Result
    return df


def nfl_player_split(data, rows_per_player, output):
    # take a list with all player data, and creates a row per player per game given a constant at which to start a new row
    data_list = data
    rows = rows_per_player
    players = [data_list[x : x + rows] for x in range(0, len(data_list), rows)]
    for player in players:
        # add week
        player.insert(0, player[0].split("|")[1])
        # add other data
        output.append(
            [
                player[0],
                player[1].split("|")[0],
                player[2].split("|")[0],
                player[3].split("|")[0],
                player[4].split("|")[0],
                player[5].split("|")[0],
            ]
        )
    return output

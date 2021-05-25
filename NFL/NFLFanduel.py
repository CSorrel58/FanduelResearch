import pandas as pd
from base import (
    google_drive_upload,
    add_position_nfl,
    clean_column,
    nfl_url_creator,
    nfl_url_scraper,
    nfl_player_split,
)
import logging
import time


def run_nfl(week):
    # saving time just to see what our efficiency level is
    start_time = time.time()
    # realized the url just updated based on week number, so wrote a loop to accumulate all of the urls up to the week number provided
    urls = []
    nfl_url_creator(week, urls)
    # creating an empty list that will have the player row for each table
    rows = []
    logging.info(f"Scraping {len(urls)} urls for player data")
    nfl_url_scraper(urls, rows)
    # create data frame
    sample_frame = pd.DataFrame.from_records(rows).reset_index()
    # rename columns
    sample_frame.columns = ["ID", "Data", "URL"]
    # clean up column with urls so it just has date
    sample_frame["Week"] = sample_frame["URL"].map(
        lambda x: x.replace("http://rotoguru1.com/cgi-bin/fyday.pl?week=", "").replace(
            "&game=fd", ""
        )
    )
    # create separate frame that removes all the url columns
    sample_frame = sample_frame[["Data", "Week"]].reset_index(drop=True)
    # There's a headers that aren't player data. we are getting rid of most those here.
    logging.info("Cleaning headers, other features from frame")
    sub = [
        "QB",
        "Points",
        "Team",
        "Salary",
        "Unlisted",
        "Running Backs",
        "Kickers",
        "Defenses",
        "Opp.",
        "Wide Receivers",
        "Tight Ends",
        "RotoGuru",
        "\n\n\n\n",
        "Score",
    ]
    pattern = "|".join(sub)
    sample_frame["gone"] = sample_frame["Data"].str.contains(pattern, case=True)
    clean_table = sample_frame[sample_frame["gone"] == False].reset_index(drop=True)
    just_data = clean_table[["Data", "Week"]].reset_index(drop=True)
    # merging data and date in a column so
    # I can then hopefully turn each one into a series and then just have the date once at the end.
    just_data["merge_date"] = just_data["Data"].astype(str) + "|" + just_data["Week"]
    # turning my merged column into a list to then add the date to the end of a player row
    data_list = list(just_data["merge_date"])
    # each row was 5 entries. This gets thrown off very easily though so we need to be careful
    player_rows = []
    logging.info("Creating player data table")
    nfl_player_split(data_list, 5, player_rows)
    sample_frame = pd.DataFrame.from_records(player_rows).reset_index(drop=True)
    sample_frame.columns = [
        "Week",
        "Name",
        "Team",
        "Opponent",
        "Fanduel_Points",
        "Fanduel_Price",
    ]
    # Replace currency symbols in column so we can make it an integer
    clean_column(sample_frame, "Fanduel_Price", ",")
    clean_column(sample_frame, "Fanduel_Price", "$")
    # Turn the column to integers
    sample_frame["Fanduel_Price"] = pd.to_numeric(
        sample_frame["Fanduel_Price"], errors="coerce"
    )
    # there is no price listed for some players. i am removing them if so
    sample_frame = sample_frame[~sample_frame["Fanduel_Price"].isna()].reset_index(
        drop=True
    )

    sample_frame["Fanduel_Points"] = pd.to_numeric(sample_frame["Fanduel_Points"])
    # create column for home vs away and updated column for opponent
    sample_frame["Game Location"] = (
        sample_frame["Opponent"]
        .str[0]
        .apply(lambda x: "Home" if str(x) == "v" else "Away")
    )
    sample_frame["Opponent"] = sample_frame["Opponent"].str[1:].replace(". ", "")
    # get rid of some carrots that are appearing
    clean_column(sample_frame, "Name", "^")
    # rename columns
    sample_frame.columns = [
        "Week",
        "Name",
        "Team",
        "Opponent",
        "Fanduel_Points",
        "Fanduel_Price",
        "Game Location",
    ]
    # add Value Column
    logging.info("Adding player fanduel value as Points/Price")
    sample_frame["Fanduel_Value"] = sample_frame["Fanduel_Points"] / (
        sample_frame["Fanduel_Price"] / 1000
    )
    # creating position column I will add my positions to, with a default of QB, then running method to match correct positions
    sample_frame["Position"] = "QB"
    add_position_nfl(sample_frame)
    # uploads the full frame to google sheets after saving locally as  a.csv
    logging.info("Uploading saved frame to google drive")
    google_drive_upload(sample_frame, "NFL")
    logging.info(f"Time to run = {round(time.time() - start_time, 2)} seconds")

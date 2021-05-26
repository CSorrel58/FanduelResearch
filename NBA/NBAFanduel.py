import pandas as pd
from base import (
    google_drive_upload,
    clean_column,
    nba_url_creator,
    nba_table_grabber,
    nba_player_split,
    word_cleaner,
)
import time
import logging


def run_nba(day, month, year):
    start_time = time.time()
    day = day
    month = month
    year = year

    urls = []
    nba_url_creator(day, month, year, urls)

    sample_frame = nba_table_grabber(urls)

    dates = sample_frame["URL"].map(
        lambda x: x.replace("http://rotoguru1.com/cgi-bin/hyday.pl?game=fd&mon=", "")
        .replace("&year=", "/")
        .replace("&day=", "/")
    )
    sample_frame["Date"] = dates

    sample_frame.columns = [
        "Position",
        "Name",
        "Fanduel_Points",
        "Fanduel_Price",
        "Team",
        "Opponent",
        "Score",
        "Minutes",
        "Stats",
        "URL",
        "Date",
    ]
    logging.info(sample_frame.columns)
    # Clearing header rows
    jump_gone = word_cleaner(frame=sample_frame, string="Jump to:")
    guard_gone = word_cleaner(frame=jump_gone, string="Guards")
    forward_gone = word_cleaner(frame=guard_gone, string="Forwards")
    centers_gone = word_cleaner(frame=forward_gone, string="Centers")
    unlisted_gone = word_cleaner(frame=centers_gone, string="Unlisted")
    unlisted_gone.to_csv("sample.csv")
    sample_frame = unlisted_gone
    clean_column(sample_frame, "Fanduel_Price", ",")
    clean_column(sample_frame, "Fanduel_Price", "$")
    sample_frame["Fanduel_Price"] = pd.to_numeric(
        sample_frame["Fanduel_Price"], errors="coerce"
    )

    df1 = sample_frame[~sample_frame["Fanduel_Price"].isna()].reset_index(drop=True)
    # convert DNP in Minutes column to 0's. Had to make 0:0 to allow split function to work for players with actual minutes
    df1["NoDNP"] = df1["Minutes"].apply(lambda x: "0:0" if str(x) == "DNP" else x)
    # convert nan in Minutes column to 0's
    df1["NoNaN"] = df1["NoDNP"].apply(lambda x: "0:0" if str(x) == "nan" else x)
    # convert nan in Minutes column to 0's
    df1["NoNa"] = df1["NoNaN"].apply(lambda x: "0:0" if str(x) == "NA" else x)
    # convert mm:ss to total minutes as a float by splitting and then adding
    # df1['Minutes_Played'] = df1['NoNa'].str.split(':').apply(lambda x: int(x[0]) + ((int(x[1]) / 60)))
    # Convert Fanduel_Points to float
    df1["Fanduel_Points"] = pd.to_numeric(df1["Fanduel_Points"])
    # create column for home vs away and updated column for opponent
    df1["Split"] = df1["Opponent"].str[0]
    df1["Home"] = df1.Split.apply(lambda x: "Home" if str(x) == "v" else "Away")
    df1["Foe"] = df1["Opponent"].str[1:]
    # clearing out some columns
    del df1["NoDNP"]
    del df1["NoNaN"]
    del df1["Split"]
    del df1["NoNa"]
    del df1["Opponent"]
    clean_column(df1, "Name", "^")
    # doing some work to parse the stats column so it's individual statistics and not the list
    stats = df1["Stats"].reset_index()
    stats_split = stats["Stats"].str.split(" ", expand=True).reset_index(drop=True)
    stats_split.fillna("0")
    # filtering just for values that contain points
    stats_split["Points"] = stats_split[2].apply(lambda x: x if x.find("pt") else 0)
    # removing signifier
    stats_split["Points"] = stats_split["Points"].str.replace("pt", "")
    # converting points to numeric
    stats_split["Points"] = pd.to_numeric(stats_split["Points"])
    # As soon as I hit rebounds, I ran into a none type error. I am trying this way instead.
    stats_split["Rebounds"] = (
        stats_split[3]
        .str.extract(pat="(.?.rb)")
        .fillna(stats_split[2].str.extract(pat="(.?.rb)"))
    )
    # removing signifier
    stats_split["Rebounds"] = stats_split["Rebounds"].str.replace("rb", "")
    # converting to numeric
    stats_split["Rebounds"] = pd.to_numeric(stats_split["Rebounds"])
    # trying now for assists
    stats_split["Assists"] = (
        stats_split[4]
        .str.extract(pat="(.?.as)")
        .fillna(stats_split[3].str.extract(pat="(.?.as)"))
        .fillna(stats_split[2].str.extract(pat="(.?.as)"))
    )
    # removing signifier
    stats_split["Assists"] = stats_split["Assists"].str.replace("as", "")
    # converting to numeric
    stats_split["Assists"] = pd.to_numeric(stats_split["Assists"])
    # trying now for steals
    stats_split["Steals"] = (
        stats_split[5]
        .str.extract(pat="(.?.st)")
        .fillna(stats_split[4].str.extract(pat="(.?.st)"))
        .fillna(stats_split[3].str.extract(pat="(.?.st)"))
        .fillna(stats_split[2].str.extract(pat="(.?.st)"))
    )
    # removing signifier
    stats_split["Steals"] = stats_split["Steals"].str.replace("st", "")
    # converting to numeric
    stats_split["Steals"] = pd.to_numeric(stats_split["Steals"])
    # trying now for Blocks
    stats_split["Blocks"] = (
        stats_split[6]
        .str.extract(pat="(.?.bl)")
        .fillna(stats_split[5].str.extract(pat="(.?.bl)"))
        .fillna(stats_split[4].str.extract(pat="(.?.bl)"))
        .fillna(stats_split[3].str.extract(pat="(.?.bl)"))
        .fillna(stats_split[2].str.extract(pat="(.?.bl)"))
    )
    # removing signifier
    stats_split["Blocks"] = stats_split["Blocks"].str.replace("bl", "")
    # converting to numeric
    stats_split["Blocks"] = pd.to_numeric(stats_split["Blocks"])
    # trying now for Turnovers
    stats_split["Turnovers"] = (
        stats_split[7]
        .str.extract(pat="(.?.to)")
        .fillna(stats_split[6].str.extract(pat="(.?.to)"))
        .fillna(stats_split[5].str.extract(pat="(.?.to)"))
        .fillna(stats_split[4].str.extract(pat="(.?.to)"))
        .fillna(stats_split[3].str.extract(pat="(.?.to)"))
        .fillna(stats_split[2].str.extract(pat="(.?.to)"))
    )
    # removing signifier
    stats_split["Turnovers"] = stats_split["Turnovers"].str.replace("to", "")
    # converting to numeric
    stats_split["Turnovers"] = pd.to_numeric(stats_split["Turnovers"])
    # trying now for Three Pointers
    stats_split["3pts"] = (
        stats_split[8]
        .str.extract(pat="(.?.trey)")
        .fillna(stats_split[7].str.extract(pat="(.?.trey)"))
        .fillna(stats_split[6].str.extract(pat="(.?.trey)"))
        .fillna(stats_split[5].str.extract(pat="(.?.trey)"))
        .fillna(stats_split[4].str.extract(pat="(.?.trey)"))
        .fillna(stats_split[3].str.extract(pat="(.?.trey)"))
        .fillna(stats_split[2].str.extract(pat="(.?.to)"))
    )
    # removing signifier
    stats_split["3pts"] = stats_split["3pts"].str.replace("trey", "")
    # converting to numeric
    stats_split["3pts"] = pd.to_numeric(stats_split["3pts"])
    # trying now for Field Goal
    stats_split["Field_Goals"] = (
        stats_split[9]
        .str.extract(pat="(.?.?.?.fg)")
        .fillna(stats_split[8].str.extract(pat="(.?.?.?.fg)"))
        .fillna(stats_split[7].str.extract(pat="(.?.?.?.fg)"))
        .fillna(stats_split[6].str.extract(pat="(.?.?.?.fg)"))
        .fillna(stats_split[5].str.extract(pat="(.?.?.?.fg)"))
        .fillna(stats_split[4].str.extract(pat="(.?.?.?.fg)"))
        .fillna(stats_split[3].str.extract(pat="(.?.?.?.fg)"))
        .fillna(stats_split[2].str.extract(pat="(.?.?.?.fg)"))
    )
    # removing signifier
    stats_split["Field_Goals"] = stats_split["Field_Goals"].str.replace("fg", "")
    # trying now for Free throws
    stats_split["Free_Throws"] = (
        stats_split[10]
        .str.extract(pat="(.?.?.?.ft)")
        .fillna(stats_split[9].str.extract(pat="(.?.?.?.ft)"))
        .fillna(stats_split[8].str.extract(pat="(.?.?.?.ft)"))
        .fillna(stats_split[7].str.extract(pat="(.?.?.?.ft)"))
        .fillna(stats_split[6].str.extract(pat="(.?.?.?.ft)"))
        .fillna(stats_split[5].str.extract(pat="(.?.?.?.ft)"))
        .fillna(stats_split[4].str.extract(pat="(.?.?.?.ft)"))
        .fillna(stats_split[3].str.extract(pat="(.?.?.?.ft)"))
        .fillna(stats_split[2].str.extract(pat="(.?.?.?.ft)"))
    )
    # removing signifier
    stats_split["Free_Throws"] = stats_split["Free_Throws"].str.replace("ft", "")
    # now splitting free throws and field goals into their own specific stats
    # creating frame of just field goals made and attempted
    field_goals_made = stats_split["Field_Goals"].str.split("-", expand=True).fillna(0)
    # naming those columns
    field_goals_made.columns = ["Field_Goals_Made", "Field_Goals_Attempted"]
    # adding back to stat_split
    stats_split["Field_Goals_Made"] = pd.to_numeric(
        field_goals_made["Field_Goals_Made"]
    )
    stats_split["Field_Goals_Attempted"] = pd.to_numeric(
        field_goals_made["Field_Goals_Attempted"]
    )
    # adding free throw percentage
    stats_split["Shooting%"] = (
        stats_split["Field_Goals_Made"] / stats_split["Field_Goals_Attempted"]
    )
    # repeating for free throws
    # creating frame of just free throws made and attempted
    frees_made = stats_split["Free_Throws"].str.split("-", expand=True).fillna(0)
    # naming those columns
    frees_made.columns = ["Frees_Made", "Frees_Attempted"]
    # adding back to stat_split
    stats_split["Free_Throws_Made"] = pd.to_numeric(frees_made["Frees_Made"])
    stats_split["Free_Throws_Attempted"] = pd.to_numeric(frees_made["Frees_Attempted"])
    # adding free throw percentage
    stats_split["Free_Throw%"] = (
        stats_split["Free_Throws_Made"] / stats_split["Free_Throws_Attempted"]
    )

    df1[
        [
            "Points",
            "Rebounds",
            "Assists",
            "Steals",
            "Blocks",
            "Turnovers",
            "3pts",
            "Field_Goals",
            "Free_Throws",
            "Field_Goals_Made",
            "Field_Goals_Attempted",
            "Shooting%",
            "Free_Throws_Made",
            "Free_Throws_Attempted",
            "Free_Throw%",
        ]
    ] = stats_split[
        [
            "Points",
            "Rebounds",
            "Assists",
            "Steals",
            "Blocks",
            "Turnovers",
            "3pts",
            "Field_Goals",
            "Free_Throws",
            "Field_Goals_Made",
            "Field_Goals_Attempted",
            "Shooting%",
            "Free_Throws_Made",
            "Free_Throws_Attempted",
            "Free_Throw%",
        ]
    ]

    df2 = df1[
        [
            "Date,",
            "Position",
            "Name",
            "Fanduel_Points",
            "Fanduel_Price",
            "Team",
            "Score",
            "Minutes_Played",
            "Home",
            "Foe",
            "Points",
            "Rebounds",
            "Assists",
            "Steals",
            "Blocks",
            "Turnovers",
            "3pts",
            "Field_Goals_Made",
            "Field_Goals_Attempted",
            "Shooting%",
            "Free_Throws_Made",
            "Free_Throws_Attempted",
            "Free_Throw%",
        ]
    ]
    google_drive_upload(df2, "NBA")

    logging.info(f"Time to run: {time.time()-start_time}")

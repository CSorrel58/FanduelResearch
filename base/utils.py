import pandas as pd
import logging
import re
import os
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

gdrive = os.path.join("/Users/a09304858/Documents/GitHub/FanduelResearch/base/gdrive_key.json")

def clean_column(df, column_name:str, character:str):
    character = character
    frame = df
    column = column_name
    frame[column] = frame[column].str.replace(character,"")
    return frame

def add_position_nfl(df):
    df = df
    Result = ['QB']
    Positions = list(['QB', 'RB', 'WR', 'TE', 'Def'])
    #creating list of my positions
    #setting index as 0 to start with QB
    Role = 0
    #loop checking for week number and points scored
    for i in range(1,len(df)):
        #if week for new row matches week for last row, and points for new row <= last row, then same position as last row
        if int(df.Week[i])== int(df.Week[i-1]) and df.Fanduel_Points[i]<= df.Fanduel_Points[i-1]:
            Result.append(Positions[Role])
        #if week for new row matches week for last row, and points for new row > last row, then next position in list
        elif int(df.Week[i]) == int(df.Week[i-1]) and df.Fanduel_Points[i] > df.Fanduel_Points[i-1]:
            Role +=1
            Result.append(Positions[Role])
        #if new week, reset and begin from Positions[0] to begin labeling as QB again
        elif int(df.Week[i]) > int(df.Week[i-1]) :
            Role = 0
            Result.append(Positions[Role])
    df['Position'] = Result
    return df

def player_split(data,rows_per_player,output):
    #take a list with all player data, and creates a row per player per game given a constant at which to start a new row
    data_list = data
    rows = rows_per_player
    players = [data_list[x:x + rows] for x in range(0, len(data_list), rows)]
    for player in players:
        player.insert(0, player[0].split('|')[1])
        output.append([player[0],
                        player[1].split('|')[0],
                        player[2].split('|')[0],
                        player[3].split('|')[0],
                        player[4].split('|')[0],
                        player[5].split('|')[0],
                        ])
    logging.info(f"{output}")
    return output

def google_drive_upload(df, sport: str, ):
    df = df
    sport = sport
    savetime = date.today()
    df.to_csv(f'{sport}.{savetime}.csv')
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    # establishing credentials given to me by Google API
    credentials = ServiceAccountCredentials.from_json_keyfile_name(gdrive, scope)
    client = gspread.authorize(credentials)
    # opening the sheet I am keeping the scores on
    spreadsheet = client.open('nfl_weekly_fanduel_scores')
    # Updating sheet with my new csv
    with open(f'{sport}.{savetime}.csv', 'r') as file_obj:
        content = file_obj.read()
        client.import_csv(spreadsheet.id, data=content)
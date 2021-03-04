import os
import logging
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

def google_drive_upload(df, sport: str, ):
    df = df
    sport = str(sport)
    savetime = date.today()
    df.to_csv(f'{sport}.{savetime}.csv')
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    # establishing credentials given to me by Google API
    credentials = ServiceAccountCredentials.from_json_keyfile_name(gdrive, scope)
    client = gspread.authorize(credentials)
    # opening the sheet I am keeping the scores on
    if sport =="NFL":
        spreadsheet = client.open('nfl_weekly_fanduel_scores')
    elif sport == "NBA":
        spreadsheet = client.open('Player_Game_Records_2021')
    # Updating sheet with my new csv
    with open(f'{sport}.{savetime}.csv', 'r') as file_obj:
        content = file_obj.read()
        client.import_csv(spreadsheet.id, data=content)
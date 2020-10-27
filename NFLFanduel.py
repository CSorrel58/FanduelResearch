'''
Created on Oct 26, 2020

@author: clint
'''
#pulling in all the necessary python libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
##realized the url just updated based on week number, so wrote a loop to accumulate all of the urls
weeks = list(range(1,17,1))
##every week added we just need to update this range

urls = []
for week in weeks:
    urls.append(str('http://rotoguru1.com/cgi-bin/fyday.pl?week='+str(week)+'&game=fd'))

##we should now have the page we need for each week
##creating an empty list that will have the player row for each table

rows = []

##Running a loop through all the urls to get every piece of data in one list
##scraping each url
for url in urls:
    webpage = requests.get(url)
    webpage_content = webpage.content
    soup = BeautifulSoup(webpage_content,'html.parser')
    table_rows = soup.find_all('td')
    #pulling just the player data, which starts on the 20th entry. 
    #We also want to add some kind of date identifier so for now im doing the url since it has the week in it
    for row in table_rows[20:]:
        rows.append([row.get_text(),url])
##create data frame
sample_frame = pd.DataFrame.from_records(rows).reset_index()
##save to csv
sample_frame.to_csv('All_nfl_rows.csv')
#create frame from saved csv
new_frame = pd.read_csv('All_nfl_rows.csv')
#rename columns
new_frame.columns = ['Row','ID','Data','URL']
#clean up column with urls so it just has date
dates = new_frame['URL'].map(lambda x: x.replace('http://rotoguru1.com/cgi-bin/fyday.pl?week=','')\
                             .replace('&game=fd',''))
new_frame['Week'] = dates

#create separate frame that removes all the url columns
date_frame = new_frame[['Data','Week']].reset_index(drop=True)
#We need to remove some ads and nav stuff here by 
#converting to a series, finding the ones that match, and adding back to the table
find_Ads = date_frame['Data']
#create series that has 0 for what matches the ads
ads_found = find_Ads.str.find('RotoGuru')
#add column to table with 0's
date_frame['Ad'] = ads_found
#create new table with those rows with zero gone
no_ads = date_frame[date_frame['Ad'] != 1].reset_index(drop=True)
#Repeating to remove Jump To:
#converting to a series, finding the ones that match, and adding back to the table
find_jump = no_ads['Data']
#create series that has 0 for what matches the text
jump_found = find_jump.str.find('Jump to:')
#add column to table with 0's
no_ads['Remove'] = jump_found
#create new table with those rows with zero gone
jump_gone = no_ads[no_ads['Remove'] !=0].reset_index(drop=True)
#There's a term 'Unlisted' that pops up occasionally and breaks everything in the NBA version of this page.
#I'm clearing that here to be safe
find_unlisted = jump_gone['Data']
#create series that has a 0 for where it says unlisted
unlisted_found = find_unlisted.str.find('Unlisted')
#add column to table with 0's
jump_gone['Z'] = unlisted_found
#create new table with those rows removed
unlisted_gone = jump_gone[jump_gone['Z'] != 0].reset_index(drop=True)
#repeating for Opp 
find_opp = unlisted_gone['Data']
#create series that has a 0 for where it says unlisted
opp_found = find_opp.str.find('Opp.')
#add column to table with 0's
unlisted_gone['F'] = opp_found
#create new table with those rows removed
opp_gone = unlisted_gone[unlisted_gone['F'] != 0].reset_index(drop=True)
#Repeating for Wide Recievers
find_wide = opp_gone['Data']
#create series that has a 0 for where it says unlisted
wide_found = find_wide.str.find('Wide Receivers')
#add column to table with 0's
opp_gone['X'] = wide_found
#create new table with those rows removed
wide_gone = opp_gone[opp_gone['X'] != 0].reset_index(drop=True)
#Repeating for \n
find_n = wide_gone['Data']
##create series that has a 0 for where it says unlisted
n_found = find_n.str.find('\n\n\n\n')
##add column to table with 0's
wide_gone['W'] = n_found
##create new table with those rows removed
n_gone = wide_gone[wide_gone['W'] != 0].reset_index(drop=True)
##Repeating for Score
find_score = n_gone['Data']
##create series that has a 0 for where it says unlisted
score_found = find_n.str.find('Score')
##add column to table with 0's
n_gone['R'] = score_found
##create new table with those rows removed
score_gone = n_gone[n_gone['R'] != 0].reset_index(drop=True)
##Repeating for Tight Ends
find_tight = score_gone['Data']
##create series that has a 0 for where it says unlisted
tight_found = find_tight.str.find('Tight Ends')
##add column to table with 0's
score_gone['S'] = tight_found
##create new table with those rows removed
tight_gone = score_gone[score_gone['S'] != 0].reset_index(drop=True)
##There's a subtable headers that aren't player data. we are getting rid of most those here.
##creates list of all the words I want to find and get rid of
sub = ['QB','Points','Team','Salary','Unlisted','Running Backs',\
       'Kickers','Defenses']
pattern = '|'.join(sub)

tight_gone['gone'] = tight_gone['Data'].str.contains(pattern, case=True)
#remove any rows where we found those subtable headers
clean_table = tight_gone[tight_gone['gone'] != True].reset_index(drop=True)
##create series with the data
just_data = clean_table[['Data','Week']].reset_index(drop=True)
#merging data and date in a column so
#I can then hopefully turn each one into a series and then just have the date once at the end.
just_data['merge_date'] = just_data['Data'].astype(str)+'|'+just_data['Week']
#turning my merged column into a list so I can run a comprehension and then add the date to the end of a player row
just_datas = just_data['merge_date']
#turning series into a list so we can do some stuff
data_list = list(just_datas)
#I used this loop to create sublists per player based on each player entry having 5 columns
##each row was 5 entries. This gets thrown off very easily though so we need to be careful to remove all other data
##which we have already done above
players = [data_list[x:x+5] for x in range(0, len(data_list), 5)]
#now we have a row per player, but every piece of data has the date. 
#So first I'm pulling the date out and adding it to the end of every sublist
for player in players:
    player.insert(0,player[0].split('|')[1])
#creating list that has each player entry as its own record without date. 
#Note - we already pulled the date and added it to the end of the sublist.
#If you haven't done that I recommend you do so first
player_rows =[]
for player in players:
    if len(player) == 6:
        player_rows.append([player[0],\
                            player[1].split('|')[0],\
                            player[2].split('|')[0],\
                            player[3].split('|')[0],\
                            player[4].split('|')[0],\
                            player[5].split('|')[0],\
                            ])
sample_frame = pd.DataFrame.from_records(player_rows).reset_index(drop=True)
sample_frame.columns = ['Week','Name','Team','Opponent','Fanduel_Points','Fanduel_Price']
#Replace currency symbols in column so we can make it an integer
sample_frame['Fanduel_Price'] = sample_frame['Fanduel_Price'].str.replace(',', '')
sample_frame['Fanduel_Price'] = sample_frame['Fanduel_Price'].str.replace('$', '')
#Turn the column to integers
sample_frame['Fanduel_Price'] = pd.to_numeric(sample_frame['Fanduel_Price'], errors='coerce')
#there is no price listed for some players. i am removing them since the whole goal is to see who exceeds their price
df1 = sample_frame[~sample_frame['Fanduel_Price'].isna()].reset_index(drop=True)
#Convert Fanduel_Points to float
df1['Fanduel_Points'] = pd.to_numeric(df1['Fanduel_Points'])
#create column for home vs away and updated column for opponent
df1['Split'] = df1['Opponent'].str[0]
df1['Home'] = df1.Split.apply(lambda x: 'Home' if str(x) == 'v' else 'Away')
df1['Foe'] = df1['Opponent'].str[1:]
#get rid of periods in home v away
df1['Opponent'] = df1['Foe'].str.replace('. ','')
#get rid of some carrots that are appearing
df1['Name'] = df1['Name'].str.replace('^','')
#removing Split column
del df1['Split']
del df1['Foe']
#going ahead and saving this for a safe template
df1.to_csv('nfl_weekly_fanduel_scores.csv')
#create frame from saved csv
nfl_frame = pd.read_csv('nfl_weekly_fanduel_scores.csv')
#rename columns
nfl_frame.columns = ['Row','Week','Name','Team','Opponent','Fanduel_Points','Fanduel_Price','Game Location']
#removing extra index column
del nfl_frame['Row']
#add Value Column
nfl_frame['Fanduel_Value'] = nfl_frame['Fanduel_Points']/(nfl_frame['Fanduel_Price']/1000)
#creating position column I will add my positions to, with a default of QB
nfl_frame['Position'] = 'QB'
##writing comprehension to perform task of adding player position
#creating empty list that I will add each position to
Result = ['QB']
#list of positions
Positions = list(['QB','RB','WR','TE','Def'])
def add_position(df):
    #creating list of my positions
    #setting index as 0 to start with QB
    Role = 0
    #loop checking for week number and points scored
    for i in range(1,len(df)):
        #if week for new row matches week for last row, and points for new row <= last row, then same position as last row
        if df.Week[i]== df.Week[i-1] and df.Fanduel_Points[i]<= df.Fanduel_Points[i-1]:
            Result.append(Positions[Role])
        #if week for new row matches week for last row, and points for new row > last row, then next position in list
        elif df.Week[i] == df.Week[i-1] and df.Fanduel_Points[i] > df.Fanduel_Points[i-1]:
            Role +=1
            Result.append(Positions[Role])
        #if new week, reset and begin from Positions[0] to begin labeling as QB again
        elif df.Week[i] > df.Week[i-1] :
            Role = 0
            Result.append(Positions[Role])
#running my comprehension on the frame
add_position(nfl_frame)
#apply add_position to my position column
nfl_frame['Position'] = Result
#saving frame as csv
nfl_frame.to_csv('nfl_tableau_script.csv')
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
#establishing credentials given to me by Google API
credentials = ServiceAccountCredentials.from_json_keyfile_name('NFL Sheets JSON.json', scope)
client = gspread.authorize(credentials)
#opening the sheet I am keeping the scores on
spreadsheet = client.open('nfl_weekly_fanduel_scores')
#Updating sheet with my new csv
with open('nfl_tableau_script.csv', 'r') as file_obj:
    content = file_obj.read()
    client.import_csv(spreadsheet.id, data=content)
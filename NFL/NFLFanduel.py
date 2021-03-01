def run_nfl():
    from bs4 import BeautifulSoup
    import requests
    import pandas as pd
    import gspread
    import logging
    from oauth2client.service_account import ServiceAccountCredentials

    from base import (
        gdrive,
        add_position_nfl,
        clean_column,
    )
    # realized the url just updated based on week number, so wrote a loop to accumulate all of the urls
    # every week added we just need to update this range
    urls = []
    for week in range(1, 17, 1):
        urls.append(str('http://rotoguru1.com/cgi-bin/fyday.pl?week=' + str(week) + '&game=fd'))
    # we should now have the url we need for each week
    # creating an empty list that will have the player row for each table
    rows = []
    # Running a loop through all the urls to get every piece of data in one list
    # scraping each url
    for url in urls:
        webpage = requests.get(url)
        webpage_content = webpage.content
        soup = BeautifulSoup(webpage_content, 'html.parser')
        table_rows = soup.find_all('td')
        # pulling just the player data, which starts on the 20th entry.
        # We also want to add some kind of date identifier so for now im doing the url since it has the week in it
        for row in table_rows[20:]:
            rows.append([row.get_text(), url])
    # create data frame
    sample_frame = pd.DataFrame.from_records(rows).reset_index()
    # rename columns
    sample_frame.columns = ['ID', 'Data', 'URL']
    # clean up column with urls so it just has date
    sample_frame['Week'] = sample_frame['URL'].map(
        lambda x: x.replace('http://rotoguru1.com/cgi-bin/fyday.pl?week=', '') \
            .replace('&game=fd', ''))
    # create separate frame that removes all the url columns
    data_frame = sample_frame[['Data', 'Week']].reset_index(drop=True)
    # There's a subtable headers that aren't player data. we are getting rid of most those here.
    # creates list of all the words I want to find and get rid of
    sub = ['QB', 'Points', 'Team', 'Salary', 'Unlisted', 'Running Backs', 'Kickers', 'Defenses','Opp.','Wide Receivers', "Tight Ends","RotoGuru","\n\n\n\n","Score"]
    pattern = '|'.join(sub)

    data_frame['gone'] = data_frame['Data'].str.contains(pattern, case=True)
    # remove any rows where we found those subtable headers
    clean_table = data_frame[data_frame['gone'] == False].reset_index(drop=True)
    just_data = clean_table[['Data', 'Week']].reset_index(drop=True)
    # merging data and date in a column so
    # I can then hopefully turn each one into a series and then just have the date once at the end.
    just_data['merge_date'] = just_data['Data'].astype(str) + '|' + just_data['Week']
    # turning my merged column into a list so I can run a comprehension and then add the date to the end of a player row
    just_datas = just_data['merge_date']
    # turning series into a list so we can do some stuff
    data_list = list(just_datas)
    # I used this loop to create sublists per player based on each player entry having 5 columns
    # each row was 5 entries. This gets thrown off very easily though so we need to be careful to remove all other data
    # which we have already done above
    players = [data_list[x:x + 5] for x in range(0, len(data_list), 5)]
    # now we have a row per player, but every piece of data has the date.
    # So first I'm pulling the date out and adding it to the end of every sublist
    for player in players:
        player.insert(0, player[0].split('|')[1])
    # creating list that has each player entry as its own record without date.
    # Note - we already pulled the date and added it to the end of the sublist.
    # If you haven't done that I recommend you do so first
    player_rows = []
    for player in players:
        if len(player) == 6:
            player_rows.append([player[0],
                                player[1].split('|')[0],
                                player[2].split('|')[0],
                                player[3].split('|')[0],
                                player[4].split('|')[0],
                                player[5].split('|')[0],
                                ])
    sample_frame = pd.DataFrame.from_records(player_rows).reset_index(drop=True)
    sample_frame.columns = ['Week', 'Name', 'Team', 'Opponent', 'Fanduel_Points', 'Fanduel_Price']
    # Replace currency symbols in column so we can make it an integer
    clean_column(sample_frame, 'Fanduel_Price', ",")
    clean_column(sample_frame, 'Fanduel_Price', "$")
    # Turn the column to integers
    sample_frame['Fanduel_Price'] = pd.to_numeric(sample_frame['Fanduel_Price'], errors='coerce')
    # there is no price listed for some players. i am removing them since the whole goal is to see who exceeds their price
    sample_frame = sample_frame[~sample_frame['Fanduel_Price'].isna()].reset_index(drop=True)
    # Convert Fanduel_Points to float
    sample_frame['Fanduel_Points'] = pd.to_numeric(sample_frame['Fanduel_Points'])
    # create column for home vs away and updated column for opponent
    sample_frame['Split'] = sample_frame['Opponent'].str[0].apply(lambda x: 'Home' if str(x) == 'v' else 'Away')
    sample_frame['Opponent'] = sample_frame['Opponent'].str[1:].replace(". ", "")
    # get rid of some carrots that are appearing
    clean_column(sample_frame, 'Name', "^")
    # rename columns
    sample_frame.columns = ['Week', 'Name', 'Team', 'Opponent', 'Fanduel_Points', 'Fanduel_Price', 'Game Location']
    # add Value Column
    sample_frame['Fanduel_Value'] = sample_frame['Fanduel_Points'] / (sample_frame['Fanduel_Price'] / 1000)
    # creating position column I will add my positions to, with a default of QB, then running method to match correct positions
    sample_frame['Position'] = 'QB'
    add_position_nfl(sample_frame)
    # saving frame as csv
    sample_frame.to_csv('nfl_tableau_script.csv')
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    # establishing credentials given to me by Google API
    credentials = ServiceAccountCredentials.from_json_keyfile_name(gdrive, scope)
    client = gspread.authorize(credentials)
    # opening the sheet I am keeping the scores on
    spreadsheet = client.open('nfl_weekly_fanduel_scores')
    # Updating sheet with my new csv
    with open('nfl_tableau_script.csv', 'r') as file_obj:
        content = file_obj.read()
        client.import_csv(spreadsheet.id, data=content)

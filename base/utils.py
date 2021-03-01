import pandas as pd

def add_position(df):
    Result = ['QB']
    Positions = list(['QB', 'RB', 'WR', 'TE', 'Def'])
    #creating list of my positions
    #setting index as 0 to start with QB
    Role = 0
    #loop checking for week number and points scored
    for i in df:
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
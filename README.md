# FanduelResearch
My personal research project on player Fanduel scores relative to their price. Each Zip contains work for a different Sports League, with the league name in the file name. I have gone ahead and pulled the notebooks out for ease of review, but they are the same as what is in the zip file.

The CSV file in each zip the information for each player's performance and their price for every game they played through the season. This information was originally pulled from http://rotoguru1.com but I converted it to a .csv for ease of use and to avoid constantly requesting the information.

The Jupyter notebooks contain:
-"Import_and_Clean_Fanduel":my efforts to clean the data and merge all of the games into one dataframe I could then use to look at player value.
-"Manipulating Cleaned Fanduel": My efforts to use the cleaned frame to measure player value
-"{NFL/NBA} Expected Price": My efforts to build a regression model using value to predict player price, points, and value in their next game (for NBA, this was all past-tense)

Current project is reowrking this to allow it to be run with CLI commands, so it eventually can be automated to run in airflow using kubernetes.

I also created some visualizations using these frames in Tableau Public and have published them here: https://public.tableau.com/profile/clinton.sorrel#!/?newProfile=&activeTab=0

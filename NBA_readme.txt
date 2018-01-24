Relevant NBA data Scripts

Reminders:
 - Try to run updates early in morning or late at night to make sure they don't include partial games

File List

1. Location Table Build.ipynb
 - Builds the dataset with NBA team cities geocoded to allow for a distance traveled calculation
 - 2 tables created:
     a. Team_Location
     b. Travel_Distance

2. NBA_df DB Update.ipynb
 - updateNBADB function is defined in this file
 - This updates all of the base tables required 
 
3. NBA_TEAM_FEATURES.ipynb
 - Builds the central team feature dataset
 - merges, team_Data, line_data, and travel_distance data to make the output 
 - merge_team_line_Data, and team_feature_generation functions are used 
 - functions are pulled from NBA_df_scripts.py 
 - creates the "team_feature_data" table in NBA DB
 
4. NBA_df_scripts.py 
 - Defines all base data acquisition functions: getNBAplayerdata(), getNBAteamdata(), and getsportsbookdata()
 - Defines base team feature creation functions: merge_team_line_data(), and team_feature_generation()

5. NBA_DB.py
 - file used to create the initial tables.

6. NBA_TEAM_DATA_VALIDATION.ipynb
 - File used to QA & Test output tables
 
 
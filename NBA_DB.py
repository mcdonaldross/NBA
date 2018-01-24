
from NBA_df_scripts import getNBAteamdata, getsportsbookdata, getNBAplayerdata
import datetime as dt
import sqlite3 as lite

#establish connection to SQLite DB. I should place this on a shared drive
con = lite.connect(r'C:\Users\ross\Python Projects\NBA Daily Fantasy Data\nba_df.db')

for yr in range(2001,2016):
    startdate = dt.date(yr,10,10)
    team_data = getNBAteamdata(yr,startdate)
    team_data.to_sql('team_box_scores',con = con,schema ='dbo',if_exists='append')
	
for yr in range(2001,2016):
    startdate = dt.date(yr,10,10)
    line_data = getsportsbookdata(yr,startdate)
    line_data.to_sql('line_results',con = con,schema ='dbo',if_exists='append')
	
for yr in range(2001,2016):
    startdate = dt.date(yr,10,10)
    player_data = getNBAplayerdata(yr,startdate)
    player_data.to_sql('player_box_scores',con = con,schema ='dbo',if_exists='append')
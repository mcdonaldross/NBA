import nbashots as nba
import pandas as pd
from bs4 import BeautifulSoup
import urllib
import numpy as np
import datetime as dt

# Function 1: Extract player data

def getNBAplayerdata(startyear, date = dt.date.today()+dt.timedelta(days=-1)):
	''' This function will return Boxscore data at the player level for every game
		in the year specified, after the date specified.
		Has been validated on game going back to the 2000-2001 season 
		startyear takes an integer that represents the year we wish to pull data from 
		date is a datetime object, that by default pulls data since the previous day
	'''
	#2015 NBA Season Player data
	all_players = nba.get_all_player_ids("all_data")

	#Only include players that have played this year
	player_list = all_players[all_players.TO_YEAR >= startyear].PERSON_ID

	#get rid of the time stamp from the date data
	date = dt.datetime.fromordinal(date.toordinal())

	#initiate DF to build on with Chef Curry Data
	NBA_playerdata = pd.DataFrame()

	#no while loop necessary
	season =  str(startyear)+'-'+str(int(str(startyear)[2:4])+1).zfill(2)

	for player_ID in player_list:    
		settings =  {'LeagueID': '00',
					'PlayerID': player_ID,
					'Season': season,
					'SeasonType': 'Regular Season'}
		player_data = nba.PlayerLog(player_ID)
		player_data.update_params(settings)
	
		player_data_df = player_data.get_game_logs()
		player_data_df = player_data_df[player_data_df['GAME_DATE']>=date]
	
	
		NBA_playerdata = NBA_playerdata.append(player_data_df)
	
	NBA_playerdata = NBA_playerdata.merge(all_players[['PLAYERCODE', 'PERSON_ID']], left_on = 'Player_ID', right_on = 'PERSON_ID')
	del NBA_playerdata['PERSON_ID']
	
	return NBA_playerdata

def getNBAteamdata(startyear, date = dt.date.today()+dt.timedelta(days=-1)):
	''' This function will return Boxscore data at the team level for every game
		in the year specified, after the date specified.
		Has been validated on game going back to the 2000-2001 season.
		startyear takes an integer that represents the year we wish to pull data from 
		date is a datetime object, that by default pulls data since the previous day
	'''
	all_teams   = nba.get_all_team_ids()
	all_teams   = all_teams[all_teams.TEAM_ID <> 0]
	
	#get rid of the time stamp from the date data
	date = dt.datetime.fromordinal(date.toordinal())
	
	team_list = all_teams.TEAM_ID
	
	NBA_teamdata = pd.DataFrame()
	
	season =  str(startyear)+'-'+str(int(str(startyear)[2:4])+1).zfill(2)

	for team_ID in team_list:    
		settings =  {'LeagueID': '00',
					'PlayerID': team_ID,
					'Season': season,
					'SeasonType': 'Regular Season'}
		
		team_data = nba.TeamLog(team_ID)
		team_data.update_params(settings)
		team_data_df = team_data.get_game_logs()
		team_data_df = team_data_df[team_data_df['GAME_DATE']>=date]

		NBA_teamdata = NBA_teamdata.append(team_data_df)

	NBA_teamdata = NBA_teamdata.merge(all_teams, left_on = 'Team_ID', right_on = 'TEAM_ID')
	del NBA_teamdata['TEAM_ID']
	
	# making joins easier
	NBA_teamdata['GAME_DATE']   = pd.to_datetime(NBA_teamdata.GAME_DATE)
	NBA_teamdata['date_as_int'] = [date.year*10000+date.month*100+ date.day for date in NBA_teamdata.GAME_DATE]
	
	# fix 2000-2002 Hornets/Pelicans name-team_id issue
	NBA_teamdata.loc[(NBA_teamdata['Team_ID'] == 1610612766) & (NBA_teamdata.date_as_int < 20020418), 'Team_ID'] = 1610612740   
	
	return NBA_teamdata

def getsportsbookdata(startyear, date = dt.date.today()+dt.timedelta(days=-1)):
	'''
	This functions returns all of the line/overunder data for each NBA game
	after the specified year and date.
	Has been validated on game going back to the 2000-2001 season 
	startyear takes an integer that represents the year we wish to pull data from 
	date is a datetime object, that by default pulls data since the previous day
	'''
	# A list of all the team id's associated with NBA teams on covers.com	
	teamids = [
	'404169', '404117', '404288', '404083', '404330', '404198', '404213', '404153',
	'404155', '404011', '404085', '664421', '404171', '404013', '404067', '404065',
	'403995', '404316', '403993', '404031', '404119', '404135', '403977', '404029', 
	'403975', '404047', '404137', '404049', '404101', '404302']

	bettingdata = {'team':[], 'date': [], 'opponent': [], 
			'score': [], 'season_type': [], 'line': [], 
			'OverUnder': []}
	
	#get rid of the time stamp from the date data
	date = dt.datetime.fromordinal(date.toordinal())

	#set to refill date
	for team in teamids:
		yearstr = str(startyear)+'-'+str(startyear+1) 
		urlstring = r'http://www.covers.com/pageLoader/pageLoader.aspx?page=/data/nba/teams/pastresults/'+yearstr+'/team'+team+'.html'
	
		#pull the weblink
		r = urllib.urlopen(urlstring).read()
		soup = BeautifulSoup(r,'lxml')
	
	
		soup.find_all('div',class_="teamname")
		if len(soup.find_all('div',class_="teamname"))>0:
			teamname = soup.find_all('div',class_="teamname")[0].find_all('h1', class_="teams")[0].get_text().strip()
			#loop through and append betting data
			for table in soup('table'): 
				for row in table.find_all('tr')[1:]:
					cells = row.find_all('td')
					gamedate = dt.datetime.strptime(cells[0].get_text()[10:],'%m/%d/%y')
					if gamedate >= date:
						bettingdata['team'].append(teamname)
						bettingdata['date'].append(cells[0].get_text())
						bettingdata['opponent'].append(cells[1].get_text())
						bettingdata['score'].append(cells[2].get_text())
						bettingdata['season_type'].append(cells[3].get_text())
						bettingdata['line'].append(cells[4].get_text())
						bettingdata['OverUnder'].append(cells[5].get_text())
	
	bettingdata = pd.DataFrame(bettingdata)
	
	bettingdata['OverUnderOutcome'] = [i[10] for i in bettingdata.OverUnder]
	bettingdata['OverUnderLine'] = [float(i[12:]) if i[12:]!='-' else None for i in bettingdata.OverUnder]
	bettingdata['SpreadOutcome'] = [i[10] for i in bettingdata.line]
	bettingdata['Spread'] = [float(i[12:]) if i[12:]!='PK' and i[12:]!='-' else 0.0 for i in bettingdata.line]
	bettingdata['season_type'] = [i.replace('\r','').replace('\n','') for i in bettingdata.season_type]
	bettingdata['season_type'] = bettingdata['season_type'].str.strip()
	bettingdata['team'] = [i.replace('\r','').replace('\n','') for i in bettingdata.team]
	bettingdata['GameOutome'] = [i[10] for i in bettingdata.score]
	bettingdata['Points_Team'] = [float(i[12:i.index('-')]) for i in bettingdata.score]
	bettingdata['Points_Opponent'] = [float(i[i.index('-')+1:i.index('-')+4]) for i in bettingdata.score]
	bettingdata['OT'] = [True if i.find('OT') > 0 else False for i in bettingdata.score]
	bettingdata['Location'] = ['Away' if i.find('@') > 0 else 'Home' for i in bettingdata.opponent]
	bettingdata['opponent'] = [i.strip().replace('@ ','') for i in bettingdata.opponent]
	bettingdata['date'] = [dt.datetime.strptime(i[10:],'%m/%d/%y') for i in bettingdata.date]
	
	del bettingdata['OverUnder']
	del bettingdata['line']
	del bettingdata['score']
	
	bettingdata = bettingdata[bettingdata['season_type'] == 'Regular Season']
	
	# fix trailblazer name problem
	bettingdata['TEAM_NAME'] = [team.rsplit(None, 1)[-1] for team in bettingdata.team]
	bettingdata['TEAM_NAME'] = ['Trail Blazers' if team == 'Blazers' else team for team in bettingdata.TEAM_NAME]
	
	#fields to make joins easier
	bettingdata['date']        = pd.to_datetime(bettingdata.date)
	bettingdata['date_as_int'] = [date.year*10000+date.month*100+ date.day for date in bettingdata.date]
    
	return bettingdata

def merge_team_line_data(line_data, team_data):
	'''
	This functions merges team and line_Data to create a mashed up dataset.
	'''
	
	# getting team_ids into line_data for joins
	team_id_combos = team_data[['TEAM_NAME', 'Team_ID']].drop_duplicates().set_index('TEAM_NAME')
	team_id_combos = team_id_combos['Team_ID'].to_dict()
	line_data['Team_ID'] = [team_id_combos[team] for team in line_data.TEAM_NAME]
	
	# merge line and team game data
	team_line_data = team_data.merge(line_data, how = 'left', on = ['date_as_int', 'Team_ID'])
	
	# delete 4/16/2013 BOS-IND game that got canceled 
	team_line_data = team_line_data[team_line_data.Game_ID != 21201214]
	del team_line_data['TEAM_NAME_y']
	team_line_data.rename(columns={'TEAM_NAME_x': 'TEAM_NAME'}, inplace=True)
	team_line_data['season'] = [date.year + 1 if date.month >= 10 else date.year for date in team_line_data.GAME_DATE]
	team_line_data['game_num'] = team_line_data.groupby(['season', 'Team_ID'])['date_as_int'].rank(ascending=True)
	team_line_data['Location'] = ['Away' if matchup.find('@') >= 0 else 'Home' for matchup in team_line_data.MATCHUP]
	
	return team_line_data
	
def team_feature_generation(nbadata):
	'''
	This is where we create the base team dataset for prediction
	'''
	nbadata['game_num'] = nbadata.groupby(['season', 'Team_ID'])['date_as_int'].rank(ascending=True)-1
	
	nbadata = nbadata.set_index(['season','game_num','Team_ID','Location'], drop = False)
	nbadata['GAME_DATE'] = pd.to_datetime(nbadata['GAME_DATE'],format='%Y-%m-%d')
	
	# Basic Feature Engineering
	nbadata['LAST_GAME'] = nbadata.sort_index(ascending=True).groupby(level = [0,2])['GAME_DATE'].shift(1)
	nbadata['LAST_GAME_Location'] = nbadata.sort_index(ascending=True).groupby(level = [0,2])['Location'].shift(1)
	nbadata['DAYS_OFF']  = ((nbadata['GAME_DATE']-nbadata['LAST_GAME']).astype('timedelta64[D]'))
	nbadata['TRAVEL_FLAG'] = np.where(np.logical_or(nbadata['Location'] == 'Away',nbadata['LAST_GAME_Location'] =='Away'),1,0 )
	nbadata['Line_Pt_Prediction'] = (nbadata['OverUnderLine']-nbadata['Spread'])/2
	
	nbadata['AVG_PTS'] = nbadata.sort_index(ascending=True).groupby(level = [0,2])['PTS'].apply(
													lambda x: pd.rolling_mean(x,window=82,min_periods=1,how="down").shift(1))
	nbadata['AVG_REB'] = nbadata.sort_index(ascending=True).groupby(level = [0,2])['REB'].apply(
													lambda x: pd.rolling_mean(x,window=82,min_periods=1,how="down").shift(1))
	nbadata['AVG_BLK'] = nbadata.sort_index(ascending=True).groupby(level = [0,2])['BLK'].apply(
													lambda x: pd.rolling_mean(x,window=82,min_periods=1,how="down").shift(1))
	nbadata['AVG_AST'] = nbadata.sort_index(ascending=True).groupby(level = [0,2])['AST'].apply(
													lambda x: pd.rolling_mean(x,window=82,min_periods=1,how="down").shift(1))
	nbadata['AVG_STL'] = nbadata.sort_index(ascending=True).groupby(level = [0,2])['STL'].apply(
													lambda x: pd.rolling_mean(x,window=82,min_periods=1,how="down").shift(1))
	nbadata['AVG_TOV'] = nbadata.sort_index(ascending=True).groupby(level = [0,2])['TOV'].apply(
													lambda x: pd.rolling_mean(x,window=82,min_periods=1,how="down").shift(1))
	nbadata['AVG_FGM'] = nbadata.sort_index(ascending=True).groupby(level = [0,2])['FGM'].apply(
													lambda x: pd.rolling_mean(x,window=82,min_periods=1,how="down").shift(1))
	nbadata['AVG_FGA'] = nbadata.sort_index(ascending=True).groupby(level = [0,2])['FGA'].apply(
													lambda x: pd.rolling_mean(x,window=82,min_periods=1,how="down").shift(1))
	nbadata['AVG_FTA'] = nbadata.sort_index(ascending=True).groupby(level = [0,2])['FTA'].apply(
													lambda x: pd.rolling_mean(x,window=82,min_periods=1,how="down").shift(1))
	nbadata['AVG_FTM'] = nbadata.sort_index(ascending=True).groupby(level = [0,2])['FTM'].apply(
													lambda x: pd.rolling_mean(x,window=82,min_periods=1,how="down").shift(1))
	nbadata['AVG_OREB'] = nbadata.sort_index(ascending=True).groupby(level = [0,2])['OREB'].apply(
													lambda x: pd.rolling_mean(x,window=82,min_periods=1,how="down").shift(1))
	nbadata['AVG_DREB'] = nbadata.sort_index(ascending=True).groupby(level = [0,2])['DREB'].apply(
													lambda x: pd.rolling_mean(x,window=82,min_periods=1,how="down").shift(1))
    
	merge_fields = nbadata[["team","Team_ID","Game_ID","DAYS_OFF","TRAVEL_FLAG","AVG_PTS","AVG_REB","AVG_BLK","AVG_AST","AVG_STL","AVG_TOV","AVG_FGM","AVG_FGA","AVG_FTM","AVG_FTA","AVG_OREB","AVG_DREB","PTS","BLK","REB","AST","STL","TOV","FGM","FGA","FTM","FTA","OREB","DREB"]]
	nbadata2 = nbadata.merge(merge_fields, how = 'left', on = ['Game_ID'], suffixes=("", "_OPP")).query(
											"Team_ID != Team_ID_OPP").set_index(['season','game_num','Team_ID','Location'],drop = False)

	nbadata2['POSS'] = 0.5*( 
		(
		nbadata2['FGA']+
		.4*nbadata2['FTA'] - 
		1.07*(nbadata2['OREB']/(nbadata2['OREB']+nbadata2['DREB_OPP']))*(nbadata2['FGA']-nbadata2['FGM'])+
		nbadata2['TOV'])+
		(
		nbadata2['FGA_OPP']+
		.4*nbadata2['FTA_OPP'] - 
		1.07*(nbadata2['OREB_OPP']/(nbadata2['OREB_OPP']+nbadata2['DREB']))*(nbadata2['FGA_OPP']-nbadata2['FGM_OPP'])+
		nbadata2['TOV_OPP']
		)
		) 

	nbadata2['PACE'] = 48*(nbadata2['POSS']*2/(2*(nbadata2['MIN']/5)))
    
	nbadata2['AVG_PACE'] = nbadata2.sort_index(ascending=True).groupby(level = [0,2])['PACE'].apply(
													lambda x: pd.rolling_mean(x,window=82,min_periods=1,how="down").shift(1))
	nbadata2['AVG_POSS'] = nbadata2.sort_index(ascending=True).groupby(level = [0,2])['POSS'].apply(
													lambda x: pd.rolling_mean(x,window=82,min_periods=1,how="down").shift(1))
	nbadata3 = nbadata2.merge(nbadata2[['Game_ID','Team_ID','AVG_PACE','AVG_POSS']],how = 'left',left_on = ['Game_ID','Team_ID_OPP'],right_on = ['Game_ID','Team_ID'],suffixes = ("","_NEW") )
	del nbadata3['Team_ID_NEW'] ;
	nbadata3.rename(columns = {'AVG_PACE_NEW':'AVG_PACE_OPP','AVG_POSS_NEW':'AVG_POSS_OPP'},inplace = True)
	return nbadata3
import requests
import json
import pandas

#create player class
class Player:
	def __init__(self,id_,squadid,teams,first, last, cost):
		self.id = id_
		self.squadid = squadid
		self.team = []
		self.first = first
		self.last = last
		self.name = " ".join([self.first,self.last])
		self.cost = cost
		self.matchhistory = []
	def findteam(self,teamlist):
		for team in teamlist:
			if(team.id==self.squadid):
				self.team = team
	def findmatchhistory(self,matchhistory):
		matches = []
		for match in matchhistory[:-1]:
			m = playerMatch(match["stats"],match["match_id"])
			matches.append(m)
		self.matchhistory = matches

class Team:
	def __init__(self,id_,short,long_,name):
		self.short = short
		self.long = long_
		self.name = name
		self.id = id_
		self.players = []
	def findplayers(self,playerlist):
		roster=[]
		for player in playerlist:
			if player.squadid==self.id:
				roster.append(player)
		self.players=roster
class playerMatch:
	def __init__(self,stats,matchid):
		self.mins = stats["MIN"]
		self.crs = stats["CRS"]
		self.yc = stats["YC"]
		self.br = stats["BR"]
		self.ass = stats["ASS"]
		self.ps = stats["PS"]
		self.bc = stats["BC"]
		self.sh = stats["SH"]
		self.tck = stats["TCK"]
		self.rc = stats["RC"]
		self.pm = stats["PM"]
		self.cl = stats["CL"]
		self.pe = stats["PE"]
		self.elg = stats["ELG"]
		self.gc = stats["GC"]
		self.blk = stats["BLK"]
		self.cs = stats["CS"]
		self.gl = stats["GL"]
		self.og = stats["OG"]
		self.aps = stats["APS"]
		self.sv = stats["SV"]
		self.int = stats["INT"]
		self.kp = stats["KP"]
		self.pss = stats["PSS"]
		self.oga = stats["OGA"]
		self.matchid = matchid

#load live json from mls website
players = requests.get(url='https://fgp-data-us.s3.amazonaws.com/json/mls_mls/players.json').json()
teams = requests.get(url='https://fgp-data-us.s3.amazonaws.com/json/mls_mls/squads.json').json()
rounds = requests.get(url='https://fgp-data-us.s3.amazonaws.com/json/mls_mls/rounds.json').json()
#write json to txt file for manual parsing 
with open('players.json', 'w') as outfile:  
    json.dump(players, outfile)
with open('squads.json', 'w') as outfile:  
    json.dump(teams, outfile)	
with open('rounds.json', 'w') as outfile:  
    json.dump(rounds, outfile)
#populate playerlist and teamlist
playerlist = []
teamlist = []
for team in teams:
	t = Team(
		team["id"], #take in player id from json
		team["short_name"],#take in squad id from json
		team["full_name"],#take in first name from json
		team["name"],#take in last name from json
		)
	teamlist.append(t)
for player in players:
	p = Player(
		player["id"], #take in player id from json
		player["squad_id"],#take in squad id from json
		teamlist,
		player["first_name"],#take in first name from json
		player["last_name"],#take in last name from json
		player["cost"]#take in cost from json
		)
	playerlist.append(p)
#attribute players to teams
for player in playerlist:
	player.findteam(teamlist)
for team in teamlist:
	team.findplayers(playerlist)
#test player list of arbitrary team
for player in playerlist:
	try:
		url = "https://fgp-data-us.s3.amazonaws.com/json/mls_mls/stats/players/"+str(player.id)+".json"
		matchhistory = requests.get(url=url).json()
		player.findmatchhistory(matchhistory)
	except ValueError:
		print("JSON Couldn't be found for: " + player.name)







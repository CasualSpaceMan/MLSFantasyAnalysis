import requests
import json
import matplotlib.pyplot as plt
import pylab
import numpy

#create player class
class Player:
	def __init__(self,player):
		self.team = []
		self.matchhistory = []
		self.pricehistory = []
		self.pointhistory = []
		self.id = player["id"]
		self.squadid = player["squad_id"]
		self.first = player["first_name"]
		self.last = player["last_name"]
		self.cost = float(player["cost"])/1000000
		self.position = player["positions"]
		self.tp = player["stats"]["total_points"]
		self.gp = player["stats"]["games_played"]
		self.sr = player["stats"]["season_rank"]
		self.ob = player["stats"]["owned_by"]
		self.l3a = player["stats"]["last_3_avg"]
		self.rr = player["stats"]["round_rank"]
		self.ap = player["stats"]["avg_points"]
		self.lmp = player["stats"]["last_match_points"]
		self.sel = player["stats"]["selections"]
		self.ls = player["stats"]["low_score"]
		self.hs = player["stats"]["high_score"]
		self.l5a = player["stats"]["last_5_avg"]
		self.name = " ".join([self.first,self.last])

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
	def findpointhistory(self,person):
		hist = []
		for i in range(len(player["stats"]["scores"])):
			try:
				hist.append(player["stats"]["scores"][str(i+1)])
			except KeyError:
				hist.append(None)
		self.pointhistory = hist
	def findpricehistory(self,person):
		hist = []
		for i in range(len(player["stats"]["prices"])):
			try:
				hist.append(float(player["stats"]["prices"][str(i+1)])/1000000)
			except KeyError:
				hist.append(None)
		self.pricehistory = hist
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
with open('jsonlcl/players.json', 'w') as outfile:  
    json.dump(players, outfile)
with open('jsonlcl/squads.json', 'w') as outfile:  
    json.dump(teams, outfile)	
with open('jsonlcl/rounds.json', 'w') as outfile:  
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
	p = Player(player)
	p.findpricehistory(player)
	p.findpointhistory(player)
	playerlist.append(p)
#attribute players to teams
for player in playerlist:
	player.findteam(teamlist)
for team in teamlist:
	team.findplayers(playerlist)
#test player list of arbitrary team
for player in playerlist:
		try:
			with open('jsonlcl/'+str(player.id)+'.json', 'r') as infile: 
				matchhistory = json.load(infile)
				player.findmatchhistory(matchhistory)
		except:
			pass

x = []
y = []
for player in playerlist:
	x.append(player.cost)
	y.append(player.l5a)
z = numpy.polyfit(x, y, 1)
p = numpy.poly1d(z)
pylab.plot(x,p(x),"r--")
# the line equation:
print "y=%.6fx+(%.6f)"%(z[0],z[1])
plt.scatter(x,y)
plt.title('cost vs. 5 week average')
plt.ylabel('5 week average')
plt.xlabel('cost')
plt.show()


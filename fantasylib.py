import requests
import json
import numpy
import pylab
import time
import tqdm
from time import sleep
from datetime import date
from datetime import datetime
import numpy as np
from ortools.linear_solver import pywraplp


playerlist = []
teamlist = []
Gameweeks = []

# picks round to stop data intake, set to gwnum(rounds) to get most up to date gameweek

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
		self.cost = None
		self.position = player["positions"][0]
		self.gp = player["stats"]["games_played"]
		self.tp = player["stats"]["total_points"]
		self.sr = player["stats"]["season_rank"]
		self.ob = player["stats"]["owned_by"]
		self.l3a = player["stats"]["last_3_avg"]
		self.rr = player["stats"]["round_rank"]
		self.lmp = player["stats"]["last_match_points"]
		self.sel = player["stats"]["selections"]
		self.ls = player["stats"]["low_score"]
		self.hs = player["stats"]["high_score"]
		self.l5a = player["stats"]["last_5_avg"]
		self.proj = list(player["stats"]["projected_scores"].values())[0]
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
	def findpointhistory(self,person,rounds):
		hist = []
		for i in range(gwnum(rounds)+1):
			try:
				hist.append(person["stats"]["scores"][str(i+1)])
			except KeyError:
				hist.append(0)
			except TypeError:
				hist.append(0)
		self.l3a = sum(hist[(len(hist)-4):(len(hist)-1)])/3
		self.pointhistory = hist
		self.ap = sum(hist)/len(hist)
	def findpricehistory(self,person,rounds):
		hist = []
		for i in range(gwnum(rounds)+1):
			try:
				hist.append(float(person["stats"]["prices"][str(i+1)])/1000000)
			except KeyError:
				hist.append(None)
		self.pricehistory = hist
		try:
			self.cost = float(hist[-1])
		except TypeError:
			self.cost = None

class Team:
	def __init__(self,id_,short,long_,name,elo):
		self.short = short
		self.long = long_
		self.name = name
		self.id = id_
		self.players = []
		self.elo = elo
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

class teamMatch:
	def __init__(self,game):
		self.id = game['id']
		self.hid = game['home_squad_id']
		self.aid = game['away_squad_id']
		self.round = game['real_round']
		self.hoscr = game['home_score']
		self.awscr = game['away_score']
		self.home = self.gethome()
		self.away = self.getaway()
	def gethome(self):
		for team in teamlist:
			if team.id == self.hid:
				return team
	def getaway(self):
		for team in teamlist:
			if team.id == self.aid:
				return team
	def uelo(self):
		x = self.home.elo - self.away.elo
		Eh = 1/(1+10**(x/400))
		Ea = 1/(1+10**(-x/400))
		if (self.hoscr==self.awscr or abs(self.hoscr-self.awscr)==1):
			G = 1
		if abs(self.hoscr-self.awscr) == 2:
			G =3/2
		if abs(self.hoscr-self.awscr)>=3:
			G = (11+(abs(self.hoscr-self.awscr)))/8
		if self.hoscr > self.awscr:
			Sh = 1;
			Sa = 0;
		if self.hoscr < self.awscr:
			Sh = 0;
			Sa = 1;
		if self.hoscr == self.awscr:
			Sh = 0.5;
			Sa = 0.5;
		self.home.elo = int(self.home.elo + 32*G*(Sh-Eh))
		self.away.elo = int(self.away.elo + 32*G*(Sa-Ea))
		dr = self.home.elo-self.away.elo
		self.hwe = (1/(10**(-dr/400)+1))
		dr = self.away.elo-self.home.elo
		self.awe = (1/(10**(-dr/400)+1))
def populatelocaljson():	#load live json from mls website
	players = requests.get(url='https://fgp-data-us.s3.us-east-1.amazonaws.com/json/mls_mls/players.json?_=1646966560478').json()
	teams = requests.get(url='https://fgp-data-us.s3.us-east-1.amazonaws.com/json/mls_mls/squads.json?_=1646966560478').json()
	rounds = requests.get(url='https://fgp-data-us.s3.us-east-1.amazonaws.com/json/mls_mls/rounds.json?_=1646966560474').json()
	#write json to txt file for manual parsing 
	with open('jsonlcl/players.json', 'w') as outfile:  
		json.dump(players, outfile)
	with open('jsonlcl/rounds.json', 'w') as outfile:  
		json.dump(rounds, outfile)

	for i in tqdm.tqdm(range(len(players))):
		try:
			player = players[i]
			url = "https://fgp-data-us.s3.amazonaws.com/json/mls_mls/stats/players/"+str(player["id"])+".json"
			matchhistory= requests.get(url=url).json()
			with open('jsonlcl/'+str(player["id"])+'.json', 'w') as outfile:  
				json.dump(matchhistory, outfile)
			print('\n'*100)
		except ValueError:
			print('\n'*100)
			pass
def getlocaljson():
	with open('jsonlcl/players.json', 'r') as infile:  
		players = json.load(infile)
	with open('jsonlcl/squads.json', 'r') as infile:  
		teams = json.load(infile)
	with open('jsonlcl/rounds.json', 'r') as infile:  
		rounds = json.load(infile)
	return players,teams,rounds
def setup():
	players,teams,rounds = getlocaljson()
	#populate playerlist and teamlist
	for team in teams:
		t = Team(
			team["id"], #take in player id from json
			team["short_name"],#take in squad id from json
			team["full_name"],#take in first name from json
			team["name"],#take in last name from json
			team["start_elo"]
		)
		teamlist.append(t)
	for player in players:
		p = Player(player)
		p.findpricehistory(player,rounds)
		p.findpointhistory(player,rounds)
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
	for Round in rounds:
		Gameweek = Round['matches']
		gw = []
		for game in Gameweek:
			g = teamMatch(game)
			sd = Round['start']
			if Round['id'] <= gwnum(rounds):
				g.uelo()
			gw.append(g)
		Gameweeks.append(gw)
	return playerlist,teamlist,Gameweeks
def teamselect(CG,players,RMS):
	iD = [] #list of player id numbers
	price = [] #list of price associated with each player (should line up with id)
	team = [] #list of team id associated with each player
	pos = [] #list of position associated with each player
	eS = [] #list of expected scores

	# populate lists that will be used for MILP process
	for game in CG:
		for player in game.home.players:
			if player.cost is not None:
#check if player is already in the list (double gameweek condition)
				if player.id in iD:	
					dr = game.home.elo-game.away.elo
					AS = player.ap*(1/(10**(-dr/400)+1))
					eS[iD.index(player.id)] = eS[iD.index(player.id)] + AS
#if they aren't then add a new element to the array
				else:
					dr = game.home.elo-game.away.elo
					AS = player.ap*(1/(10**(-dr/400)+1))
					iD.append(player.id)
					price.append(player.cost)
					team.append(player.squadid)
					pos.append(player.position)
					eS.append(AS)

		for player in game.away.players:
			if player.cost is not None:
				if player.id in iD:	
					dr = game.away.elo-game.home.elo
					AS = player.ap*(1/(10**(-dr/400)+1))
					eS[iD.index(player.id)] = eS[iD.index(player.id)] + AS
				else:
					dr = game.away.elo-game.home.elo
					AS = player.ap*(1/(10**(-dr/400)+1))
					iD.append(player.id)
					price.append(player.cost)
					team.append(player.squadid)
					pos.append(player.position)
					eS.append(AS)
	#define team constraints for each team
	tc = [[0]*len(iD)]*28
	for i,t in enumerate(teamlist):
		tc[i]= list(map(int,list(np.array(team)==t.id)))

	pc = [[0]*len(iD)]*4
	positions = [1,2,3,4]

	for i,a in enumerate(positions):
		pc[i] = list(map(int,list(np.array(pos)==a)))
	constraint_matrix = tc + pc + [price]
	cub = [3]*28 + [2,5,5,3]+[RMS]
	clb = [0]*28 + [2,5,5,3]+[0]

	def create_data_model():
		data = {}
		data['constraint_coeffs'] = constraint_matrix
		data['bounds'] = cub
		data['obj_coeffs'] = eS #coefficients of objective function are adjusted scores for upcoming match
		data['num_vars'] = len(iD) #number of variables is equal to the total number of players 
		data['num_constraints'] = 33 #team constraints: 28 , position constraints: 4, cost constraints: 1 = 33
		return data
	data = create_data_model()
	solver = pywraplp.Solver.CreateSolver('SCIP')
	x = {}
	for j in range(data['num_vars']):
		x[j] = solver.IntVar(0,1,'x[%i]' % j)
	for i in range(data['num_constraints']):
		constraint = solver.RowConstraint(clb[i], data['bounds'][i], '')
		for j in range(data['num_vars']):
			constraint.SetCoefficient(x[j], data['constraint_coeffs'][i][j])
	objective = solver.Objective()
	for j in range(data['num_vars']):
		objective.SetCoefficient(x[j], data['obj_coeffs'][j])
	objective.SetMaximization()

	status = solver.Solve()
	if status == pywraplp.Solver.OPTIMAL:
	    print('Objective value =', solver.Objective().Value())
	    print('Problem solved in %f milliseconds' % solver.wall_time())
	    print('Problem solved in %d iterations' % solver.iterations())
	    print('Problem solved in %d branch-and-bound nodes' % solver.nodes())
	else:
	    print('The problem does not have an optimal solution.')
	squad_ids = []
	for j in range(data['num_vars']):
		if (x[j].solution_value()==1):
			squad_ids.append(iD[j])
	squad = []
	for num in squad_ids:
		for player in playerlist:
			if num==player.id:
				squad.append(player)
	cost = 0
	print('-------------')
	for val in positions:
		for player in squad:
				if player.position == val:
					print(player.name + ','+str(player.position)+','+player.team.long+','+str(player.cost))
					cost = cost+player.cost

		print('-------------')
	print(cost)
def gwnum(rounds):
	i=0
	for round in rounds:
		if round['status']=='complete':
			i=i+1
	return i
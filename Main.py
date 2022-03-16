from fantasylib import *
import statistics as stat
import matplotlib.pyplot as plt, mpld3
import numpy as np
from ortools.linear_solver import pywraplp

#populatelocaljson()
#pull playerlist from json
players,teams,rounds = getlocaljson()
playerlist,teamlist, Gameweeks = setup()

# Rank Top PLayers based on adjusted score
CG = Gameweeks[3]
iD = [] #list of player id numbers
price = [] #list of price associated with each player (should line up with id)
team = [] #list of team id associated with each player
pos = [] #list of position associated with each player
eS = [] #list of expected scores


# populate lists that will be used for MILP process
for game in CG:
	for player in game.home.players:
		if player.cost is not None:
			dr = game.home.elo-game.away.elo
			AS = player.ap*(1/(10**(-dr/400)+1))
			iD.append(player.id)
			price.append(player.cost)
			team.append(player.squadid)
			pos.append(player.position)
			eS.append(AS)

	for player in game.away.players:
		if player.cost is not None:
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
cub = [3]*28 + [2,5,5,3]+[103.1]
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

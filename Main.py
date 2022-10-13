from fantasylib import *
from sklearn.linear_model import LinearRegression
import numpy as np

populatelocaljson()

#pull playerlist from json
players,teams,rounds = getlocaljson()
playerlist,teamlist, Gameweeks = setup()
print('setup complete')

# Rank Top PLayers based on adjusted score
CG = Gameweeks[gwnum(rounds)]
team_value = 143.7
teamselect(CG,players,team_value)
from fantasylib import *
import numpy as np

populatelocaljson()

# pull playerlist from json
players, teams, rounds, playerlist, teamlist, Gameweeks = setup('jsonlcl')
print('setup complete')


# Rank Top PLayers based on adjusted score
def objFun(player, dr):
    #AdjSc = player.ap * (1 / (10 ** (-dr / 400) + 1))
    AdjSc = player.pointhistory[0]
    return AdjSc

CG = Gameweeks[gwnum(rounds)-1]
team_value = 100
teamselect(CG,players,team_value,objFun)

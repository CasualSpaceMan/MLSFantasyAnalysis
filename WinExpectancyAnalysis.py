from fantasylib import *
from sklearn.linear_model import LinearRegression
import numpy as np

players,teams,rounds = getlocaljson()
playerlist,teamlist, Gameweeks = setup()

# create loop and calculate win expectancy
i = 1
OVR=0
UND=0
COR=0
CS = 0
total = 0
for gameweek in Gameweeks:
	total = total + len(gameweek)
	for game in gameweek:

		#calculate win expectancy
		dr = game.home.elo-game.away.elo
		WE = (1/(10**(-dr/400)+1))
		#represent game result as either 1 (win), 0 (loss), 0.5 (draw)
		if game.hoscr>game.awscr:
			WR = 1
		elif game.hoscr<game.awscr:
			WR = 0
		else:
			WR = 0.5
		if game.hoscr==0 or game.awscr ==0:
			CS = CS+1
		if WR == 1:
			if WE>0.5:
				COR = COR+1
			else:
				UND = UND+1
		elif WR == 0:
			if WE<0.5:
				COR = COR+1
			else:
				OVR = OVR+1
		else:
			if WE>0.45 and WE<0.55:
				COR = COR+1
			elif WE<0.45:
				UND = UND+1
			else:
				OVR = OVR+1
	if i>=gwnum(rounds):
		break
	i = i+1
print('Over ',OVR,' ','Under ', UND,' ','Correct ',COR)
print(CS)
print(total)
#!/usr/bin/env python

from pymongo import MongoClient

class State:
	OPEN=1
	WINS=2
	DONE=3
	EOF=4

with open('log') as log:
	state=State.OPEN
	team1=''
  	team2=''
  	winner=''
  	loser=''
  	line=''
  	author1=''
  	author2=''
  	tier=''
  	mode=''
  	matchID=''

	# connect to mongodb
	client=MongoClient()
	db=client.saltybet

	while (state != State.EOF):
		line=log.readline()

		if line == '':
			state=State.EOF
		
		if state == State.OPEN:
			if "OPEN" in line:
				if not ("Team" in line and " vs " in line and " vs Team " in line):
					state=State.WINS
					# parse out player/team names
					team1=line[(line.find("Bets are OPEN for ")+18):(line.find(" vs "))]
					team2=line[(line.find(" vs ")+4):(line.find("! ("))]
					tier=line[(line.find("! (")+3):(line.find(" Tier)"))]
					if "(matchmaking)"in line:
						mode="matchmaking"
					elif "tournament bracket" in line:
						mode="tournament"
					else:
						mode=""

					matchID = db.matches.insert(
							{ 
	                          'player1': team1,
	                          'player2': team2,
	                          'tier': tier,
	                          'mode': mode 
	                        },
						)

		elif state == State.WINS:
			if "wins" in line:
				state=State.DONE
				# parse out winner name
				winner=line[:line.find(" wins!")]
				if team1 in winner:
					loser=team2
				else:
					loser=team1
				
			elif "by" in line:
				if not "requested by" in line:
					if team1 in line and team2 in line:
						author1=line[(line.find("by ")+3):(line.find(", "))]
						author2=line[(line.find(", "+team2+" by ")+len(team2)+6):(line.find("\n"))]

		if state == State.DONE:
			state=State.OPEN
			db.names.update(
					{ 
						'name': team1
					},
					{ 
					  	'$set': {'author': author1 },
					  	'$inc': { 'games': 1 } 
					},
					upsert=True
				)
			db.names.update(
					{ 
						'name': team2 
					},
					{ 
						'$set': {'author': author2 },
						'$inc': { 'games': 1 } 
					},
					upsert=True
				)
			db.names.update(
					{ 
						'name': winner
					},
					{ 
						'$inc': { 'wins': 1 }
					},
					upsert=True
				)
			db.names.update(
					{ 
						'name': winner
					},
					{ 
						'$inc': { 'losses': 1}
					},
					upsert=True
				)
			db.matches.update(
					{ 
						'_id': matchID
                    },
                    { 
                    	'$set': { 'winner': winner }
                    },
                    upsert=True
				)
			# with open('log','a') as fstr:
			print(team1+","+author1+","+team2+","+author2+","+tier+","+mode+","+winner+"\n")

			# printWinner(team1,team2,winner)
			team1=''
		  	team2=''
		  	winner=''
		  	loser=''
		  	line=''
		  	author1=''
		  	author2=''
		  	tier=''
		  	mode=''
		  	matchID=''

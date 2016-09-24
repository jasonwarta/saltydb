#!/usr/bin/env python

from pymongo import MongoClient
import select
import socket
import time
import random

class State:
  OPEN=1
  WINS=2
  DONE=3

def printWinner(team1,team2,winner):
  if team1==winner :
    print("("+team1+") "+team2)
  elif team2 == winner :
    print(team1+" ("+team2+")")

def available(conn):
  try:
    readable,writeable,errored=select.select([conn],[],[],0)
    if conn in readable:
      return True
  except:
    pass
  return False

def starts_with(in_str,match):
  return (match in in_str and in_str.index(match)==0)

if __name__=='__main__':
  sock=None
  nick="justinfan"
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

  random.seed();
  nRand = random.randint(1000000000000,9999999999999)

  client=MongoClient()
  db=client.saltybet

  while True:
    try:
      sock=socket.socket()
      sock.connect(("irc.chat.twitch.tv",6667))
      sock.send('NICK '+nick+str(nRand)+'\r\n')
      sock.send('JOIN #saltybet\r\n')

      while True:
        if available(sock):
          buff=sock.recv(1024)

          if not buff:
            raise Exception("Disconnect")
          for ii in range(len(buff)):
            line+=buff[ii]

            if line[-2:]=='\r\n':
              line=line.rstrip()
              ping='PING :tmi.twitch.tv'
              pong='PONG :tmi.twitch.tv\r\n'
              waifu=':waifu4u!waifu4u@waifu4u.tmi.twitch.tv PRIVMSG #saltybet :'

              if starts_with(line,ping):
                sock.send(pong)
              elif starts_with(line,waifu):
                print(line)
                line=line[len(waifu):]

                if state == State.OPEN:
                  if "OPEN" in line:
                    state=State.WINS
                    # parse out player/team names
                    team1=line[(line.find("for ")+4):(line.find(" vs "))]
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
                        }
                      )

                if state == State.WINS:
                  if "wins" in line:
                    state=State.DONE
                    # parse out winner name
                    winner=line[:line.find(" wins!")]
                    if team1 in winner:
                      loser=team2
                    else:
                      loser=team1
                    
                  if "by" in line:
                    if team1 in line and team2 in line:
                      author1=line[(line.find("by ")+3):(line.find(", "))]
                      author2=line[(line.find(", ")+2):(line.find("\n"))]

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
                  
                  with open('log','a') as fstr:
                    fstr.write(team1+","+author1+","+team2+","+author2+","+tier+","+mode+","+winner+"\n")

                  # printWinner(team1,team2,winner)
                  team1=''
                  team2=''
                  winner=''
                  loser=''
                  author1=''
                  author2=''
                  tier=''
                  mode=''
                  matchID=''

              line=''
        time.sleep(0.1)
    except KeyboardInterrupt:
      exit(1)
    except Exception as error:
      print(error)
    try:
      sock.close()
    except:
      pass
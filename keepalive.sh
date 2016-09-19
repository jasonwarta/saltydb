#!/usr/bin/env bash

# keepalive script for restarting python server when it breaks
# Usage: place in same dir as server and run from there


PID=""
if ! pgrep -f server.py 2>&1 > /dev/null; then
	echo "server wasn't running."
	echo "starting server"
	nohup ./server.py &
	PID=$!
else
	echo "server was already running"
	echo "attaching to server process"
	PID=$(pgrep -f server.py)
fi


function terminate {
	kill $PID
	exit
}
trap terminate SIGHUP SIGINT SIGKILL SIGTERM SIGSTOP


while true; do
	while pgrep -f server.py 2>&1 > /dev/null; do
		sleep 1
	done

	echo "$(date): Restarting saltydb python server" >> death_log.txt
	nohup ./server.py &
	PID=$!
done
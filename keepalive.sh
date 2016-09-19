#!/usr/bin/env bash

# keepalive script for restarting python server when it breaks
# Usage: place in same dir as server and run from there

./server.py &
PID=$!


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
	./server.py &
	PID=$!
done
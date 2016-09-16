#!/usr/bin/env python

import SimpleHTTPServer
import BaseHTTPServer
import urllib
import urlparse
import json

from pymongo import MongoClient
client = MongoClient()
db=client.saltybet

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def do_GET(self):
		page = open("results.html","r")
		self.send_response(200)
		self.send_header("Content-type","text/html")
		self.end_headers()
		self.wfile.write(page.read())
		self.wfile.close()

	def do_POST(self):
		queryName=urlparse.urlparse(self.path).query
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		queryName=urllib.unquote(queryName)
		arr={"wins":0,"games":0,"name":"not found"}
		results = db.names.find({"name":queryName})
		for doc in results:
			for key in doc:
				if key != "_id":
					arr[key] = doc[key]
		self.wfile.write(json.dumps(arr))

if __name__ == '__main__':
	Handler = MyHandler
	server=BaseHTTPServer.HTTPServer(('127.0.0.1',8080),MyHandler)
	server.serve_forever()
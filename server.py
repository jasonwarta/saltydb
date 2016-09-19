#!/usr/bin/env python

import SimpleHTTPServer
import BaseHTTPServer
import urllib
import urlparse
import json
import sys
import traceback
import datetime

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
		try:
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
		except e:
			exc_type,exc_value,exc_traceback=sys.exc_info()
			lines=traceback.format_exception(exc_type,exc_value,exc_traceback)
			with open('error_log','a') as error_log:
				error_log.write(datetime.datetime.now() + " " + line for line in lines)
				error_log.close()
			pass

if __name__ == '__main__':
	try:
		Handler = MyHandler
		server=BaseHTTPServer.HTTPServer(('127.0.0.1',8080),MyHandler)
		server.serve_forever()
	except e:
		exc_type,exc_value,exc_traceback=sys.exc_info()
		lines=traceback.format_exception(exc_type,exc_value,exc_traceback)
		with open('error_log','a') as error_log:
			error_log.write(datetime.datetime.now() + " " + line for line in lines)
			error_log.close()
		pass
	
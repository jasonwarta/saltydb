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
		try:
			print(self.path)
			page = open("live_results.html","r")
			self.send_response(200)
			self.send_header("Content-type","text/html")
			self.end_headers()
			self.wfile.write(page.read())
			self.wfile.close()
		except:
			exc_type,exc_value,exc_traceback=sys.exc_info()
			lines=traceback.format_exception(exc_type,exc_value,exc_traceback)
			with open('error_log','a') as error_log:
				error_log.write(str(datetime.datetime.now() + " GET " + line for line in lines))
				error_log.close()
			pass

	def do_POST(self):
		try:
			query=db.matches.find().limit(1).sort({'$natural':-1}).pretty()
			# query=urlparse.urlparse(self.path).query
			print(query)
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
		except:
			exc_type,exc_value,exc_traceback=sys.exc_info()
			lines=traceback.format_exception(exc_type,exc_value,exc_traceback)
			with open('error_log','a') as error_log:
				error_log.write(str(datetime.datetime.now() + " POST " + line for line in lines))
				error_log.close()
			pass

if __name__ == '__main__':
	try:
		Handler = MyHandler
		server=BaseHTTPServer.HTTPServer(('127.0.0.1',8081),MyHandler)
		server.serve_forever()
	except:
		exc_type,exc_value,exc_traceback=sys.exc_info()
		lines=traceback.format_exception(exc_type,exc_value,exc_traceback)
		with open('error_log','a') as error_log:
			error_log.write(str(datetime.datetime.now() + " MAIN " + line for line in lines))
			error_log.close()
		pass

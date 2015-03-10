import logging
import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.websocket
import os.path
import uuid

import os
import tweepy
import json
import random
import time

from tornado.concurrent import Future
from tornado import gen
from tornado.options import define, options, parse_command_line

from elasticsearch import Elasticsearch

import config

es = Elasticsearch([config.es["server"]])

# Web Server port to listen
define("port", default=config.port, help="run on the given port", type=int)

# Tweepy config
auth = tweepy.OAuthHandler(config.twitter["consumer_key"], config.twitter["consumer_secret"])
auth.set_access_token(config.twitter["access_token"], config.twitter["access_token_secret"])

# Global variables
stream = None
track = None
index = None

# Listener responsible to receive the data from Twitter and sent it to the Stream Handler
class StdOutListener(tweepy.StreamListener):
	def on_data(self, data):
		global index
		# Send tweet to the client
		StreamHandler.send_tweet(data)

		# Switch lat/lon if geo coordinates are present
		doc = tornado.escape.json_decode(data)
		if doc["geo"] is not None:
			lat = doc["geo"]["coordinates"][1]
			lon = doc["geo"]["coordinates"][0]

			doc["geo"]["coordinates"][0] = lat
			doc["geo"]["coordinates"][1] = lon

		# Store tweet in ES
		es.index(index=index, doc_type='tweet', id=doc["id_str"], body=doc)

	def on_error(self, status):
		print status

# Handler that renders the webpage
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

# Handler that manages the messages recived from the client socket
class StreamHandler(tornado.websocket.WebSocketHandler):
	waiters = set()

	def open(self):
		print 'Client connected'
		StreamHandler.waiters.add(self)
		stopStream()

	def on_message(self, data):
		obj = tornado.escape.json_decode(data)
		if obj["message"] == "start":
			print 'New Stream received'
			global track
			track = obj["track"]
			startStream(track)
		
		elif obj["message"] == "stop":
			print 'Stop Stream received'
			stopStream()

		elif obj["message"] == "pause":
			print 'Pause Stream received'
			stopStream()

		elif obj["message"] == "resume":
			print 'Resume Stream received'
			global track
			startStream(track)

	def on_close(self):
		print 'Client disconnected'
		StreamHandler.waiters.remove(self)
		stopStream()

	@classmethod
	def send_tweet(cls, tweet):
		obj = { "message": "newTweet", "tweet": tweet }
		for waiter in cls.waiters:
			try:
				waiter.write_message(obj)
			except:
				logging.error("Error sending message", exc_info=True)


# Stop Stream function
def stopStream():
	global stream
	if stream is not None:
		stream.disconnect()
		stream = None

# Start Stream function
def startStream(track):
	global stream
	global index

	# Generate a random index name
	index = 'gimme-' + str(int(time.time())) + str(random.randint(1000000, 9999999))

	# Create index with the settings defined in config.py
	es.indices.create(index=index, body=config.es["index_settings"])

	# Init the Twitter connection with the auth keys and connect to the filter stream API
	stream = tweepy.Stream(auth, StdOutListener())
	stream.filter(track=[track], async=True)


# Server application
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/tweetsocket", StreamHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)

# Main
if __name__ == '__main__':
	try:
		tornado.options.parse_command_line()
		app = Application()
		app.listen(options.port)
		tornado.ioloop.IOLoop.instance().start()
	except KeyboardInterrupt:
		os._exit(0)
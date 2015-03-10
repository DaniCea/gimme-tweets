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

# Listener responsible to receive the data from Twitter and sent it to the Stream Handler
class StdOutListener(tweepy.StreamListener):
	def on_data(self, data):
		# Send tweet to the client
		StreamHandler.send_tweet(data)

		# Switch lat/lon if geo coordinates are present
		doc = tornado.escape.json_decode(data)
		if doc["geo"] is not None:
			lat = doc["geo"]["coordinates"][1]
			lon = doc["geo"]["coordinates"][0]

			doc["geo"]["coordinates"][0] = lat
			doc["geo"]["coordinates"][1] = lon

		es.storeTweet(doc["id_str"], doc)

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


class ElasticsearchHandler():
	def __init__(self):
		if config.es["active"]:
			self.es = Elasticsearch([config.es["server"]])
		else:
			self.es = False

	def newIndex(self):
		if config.es["active"]:
			# Generate a random index name
			self.index = 'gimme-' + str(int(time.time())) + str(random.randint(1000000, 9999999))
			# Create index with the settings defined in config.py
			self.es.indices.create(index=self.index, body=config.es["index_settings"])

	def storeTweet(self, id, tweet):
		if config.es["active"]:
			# Store tweet in ES
			self.es.index(index=self.index, doc_type='tweet', id=id, body=tweet)





# Web Server port to listen
define("port", default=config.port, help="run on the given port", type=int)

# ElasticSearch Handler instance
es = ElasticsearchHandler()

# Tweepy config
auth = tweepy.OAuthHandler(config.twitter["consumer_key"], config.twitter["consumer_secret"])
auth.set_access_token(config.twitter["access_token"], config.twitter["access_token_secret"])

# Global variables
stream = None
track = None


# Stop Stream function
def stopStream():
	global stream
	if stream is not None:
		stream.disconnect()
		stream = None

# Start Stream function
def startStream(track):
	global stream
	es.newIndex()

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
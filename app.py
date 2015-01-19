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

from tornado.concurrent import Future
from tornado import gen
from tornado.options import define, options, parse_command_line

# Web Server port to listen
define("port", default=5000, help="run on the given port", type=int)

# Twitter authentication details
consumer_key = 'QULl7GNb5JKzwKznevMZmQ'
consumer_secret = 'tKbUP8DqcjjYgl9Ih0sIt6TNPebTNdgkCoWJ0qfW9Sc'
access_token = '2353070090-LjkVD41lVcR8dqNb2gg29IIFqpySSYHmgioEB0D'
access_token_secret = 'VoZS0ENHbtgNhVTvvWgaMAp4Nsc2grcdhXGkP91VSSML5'

# Tweepy config
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Global variables
stream = None
track = None

# Listener responsible to receive the data from Twitter and sent it to the Stream Handler
class StdOutListener(tweepy.StreamListener):
	def on_data(self, data):
		print 'New tweet'
		StreamHandler.send_tweet(data)

	def on_error(self, status):
		print status


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


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
	stream = tweepy.Stream(auth, StdOutListener())
	stream.filter(track=[track], async=True)

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


def main():
	tornado.options.parse_command_line()
	app = Application()
	app.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		os._exit(0)
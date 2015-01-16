from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit

import os
import tweepy
import json

# Variable that holds the running stream
stream = None
track = None

# This is the listener, resposible for receiving data
class StdOutListener(tweepy.StreamListener):
    def on_data(self, data):
        # Twitter returns data in JSON format - we need to decode it first
        decoded = json.loads(data)
        print 'New tweet'
        socketio.emit('tweet', decoded, namespace='/tweets');

    def on_error(self, status):
        print status

# Twitter authentication details
consumer_key = 'QULl7GNb5JKzwKznevMZmQ'
consumer_secret = 'tKbUP8DqcjjYgl9Ih0sIt6TNPebTNdgkCoWJ0qfW9Sc'
access_token = '2353070090-LjkVD41lVcR8dqNb2gg29IIFqpySSYHmgioEB0D'
access_token_secret = 'VoZS0ENHbtgNhVTvvWgaMAp4Nsc2grcdhXGkP91VSSML5'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Tweepy config
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Stop Stream function
def stopStream():
	global stream
	if stream is not None:
		stream.disconnect()
		stream = None

def startStream(track):
	global stream
	stream = tweepy.Stream(auth, StdOutListener())
	stream.filter(track=[track], async=True)

# Route definition
@app.route('/')
def index():
	return render_template('index.html')

# Socket.io messages and responses
@socketio.on('start', namespace='/tweets')
def start(message):
	print 'New Stream received'
	global track
	track = message
	startStream(track)
	emit('start-ack')

@socketio.on('stop', namespace='/tweets')
def stop():
	print 'Stop Stream received'
	stopStream()
	emit('stop-ack')

@socketio.on('pause', namespace='/tweets')
def pause():
	print 'Pause Stream received'
	stopStream()
	emit('pause-ack')

@socketio.on('resume', namespace='/tweets')
def resume():
	print 'Resume Stream received'
	global track
	startStream(track)
	emit('resume-ack')


@socketio.on('connect', namespace='/tweets')
def connect():
    print 'Client connected'
    stopStream()

@socketio.on('disconnect', namespace='/tweets')
def disconnect():
	print 'Client disconnected'
	stopStream()

if __name__ == '__main__':
	try:
		socketio.run(app)
	except KeyboardInterrupt:
		os._exit(0)
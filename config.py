# Twitter settings
twitter = {
	"consumer_key": 'QULl7GNb5JKzwKznevMZmQ',
	"consumer_secret": 'tKbUP8DqcjjYgl9Ih0sIt6TNPebTNdgkCoWJ0qfW9Sc',
	"access_token": '2353070090-LjkVD41lVcR8dqNb2gg29IIFqpySSYHmgioEB0D',
	"access_token_secret": 'VoZS0ENHbtgNhVTvvWgaMAp4Nsc2grcdhXGkP91VSSML5'	
}

# ElasticSearch settings
es = {
	"active": True,
	"server": 'http://minerva.bsc.es:8089',
	"index_settings": {
	    "mappings" : {
		    "tweet": {
		        "_timestamp": {
		            "enabled": True,
		            "store": True,
		            "index": "analyzed"
		        },
		        "_index": {
		            "enabled": True,
		            "store": True,
		            "index": "analyzed"
		        }
		    }
	    }	
	}
}

# Server settings
port = 5000
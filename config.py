# Twitter settings
twitter = {
	"consumer_key": 'INSERT_CONSUMER_KEY_HERE',
	"consumer_secret": 'INSERT_CONSUMER_SECRET_HERE',
	"access_token": 'INSERT_ACCESS_TOKEN_HERE',
	"access_token_secret": 'INSERT_ACCESS_TOKEN_SECRET_HERE'	
}

# ElasticSearch settings
es = {
	"server": 'INSERT_ELASTICSEARCH_URL_HERE',
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
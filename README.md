Gimme-tweets is a simple web server written in Python to obtain tweets about a topic in real-time and store them in Elasticsearch (optional)

To get it running:



· Clone the repository

· Install the requirements:

	pip install -r requirements.txt

· Edit the config.py with your Twitter keys and, if you want to store tweets in ElasticSearch, set it to the URL of your ES instance (generally http://localhost:9200) and set "active" to True

· Run the server:

	python app.py



The default port is set to 5000, so the server should be accesible using the following url:

http://localhost:5000
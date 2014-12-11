# In this file we connec to the database
import pyorient
# init a connection to the database

def connect():
	client = pyorient.OrientDB("localhost", 2424)
	session_id = client.connect( "root", "root" )
	client.db_open( "moviesDB", "admin", "admin")
	return client

import requests
import psycopg2
from datetime import datetime
import secrets_1

#connect to database 
conn = psycopg2.connect(
    host=secrets_1.host,
    database=secrets_1.database,
    user=secrets_1.user,
    password=secrets_1.password)

cur = conn.cursor()

#Check database for latest refresh token.
cur.execute("SELECT Refresh_token FROM tokens ORDER BY Expires_at DESC LIMIT 1")
refresh_token = cur.fetchone()
print("refresh_token: " + refresh_token[0])

#Strava API Authentication 
params = {
    "client_id":secrets_1.client_id,
    "client_secret":secrets_1.client_secret,
    "grant_type":"refresh_token",
    "refresh_token":refresh_token[0]
}
url = "https://www.strava.com/api/v3/oauth/token"

#Exchanging refresh token for latest access token
response = requests.post(url, data=params)

#Returned values
new_access_token = response.json()['access_token']
expires_at = response.json()['expires_at']
new_refresh_token = response.json()['refresh_token']
print(response)
print("new access_token: " + new_access_token, "expires_at: " + str(expires_at), "refresh_token: " + str(new_refresh_token[0]))

#Send info to database
cur.execute("Insert into tokens (access_token, expires_at, refresh_token) VALUES (%s, %s, %s)", (new_access_token, expires_at, new_refresh_token))
conn.commit()

#Check database for latest access token.  
cur.execute("SELECT Access_token FROM tokens ORDER BY Expires_at DESC LIMIT 1")
access_token = cur.fetchone()
print("latest access token has been fetched from database: " + access_token[0])

#Use access token to pull recent Strava activities
my_headers = {'Authorization' : 'Bearer ' + access_token[0]}
response = requests.get ("https://www.strava.com/api/v3/activities/7600292122", headers=my_headers)
print(response.json())

cur.execute("Insert into activities (name, distance, moving_time, total_elevation_gain, sport_type, id, start_date, map, average_speed) \
    values (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
    (response.json()['name'],
        round((response.json()['distance'])/1609,2), #convert distance from meters to miles, rounded to 2 decimal places
        response.json()['moving_time'],
        response.json()['total_elevation_gain'], 
        response.json()['sport_type'],
        response.json()['id'],
        response.json()['start_date'],
        response.json()['map']['summary_polyline'],  
        response.json()['average_speed'],
        ))
conn.commit()

#closing database connection
cur.close()
conn.close()
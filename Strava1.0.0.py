import requests
import psycopg2

#connect to database 
conn = psycopg2.connect(
    host="XXX",
    database="XXX",
    user="XXX",
    password="XXX")

cur = conn.cursor()

#Check database for latest refresh token.
cur.execute("SELECT Refresh_token FROM tokens ORDER BY Expires_at DESC LIMIT 1")
refresh_token = cur.fetchone()
print("refresh_token: " + refresh_token[0])

#Strava API Authentication 
params = {
    "client_id":"XXX",
    "client_secret":"XXX",
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
print(new_access_token, expires_at, refresh_token)

#Send info to database
cur.execute("Insert into tokens (access_token, expires_at, refresh_token) VALUES (%s, %s, %s)", (new_access_token, expires_at, new_refresh_token))
conn.commit()

#Check database for latest access token.  
cur.execute("SELECT Access_token FROM tokens ORDER BY Expires_at DESC LIMIT 1")
access_token = cur.fetchone()
print("access_token: " + access_token[0])

#Use access token to pull recent Strava activities
my_headers = {'Authorization' : 'Bearer ' + access_token[0]}
response = requests.get ("https://www.strava.com/api/v3/athlete/activities?per_page=3", headers=my_headers)

print (response)
#print (response.text)

#closing database connection
cur.close()
conn.close()
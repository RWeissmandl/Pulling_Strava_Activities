import requests
import psycopg2
from datetime import datetime, timedelta 
import polyline
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
response = requests.get ("https://www.strava.com/api/v3/athlete/activities?per_page=200", headers=my_headers)

#Check db for latest activity date to only insert activities that are later than activites in db - avoids duplication
cur.execute("select start_date from activities order by start_date desc limit 1")
db_latest_activity_date = cur.fetchone()
strava_date_format = '%Y-%m-%dT%H:%M:%SZ'

#Looping through each activity
for x in range(len(response.json())):
    
    #compare dates of current activitites to db date
    strava_activity_date = response.json()[x]['start_date'] 
    strava_activity_datetime_format = datetime.strptime(strava_activity_date, strava_date_format).date()
    
    if strava_activity_datetime_format > db_latest_activity_date[0]: 
        #storing map as variable to trim in loop:
        if response.json()[x]['map']['summary_polyline'] != "":
            map = response.json()[x]['map']['summary_polyline']
            trimmed_map = polyline.decode(map)[12:-12]
            trimmed_encoded_map = polyline.encode(trimmed_map)

        cur.execute("Insert into activities (name, distance, moving_time, total_elevation_gain, sport_type, id, start_date, map, average_speed) \
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
            (response.json()[x]['name'],
             round((response.json()[x]['distance'])/1609,2), #convert distance from meters to miles, rounded to 2 decimal places
            str(timedelta(seconds = response.json()[x]['moving_time'])), #convert seconds to HMS
            round((response.json()[x]['total_elevation_gain'])*3.28084), #convert meters to feet
             response.json()[x]['sport_type'],
             response.json()[x]['id'],
             response.json()[x]['start_date'],
             trimmed_encoded_map,  
             round(response.json()[x]['average_speed']*2.23694, 1), #convert seconds/meter to mins/mile
             ))
conn.commit()

#closing database connection
cur.close()
conn.close()
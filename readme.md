This code gets latest activities from Strava and sends to a PostgreSQL database.

1: Connect to Strava's API. Strava uses OAuth2 for authentication. Once a one-time refresh token is gained (for more info: https://developers.strava.com/docs/getting-started/), a short-lived access-token can be aquired. Each time an access token is gained, the refresh token may update with only the latest refresh token valid. Therefore, all tokens are stored in a PostgreSQL database using the psycopg2 library to connect. 

2: Specified data from activities are sent to PostgreSQL. To avoid duplication, it first checks the latest date already in the database, and only sends activities later than said date. 
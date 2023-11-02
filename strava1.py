import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

swagger_client.configuration.access_token = '3a786515e153f2f97ac60c1e27d3cd8ce7990ab5'
api_instance = swagger_client.ActivitesApi ()
id = 9855413708
includeAllEfforts = True

try:
    api_response = api_instance.getActivityById(id, includeAllEfforts=includeAllEfforts)
    pprint(api_response)
except ApiException as e:
    print ("Exception when calling ActivitiesApi->getActivityById: %s\n" % e)
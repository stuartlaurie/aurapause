import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from argparse import ArgumentParser
from tqdm import tqdm
import sys

auraendpoint = "https://api.neo4j.io/v1/instances"

########################################
##  SETUP command line arguments
########################################

parser = ArgumentParser(prog='aurapause.py',
                    description='Lists and pauses Neo4j Aura instances',)
parser.add_argument("-c", "--credentials", dest="credfile",
                    help="file containing aura API credentials")
parser.add_argument("-p", "--pause", dest="pause", default="",
                    help="whether to pause instance, ALL or comma separated list of ids")
parser.add_argument("-e", "--exclude", dest="exclude", default="", 
                    help="instances to exclude from pause, comma separated list of ids")
parser.add_argument("-t", "--tenant", dest="tenant", default="", 
                    help="tenant id, filter only to dbs in specified tenant")
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)

args = parser.parse_args()

########################################
##  READ CREDS AND AUTHENTICATE
########################################

## Read aura credentials
config = {}
with open(args.credfile, "r") as configs:
    for line in configs:
        line = line.strip()
        name, var = line.partition("=")[::2]
        config[name.strip()] = str(var)

## Make the request to the Aura API Auth endpoint
print ("Authorizing.. ")
response = requests.request(
    "POST",
    "https://api.neo4j.io/oauth/token",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={"grant_type": "client_credentials"},
    auth=HTTPBasicAuth(config['CLIENT_ID'], config['CLIENT_SECRET'])
)

API_Data = response.json()
# print (API_Data['access_token'])
## set auth header
headers = {"Authorization": "Bearer "+API_Data['access_token'], "Content-Type": "application/json"}

########################################
##  GET INSTANCE LIST
########################################

print ("Getting list of instances.. ")
instances = requests.get(auraendpoint,headers=headers).json()
instancelistdf=pd.DataFrame(instances['data'])
if args.tenant != "":
    if args.tenant in instancelistdf['tenant_id'].values:
        instancelistdf = instancelistdf.loc[instancelistdf['tenant_id'] == args.tenant]
    else:
        ## TODO: could also use the tenant API endpoint to validate if exists
        print("No databases found for tenant: " + args.tenant)
        exit()

print ("Found " + str(len(instancelistdf)) + " databases")

########################################
##  GET DB DETAILS/STATUS
########################################

print ("Getting instance details.. ")
instancedetails=[]

for dbid in tqdm(instancelistdf['id']):
    instanceendpoint = auraendpoint+"/"+dbid
    instancedetail = requests.get(instanceendpoint,headers=headers).json()
    instancedetails.append(instancedetail['data'])

########################################
##  SHOW DBs
########################################

print ("Running Instances:")
instancedf = pd.DataFrame(instancedetails)
## get rid of ..GB and make int for correct sort
## when paused we don't get memory/storage info so add empty columns
if 'memory' in instancedf:
    instancedf["memoryint"] = instancedf.memory.str[:-2]
    instancedf["memoryint"] = instancedf["memoryint"].replace('NaN', pd.NA).fillna(0).astype(int)
    instancedf.sort_values(by=['status', 'memoryint'],ascending=[False,False],inplace=True)
else:
    instancedf["memory"]='NaN'
if 'storage' not in instancedf:
    instancedf["storage"]='NaN'

print (instancedf[['tenant_id','name','id','status','memory','storage','cloud_provider','region']])


########################################
##  PAUSING
########################################

def pause_db(pause_list):
    for dbid in pause_list:
        print ("Attempting to pause db with ID(s): " + dbid)
        pauseendpoint = auraendpoint+"/"+dbid+"/pause"
        pausedetail = requests.post(pauseendpoint,headers=headers).json()
        print(pausedetail)

## Check to see if we want to pause any
pause_list=[]
if args.pause != "":
    if args.pause == "ALL":
        print ("Pausing all running DBs..")
        pause_list=instancedf.loc[instancedf['status'] == 'running', 'id'].tolist()
        if args.exclude != "":
            exclude_list = args.exclude.split(",")
            print ("Excluding DB ids: " + ','.join(exclude_list))
            for exclude_db in exclude_list:
                if exclude_db in pause_list:
                    pause_list.remove(exclude_db)
                else:
                    print ("Warning: " + exclude_db + " Not found in list of databases")
    else:
        print ("Pausing: "+args.pause)
        pause_list = args.pause.split(",")
    #print(pause_list)
    pause_db(pause_list)


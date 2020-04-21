import json
import re
import redis
import requests
from ratelimit import limits, sleep_and_retry

ipmap = {}

redisDb = redis.Redis(
    host='localhost',
    port=6379, 
    password='')

@sleep_and_retry
@limits(calls=1, period=5)
def fetchNewIpData(ip):
    response = requests.get("https://tools.keycdn.com/geo.json?host=" + ip)
    ipmap[ip] = response.json()["data"]
    redisDb.set(ip, json.dumps(ipmap[ip]))

if __name__ == "__main__":
    with open('sample.log','r') as logFile:
        failedPattern = re.compile('Failed password for .* from [0-9]*[.][0-9]*[.][0-9]*[.][0-9]* ')
        ipPattern = re.compile('[0-9]*[.][0-9]*[.][0-9]*[.][0-9]*')

        for line in logFile:
            lineResult = failedPattern.search(line)
            if lineResult != None:
                ip = ipPattern.search(lineResult.group(0)).group(0)
                if (redisDb.get(ip) is None):
                    print("New ip " + ip)
                    fetchNewIpData(ip)
                else:
                    ipData = json.loads(redisDb.get(ip))
                    print("{} {}".format(ipData['geo']['latitude'], ipData['geo']['latitude']))
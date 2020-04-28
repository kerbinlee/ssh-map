import json
import re
import redis
import requests
from datetime import date, datetime
from ratelimit import limits, sleep_and_retry

class IpData:
    @sleep_and_retry
    @limits(calls=1, period=5)
    def fetchNewIpData(self, ip):
        response = requests.get("https://tools.keycdn.com/geo.json?host=" + ip)
        self.ipmap[ip] = response.json()["data"]["geo"]
        self.redisDb.set("ipdata:" + ip, json.dumps(self.ipmap[ip]))

    def getIpTimes(self, ip):
        data = self.redisDb.lrange('iptimes:' + ip, 0, -1)
        return data

    def __init__(self):
        self.ipmap = {}
        self.redisDb = redis.Redis(
            host='localhost',
            port=6379, 
            password='',
            charset='utf-8',
            decode_responses=True)

        with open('auth.log','r') as logFile:
            failedPattern = re.compile('.* Failed password for .* from [0-9]*[.][0-9]*[.][0-9]*[.][0-9]* ')
            datePattern = re.compile('^[A-Z][a-z]* [0-9]* [0-9:]*')
            ipPattern = re.compile('[0-9]*[.][0-9]*[.][0-9]*[.][0-9]*')

            for line in logFile:
                lineResult = failedPattern.search(line)
                if lineResult != None:
                    dateStr = datePattern.search(lineResult.group(0)).group(0)
                    ipDate = datetime.strptime(dateStr, '%b %d %H:%M:%S').replace(year=date.today().year)
                    ip = ipPattern.search(lineResult.group(0)).group(0)
                    if (self.redisDb.get("ipdata:" + ip) is None):
                        print("New ip " + ip)
                        self.fetchNewIpData(ip)
                    else:
                        ipData = json.loads(self.redisDb.get("ipdata:" + ip))
                        print("{} {}".format(ipData['latitude'], ipData['latitude']))
                        self.ipmap[ip] = ipData
                    # self.redisDb.rpush('iptimes:' + ip, ipDate.timestamp())
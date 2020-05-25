import glob
import gzip
import json
import re
import redis
import requests
from datetime import date, datetime
from pathlib import Path
from ratelimit import limits, sleep_and_retry

class IpData:
    @sleep_and_retry
    @limits(calls=1, period=2)
    def fetchNewIpData(self, ip):
        response = requests.get("https://tools.keycdn.com/geo.json?host=" + ip)
        self.ipmap[ip] = response.json()["data"]["geo"]
        self.redisDb.set("ipdata:" + ip, json.dumps(self.ipmap[ip]))

    def getIpTimes(self, ip):
        dataList = self.redisDb.zrange('iptimes:' + ip, 0, -1)
        returnData = []
        for data in dataList:
            returnData.append(json.loads(data))
        return returnData

    def __init__(self):
        self.ipmap = {}
        self.redisDb = redis.Redis(
            host='localhost',
            port=6379, 
            password='',
            charset='utf-8',
            decode_responses=True)

        authLogs=glob.glob('auth.log.*.gz')
        authLogs.sort(reverse = True)
        
        latestParsedEntryTime = None
        latestDbTime = self.redisDb.get("lastLogTime")

        for authLog in authLogs:
            print("Processing file {}".format(authLog))
            with gzip.open(authLog, 'rt') as logFile:
                latestParsedEntryTime = self.processLogFile(logFile, latestDbTime, latestParsedEntryTime)

        if Path('auth.log').exists():
            with open('auth.log','r') as logFile:
                print("Processing file auth.log")
                latestParsedEntryTime = self.processLogFile(logFile, latestDbTime, latestParsedEntryTime)

        matched_pairs = self.redisDb.scan_iter(match='ipdata:*')
        for keyvalue in matched_pairs:
            ip = keyvalue.split(':')[1]
            ipData = json.loads(self.redisDb.get(keyvalue))
            self.ipmap[ip] = ipData

        if (latestParsedEntryTime is not None and latestDbTime is not None and latestParsedEntryTime > float(latestDbTime)):
            print("setting lastLogTime of {}".format(latestParsedEntryTime))
            self.redisDb.set("lastLogTime", latestParsedEntryTime)

    def processLogFile(self, logFile, latestDbTime, latestParsedEntryTime):
        failedPattern = re.compile('.* Failed password for .* from [0-9]*[.][0-9]*[.][0-9]*[.][0-9]* ')
        datePattern = re.compile('^[A-Z][a-z]*[ ]+[0-9]*[ ]+[0-9:]*')
        ipPattern = re.compile('[0-9]*[.][0-9]*[.][0-9]*[.][0-9]*')
        userPattern = re.compile('Failed password for (invalid user )?')

        lastParsedEntryTime = None
        for line in logFile:
            lineResult = failedPattern.search(line)
            if lineResult != None:
                dateStr = datePattern.search(lineResult.group(0)).group(0)
                ipDate = datetime.strptime(dateStr, '%b %d %H:%M:%S').replace(year=date.today().year)
                lastParsedEntryTime = ipDate.timestamp()
                ip = ipPattern.search(lineResult.group(0)).group(0)
                user = userPattern.split(lineResult.group(0))[2].split()[0]
                if (latestDbTime is None or float(latestDbTime) < ipDate.timestamp()):
                    if (self.redisDb.get("ipdata:" + ip) is None):
                        print("New ip " + ip)
                        self.fetchNewIpData(ip)
                    self.redisDb.zadd('iptimes:' + ip, {json.dumps({'time': ipDate.timestamp(), 'user': user}): ipDate.timestamp()})
        if latestParsedEntryTime is None or (lastParsedEntryTime is not None and lastParsedEntryTime > latestParsedEntryTime):
            latestParsedEntryTime = lastParsedEntryTime
        return latestParsedEntryTime
                    
#!/usr/bin/python
"""Dynamic DNS update script for Google Domains
"""
import requests
import json
from datetime import datetime
from sys import exit
from socket import gethostbyname


CONFFILE = 'dyndns-google.conf'
LOGFILE = 'dyndns-google.log'

def getCurrentIP():
    try:
        response = requests.get('http://jsonip.com')
        ip = json.loads(response.text)['ip']
    except:
        ip = None
    return ip

def getCurrentDNS(hostname):
    try:
        ip = gethostbyname(hostname)
    except:
        ip = None
    return ip

def getConfigItems(path=CONFFILE):
    with open(path) as f:
        conf = json.load(f)
    return conf

def updateConfigItems(config, path=CONFFILE):
    with open(path, 'w') as f:
        f.write(json.dumps(config, sort_keys=True, indent=2))

def writeLog(event, path=LOGFILE):
    with open(path, 'a') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = '{t} {e}\n'.format(t=timestamp, e=event)
        f.write(line)

def updateGoogleDNS(conf):
    baseurl = 'domains.google.com/nic/update'
    url = 'https://{u}:{p}@{b}?hostname={h}&myip={i}'.format(
        u=conf['username'],
        p=conf['password'],
        b=baseurl,
        h=conf['hostname'],
        i=conf['ipaddress'])
    headers = {'User-Agent':'Chrome/41.0'}
    response = requests.post(url, headers=headers)
    return response

conf = getConfigItems()
currentIP = getCurrentIP()
print('Current IP : {}'.format(currentIP))
currentDNS = getCurrentDNS(conf['hostname'])
print('Current DNS: {}'.format(currentDNS))

if currentIP == currentDNS:
    print('Current and Previous match')
    event = 'NO CHANGE: IP={}'.format(currentIP)
else:
    print('Current and Previous are different')
    print('Updating Google DNS...')
    conf['ipaddress'] = currentIP
    response = updateGoogleDNS(conf)
    print(response)
    print(response.text)
    if response.ok:
        event = 'UPDATED: IP={}, STATUS={}, REPLY="{}"'.format(currentIP, str(response.status_code), response.text)
    else:
        event = 'ERROR: IP={}, STATUS={}, REPLY="{}"'.format(currentIP, str(response.status_code), response.text)
writeLog(event)

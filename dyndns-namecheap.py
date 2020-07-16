#!/usr/bin/python
"""Dynamic DNS update script for NameCheap Domains
Client doc: https://www.namecheap.com/support/knowledgebase/article.aspx/5/11/are-there-any-alternate-dynamic-dns-clients
HTTP doc: https://www.namecheap.com/support/knowledgebase/article.aspx/29/11/how-do-i-use-a-browser-to-dynamically-update-the-hosts-ip
"""
import argparse
import requests
import json
from datetime import datetime
from sys import exit
from socket import gethostbyname


CONFFILE = 'dyndns.conf'
LOGFILE = 'dyndns.log'

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

def getConfigItems(path=None):
    if path is None:
        path = CONFFILE
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

def updateNameCheapDNS(conf):
    url = 'https://dynamicdns.park-your-domain.com/update'
    # ?host=[host]&domain=[domain_name]&password=[ddns_password]&ip=[your_ip]'
    params = {
        'host': conf['hostname'],
        'domain': conf['domain'],
        'password': conf['password'],
        'ip': conf['ipaddress']
    }
    headers = {'User-Agent':'Chrome/41.0'}
    response = requests.get(url, headers=headers, params=params)
    return response


parser = argparse.ArgumentParser()
parser.add_argument('--config', help='Alternate dyndns.conf filepath')
args = parser.parse_args()


conf_list = getConfigItems(args.config)
currentIP = getCurrentIP()
print('Current IP : {}'.format(currentIP))
for conf in conf_list:
    currentDNS = getCurrentDNS(conf['hostname'])
    print('Current DNS: {}'.format(currentDNS))

    if currentIP == currentDNS:
        print('Current and Previous match')
        event = 'NO CHANGE: IP={}'.format(currentIP)
    else:
        print('Current and Previous are different')
        print('Updating NameCheap DNS...')
        conf['ipaddress'] = currentIP
        response = updateNameCheapDNS(conf)
        print(response)
        print(response.text)
        if response.ok:
            event = 'UPDATED: IP={}, STATUS={}, REPLY="{}"'.format(currentIP, str(response.status_code), response.text)
        else:
            event = 'ERROR: IP={}, STATUS={}, REPLY="{}"'.format(currentIP, str(response.status_code), response.text)
    writeLog(event)

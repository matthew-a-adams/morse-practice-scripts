#!/usr/bin/env python3

import requests
import re

# Get redirect URL
r = requests.get('https://www.qrz.com/random-callsign')
print(r.url)
callsign = r.url.split('/')[4]
print('CALL: '+callsign)

## Get page source
#page = requests.get(r.url)
##print (page.text.encode('utf8'))
#
#lines = page.text.split('\n')
#for line in lines:
#    if search(callsign, line):
#        print(line)

session = requests.get('https://xmldata.qrz.com/xml/current/?username=kd2wai&password=clP@84JooqSL')
lines = session.text.split('\n')
for line in lines:
    if re.search('Key',line):
        p = re.compile('<[/]*Key>')
        key = p.sub('', line)
        #print('KEY: '+ key)
    if re.search('Count',line):
        p = re.compile('<[/]*Count>')
        count = p.sub('', line)
        #print('COUNT: '+ count)

hampage = requests.get('http://xmldata.qrz.com/xml/current/?s='+key+'&callsign='+callsign)
lines = hampage.text.split('\n')
for line in lines:
    if re.search('fname',line):
        p = re.compile('<[/]*fname>')
        name = p.sub('', line)
        fname = name.split(' ')[0]
        print('NAME: '+ fname)
    if re.search('addr2', line):
        p = re.compile('<[/]*addr2>')
        city = p.sub('', line)
        print('CITY_orig: '+city)
        q = re.compile('\d+')
        citystr = q.sub('', city)
        print('CITY: '+citystr)
    if re.search('state', line):
        p = re.compile('<[/]*state>')
        state = p.sub('', line)
        print('STATE: '+state)
    if re.search('country', line):
        p = re.compile('<[/]*country>')
        country = p.sub('', line)
        print('COUNTRY: '+country)

print('http://xmldata.qrz.com/xml/current/?s='+key+'&callsign='+callsign)
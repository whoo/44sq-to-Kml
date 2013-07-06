#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Dominique DERRIER <d.derrier@linkbynet.com>
#
# This file is part of 44sq-to-Kml.
# 
# 44sq-to-Kml is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# 44sq-to-Kml is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with 44sq-to-Kml.  If not, see <http://www.gnu.org/licenses/>
# 

import foursquare
from lxml import etree
import lxml.builder as lb
import pickle
import os
import datetime

try:
    import cred
except ImportError:
    print "Please create a creds.py file in this package, based upon cred.example.py"


TOKEN_FILE='token_file.key'
CONSUMER_KEY 	= cred.CONSUMER_KEY
CONSUMER_SECRET  = cred.CONSUMER_SECRET
URL_CALLBACK= cred.URL_CALLBACK
TOKEN=''

""" Load file """
if (os.path.exists(TOKEN_FILE)):  
	vfile = open(TOKEN_FILE,'r');
	keys=pickle.load(vfile)
	TOKEN=keys

if (TOKEN==''):
	""" Get token with Oauth"""
	Api = foursquare.Foursquare(client_id=CONSUMER_KEY,client_secret=CONSUMER_SECRET,redirect_uri=URL_CALLBACK)
	auth_url = Api.oauth.auth_url()
	print 'Please authorize: ' + auth_url
	code = raw_input('The code: ').strip()
	access_token = Api.oauth.get_token(code)
	print 'Your access token is ' + access_token
	keys=(access_token)
	vfile=open(TOKEN_FILE,'w+')
	pickle.dump(keys,vfile)
	vfile.close()
	Api.set_access_token(access_token)
else:	
	Api= foursquare.Foursquare(client_id=CONSUMER_KEY,client_secret=CONSUMER_SECRET,
		access_token=TOKEN)



root = lb.E.kml(xmlns="http://www.opengis.net/kml/2.2")
document=lb.E.Document(
lb.E.Style(lb.E.IconStyle(lb.E.Icon(lb.E.href('http://maps.google.com/mapfiles/kml/paddle/red-blank.png'))),id='red'),
lb.E.Style(lb.E.IconStyle(lb.E.Icon(lb.E.href('http://maps.google.com/mapfiles/kml/paddle/blue-blank.png'))),id='blue'))
root.append(document)

folder={}

for checkin in Api.users.all_checkins():
	if ('venue' in checkin ):
		categorie=" "
		icon="https://playfoursquare.s3.amazonaws.com/press/logo/icon-36x36.png"
		if  len(checkin['venue']['categories']):
			""" Avoid empty fields """
			categorie = checkin['venue']['categories'][0]['name']
			icon= checkin['venue']['categories'][0]['icon']['prefix'][:-1]+checkin['venue']['categories'][0]['icon']['suffix']
		name=checkin['venue']['name']
		url=checkin['venue']['canonicalUrl']
		if ('country' in checkin['venue']['location']):
			""" Avoid empty fields"""
			country=checkin['venue']['location']['country']
			if ('city' in checkin['venue']['location']):
				 city=checkin['venue']['location']['city'] 

		if not (country in folder):
			folder[country]=lb.E.Folder(lb.E.name(country),lb.E.description('4sq data in %s'%(country)))
		
		date=datetime.date.fromtimestamp(checkin['createdAt'])

		data={'icon':icon,
		'categorie':categorie,
		'city':city,
		'country':country,
		'url':url,
		'date':date}

		desc		="<img src=%(icon)s> %(categorie)s in %(city)s <br>%(country)s<br>Le %(date)s <a href='%(url)s'>Go</a>"%(data)
		coordinates	="%s,%s,0"%(checkin['venue']['location']['lng'],checkin['venue']['location']['lat'])

		place=lb.E.Placemark(lb.E.name(name),lb.E.styleUrl('#red'),lb.E.description(desc),
			lb.E.Point(lb.E.coordinates(coordinates)))
		folder[country].append(place)

for key in folder:
	document.append(folder[key])

print etree.tostring(root,pretty_print=True)

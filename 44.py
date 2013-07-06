#!/usr/bin/env python
# -*- coding: utf-8 -*-


import foursquare
from lxml import etree
import lxml.builder as lb
import cgi
import pickle
import os
import datetime


CONSUMER_KEY = "XGBX3TG3XCTSABJVGDXXVY0AT2Z00ZEFMBDOTRDVSNMEKKAA"
CONSUMER_SECRET  = "2OZOJGADK5WP4Z1BWXHEX53CJGIYIXHCN0Y03W2PA4IS1T50"
TOKEN=''

if (os.path.exists('dd.dmp')):  
	vfile = open('dd.dmp','r');
	keys=pickle.load(vfile)
	TOKEN=keys

if (TOKEN==''):
	Api = foursquare.Foursquare(client_id=CONSUMER_KEY,client_secret=CONSUMER_SECRET,redirect_uri='http://blog.nasa.fr/')
	auth_url = Api.oauth.auth_url()
	print 'Please authorize: ' + auth_url
	code = raw_input('The code: ').strip()
	print code
	access_token = Api.oauth.get_token(code)
	print 'Your access token is ' + access_token
	keys=(access_token)
	vfile=open('dd.dmp','w+')
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

f={}

for a in Api.users.all_checkins():
	if ('venue' in a ):
		pict=categorie=" "
		pict="https://playfoursquare.s3.amazonaws.com/press/logo/icon-36x36.png"
		if  len(a['venue']['categories']):
			categorie = a['venue']['categories'][0]['name']
			pict= a['venue']['categories'][0]['icon']['prefix'][:-1]+a['venue']['categories'][0]['icon']['suffix']
		name=a['venue']['name']
		lat=a['venue']['location']['lat']
		lng=a['venue']['location']['lng']
		url=a['venue']['canonicalUrl']
		if ('country' in a['venue']['location']):
			country=a['venue']['location']['country']
			if ('city' in a['venue']['location']):
				 city=a['venue']['location']['city'] 
#		print "%s (%s):%s:%s:%s"%(name,categorie,country,lat,lng)

		if not (country in f):
			f[country]=lb.E.Folder(lb.E.name(country),lb.E.description('Foursquare data in %s'%(country)))
		
		ll="%s,%s,0"%(lng,lat)
		date=datetime.date.fromtimestamp(a['createdAt'])

		data={'pict':pict,'categorie':categorie,'city':city,'country':country,'url':url,'date':date}
		desc="<img src=%(pict)s> %(categorie)s in %(city)s <br>%(country)s<br>Le %(date)s <a href='%(url)s'>Go</a>"%(data)
		place=lb.E.Placemark(lb.E.name(name),lb.E.styleUrl('#red'),lb.E.description(desc),
			lb.E.Point(lb.E.coordinates(ll)))
		f[country].append(place)

for a in f:
	document.append(f[a])

print etree.tostring(root,pretty_print=True)

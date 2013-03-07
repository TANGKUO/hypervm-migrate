#!/usr/bin/env python
from collections import OrderedDict
import csv

reader = csv.reader(open("input.csv", "r"))
sorted_list = {}

locations = {
	"IL": ["64.79.106.219", "64.79.106.220", "64.79.106.221"],
	"CA": ["nitrogen.bluevm.com", "oxygen.bluevm.com", "phosphorus.bluevm.com", "carbon.bluevm.com", "helium.bluevm.com", "lithium.bluevm.com", "neon.bluevm.com", "argon.bluevm.com"],
	"ATL": ["calcium.bluevm.com", "magnesium.bluevm.com", "silicon.bluevm.com", "sodium.bluevm.com"],
	"TX": ["nickel.bluevm.com"]
}

new_servers = {
	"IL": OrderedDict({12: 1, 34: 1, 56: 1}),
	"CA": OrderedDict({12: 2, 34: 3, 56: 1}),
	"ATL": OrderedDict({12: 1, 34: 2, 56: 1}),
	"TX": OrderedDict({12: 1, 34: 1, 56: 1})
}

new = {}

for location, x in new_servers.iteritems():
	sorted_list[location] = OrderedDict({})
	sorted_list[location][12] = []
	sorted_list[location][34] = []
	sorted_list[location][56] = []

for vps in reader:
	username, vpsid, current, plan = vps
	
	location = ""
	
	for loc, hosts in locations.iteritems():
		if current in hosts:
			location = loc
	
	if location == "":
		print "No location specified for %s" % (repr(vps))
		continue
	
	if "blue1" in plan or "blue2" in plan or "lebletspecial" in plan or "vps1" in plan or "vps2" in plan:
		sorted_list[location][12].append((username, vpsid))
	elif "blue3" in plan or "blue4" in plan or "vps3" in plan or "vps4" in plan:
		sorted_list[location][34].append((username, vpsid))
	elif "blue5" in plan or "blue6" in plan or "presale" in plan or "vps5" in plan or "vps6" in plan:
		sorted_list[location][56].append((username, vpsid))

for location, items in new_servers.iteritems():
	new[location] = OrderedDict({})
	
	for category, count in items.iteritems():
		for i in xrange(0, count):
			new[location][i] = []

for location, items in sorted_list.iteritems():
	current_server = 0
	
	for category, vpses in items.iteritems():
		total_vpses = len(vpses)
		total_servers = new_servers[location][category]
		per_server = total_vpses / total_servers
		
		for i in xrange(0, total_servers):
			start = per_server * i
			end = (per_server * (i + 1)) - 1
			
			if end + 2 >= total_vpses:
				end = total_vpses - 1
			
			current_server += 1	
			hostname = "s%d.c%d.%s.bluevm.com" % (current_server, category, location.lower())
				
			for s in xrange(start, end + 1):
				print "%s,%s,%s" % (vpses[s][0], vpses[s][1], hostname)

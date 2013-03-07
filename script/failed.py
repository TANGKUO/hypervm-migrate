#!/usr/bin/python

import oursql

db = oursql.connect(host="localhost", user="root", passwd="", db="transfer")
c = db.cursor()

c.execute("SELECT * FROM servers")
servers = c.fetchall()

for server in servers:
	if server[2] == 2 or server[2] == 4:
		c.execute("SELECT * FROM entries WHERE `TargetNode` = ? AND `Position` = ?", (server[1], server[3]))
		results = c.fetchall()
		
		try:
			vps = results[0]
		except IndexError, e:
			continue
		
		if vps[6] == 3:
			print "%s\t%s\t%s\t%s" % (server[1].ljust(26), str(vps[1]).ljust(6), vps[2].ljust(18), vps[3])
	

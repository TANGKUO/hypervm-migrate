#!/usr/bin/python

import oursql

db = oursql.connect(host="localhost", user="root", passwd="", db="transfer")
c = db.cursor()

c.execute("SELECT * FROM servers")
servers = c.fetchall()

for server in servers:
	c.execute("SELECT * FROM entries WHERE `TargetNode` = ?", (server[1],))
	vpses = c.fetchall()
	
	total_vpses = len(vpses)
	
	if server[2] == 0 or server[2] == 3:
		current_vps = int(server[3])
	else:
		current_vps = int(server[3]) - 1
		
	if server[2] == 0:
		status = "Reported done."
	elif server[2] == 1:
		status = "Busy..."
	elif server[2] == 2:
		status = "Reported failure."
	elif server[2] == 3:
		status = "Finished."
	elif server[2] == 4:
		status = "Aborted."
	
	if server[2] == 1:
		c.execute("SELECT * FROM entries WHERE `TargetNode` = ? AND `Finished` = 1", (server[1],))
		current = c.fetchall()[0]
		current_vps_data = "\t%.2fG" % ((current[7] / 1024.0 / 1024),)
		status = "Busy... (%s)" % current[2]
	else:
		current_vps_data = ""
	
	print "%s%s%d/%d (%d%%)%s" % (server[1].ljust(25), status.ljust(25), current_vps, total_vpses, (100.0 * current_vps / total_vpses), current_vps_data)

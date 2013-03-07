import oursql, csv

# input.csv must be in the format username,vpsid,targetnode

db = oursql.connect(host="localhost", user="root", passwd="", db="transfer")
reader = csv.reader(open("sorted.csv", "r"))

nodes = []
c = db.cursor()

for entry in reader:
	username, vps_id, target_node = entry
	c.execute("INSERT INTO entries (`VpsId`, `Username`, `TargetNode`, `Finished`) VALUES (?, ?, ?, 0)", (vps_id, username, target_node))
	print "Adding VPS %s to queue (target node %s)" % (vps_id, target_node)
	
	if target_node not in nodes:
		nodes.append(target_node)

db.commit()

for node in nodes:
	c.execute("INSERT INTO servers (`Host`, `Busy`, `Current`) VALUES (?, 0, 0)", (node,))
	
	c.execute("SELECT Id FROM entries WHERE `TargetNode` = ?", (node,))
	node_entries = c.fetchall()
	counter = 1
	
	for entry in node_entries:
		c.execute("UPDATE entries SET `Position` = ? WHERE `Id` = ?", (counter, entry[0]))
		counter += 1

db.commit()

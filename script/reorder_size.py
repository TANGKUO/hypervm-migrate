import csv, re, operator, oursql

db = oursql.connect(host="localhost", user="root", passwd="", db="transfer")
reader = csv.reader(open("sizes.csv", "r"))

sizes = {}

for entry in reader:
	size, vpsid = entry
	
	if re.match("[0-9]+", vpsid):
		sizes[vpsid] = int(size)
		#print "%s => %.2fG" % (vpsid, int(size) / 1024.0 / 1024.0)

sorted_list = sorted(sizes.iteritems(), key=operator.itemgetter(1))

c = db.cursor()

for vpsid, size in sorted_list:
	c.execute("UPDATE entries SET `DiskUsage` = ? WHERE `VpsID` = ?", (size, vpsid))
	
c.execute("SELECT * FROM entries ORDER BY `TargetNode` ASC, `DiskUsage` ASC")
results = c.fetchall()

servers = {}

for row in results:
	nodename = row[4]
	
	try:
		servers[nodename] += 1
	except KeyError, e:
		servers[nodename] = 1
		
	c.execute("UPDATE entries SET `Position` = ? WHERE `Id` = ?", (servers[nodename], row[0]))



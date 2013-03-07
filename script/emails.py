import oursql, csv, random, string

# input.csv must be in the format vpsid,email

db = oursql.connect(host="localhost", user="root", passwd="", db="transfer")
reader = csv.reader(open("emails.csv", "r"))

emails = []
c = db.cursor()

for entry in reader:
	vps_id, email = entry
	c.execute("UPDATE entries SET `EmailAddress` = ? WHERE `VpsId` = ?", (email, vps_id))
	print "Added e-mail address for VPS %s" % (vps_id)
	
	if email not in emails:
		emails.append(email)

db.commit()

for email in emails:
	if email.strip() != "":
		random_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(0, 16))
		c.execute("INSERT INTO emails (`EmailAddress`, `Key`) VALUES (?, ?)", (email, random_key))

db.commit()

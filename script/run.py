#!/usr/bin/env python

import oursql, time, sys, requests, re
import smtplib
import datetime

db = oursql.connect(host="localhost", user="root", passwd="", db="transfer")

mail_start = """
Hello,

As announced a short while ago, we are going to migrate your VPSes to new servers.
We've had some unforeseen technical difficulties that led to a delay, but these
have been resolved. This e-mail is to inform you that the migration process has 
been started.

The following of your VPSes are affected:

%s

You can follow the queue position and progress of your VPS migrations here: %s

You will receive further notifications for every individual VPS that is being migrated.
Please ensure that you add admin@bluevm.com to your address book, so that
our e-mails do not end up in your spam folder.

Regards,
BlueVM Staff
https://bluevm.com/
"""

mail_vps_start = """
Hello,

This e-mail is to inform you that the migration of your VPS with the username %s has started.
You will receive an e-mail when this migration is finished.

You can follow the progress of all your VPS migrations at %s

Regards,
BlueVM Staff
https://bluevm.com/
"""

mail_vps_success = """
Hello,

This e-mail is to inform you that the migration of your VPS with the username %s has 
finished successfully.

Your new IP addresses are:

%s

You can follow the progress of all your VPS migrations at %s

Regards,
BlueVM Staff
https://bluevm.com/
"""

mail_vps_error = """
Hello,

This e-mail is to inform you that the migration of your VPS with the username %s has 
been aborted because an error has occurred. No data loss has occurred, and staff
will be looking into the issue shortly.

You can follow the progress of all your VPS migrations at %s

Regards,
BlueVM Staff
https://bluevm.com/
"""

class Panel(object):
	def __init__(self, target):
		self.target = target
		self.sess = requests.Session()
		
	def login(self, username, password):
		page = self.sess.get("%s/login/" % self.target).text
		match = re.search('<input type=hidden name=id value="([^"]+)">', page)

		if match is None:
			raise Exception("Not a valid HyperVM panel.")
			
		fid = match.group(1)

		error_string = "Login Unsuccessful"
		post_target = "%s/htmllib/phplib/" % self.target
		post_vars = {
			"frm_clientname": username,
			"frm_password": password,
			"id": fid,
			"login": "Login"
		}

		page = self.sess.post(post_target, data=post_vars).text

		if error_string in page:
			raise Exception("Login failed.")
		
	def run_command(self, node, command):
		post_target = "%s/display.php" % self.target
		post_vars = {
			"frm_o_o[0][class]": "pserver",
			"frm_o_o[0][nname]": node,
			"frm_pserver_c_ccenter_command": command,
			"frm_pserver_c_ccenter_error": "",
			"frm_action": "updateform",
			"frm_subaction": "commandcenter",
			"frm_change": "Execute"
		}

		page = self.sess.post(post_target, data=post_vars).text
		result = re.search("<textarea[^>]+frmtextarea[^>]+>(.*?)<\/textarea>", page, re.DOTALL)
		
		if result is not None:
			return result.group(1)
		
	def Vps(self, username):
		return Vps(self, username)
	
class Vps(object):
	def __init__(self, panel, username):
		self.panel = panel
		self.username = username
		
	def get_ip_addresses(self):
		get_target = "%s/display.php" % self.panel.target
		get_vars = {
			"frm_o_o[0][class]": "vps",
			"frm_o_o[0][nname]": self.username,
			"frm_o_cname": "vmipaddress_a",
			"frm_action": "list",
			"frm_list_refresh": "yes"
		}

		page = self.panel.sess.get(get_target, params=get_vars).text

		ip_regex = '<td\s+class=collist\s+wrap\s+align=left\s+>\s+([0-9.]+)\s+<\/td>'
		ip_list = re.findall(ip_regex, page)
		self.ip_list = ip_list
		
		return ip_list
		
	def delete_ip_addresses(self, addresses):
		post_target = "%s/display.php" % self.panel.target
		post_vars = {
			"frm_o_o[0][class]": "vps",
			"frm_o_o[0][nname]": self.username,
			"frm_accountselect": ",".join(addresses),
			"frm_action": "delete",
			"frm_o_cname": "vmipaddress_a",
			"frm_confirmed": "yes",
			"Confrm": "Confirm"
		}

		page = self.panel.sess.post(post_target, data=post_vars).text
		
	def add_ip_addresses_num(self, num):
		post_target = "%s/display.php" % self.panel.target
		post_vars = {
			"frm_o_o[0][class]": "vps",
			"frm_o_o[0][nname]": self.username,
			"frm_dttype[var]": "type",
			"frm_dttype[val]": "npool",
			"frm_o_cname": "vmipaddress_a",
			"frm_vmipaddress_a_c_type": "npool",
			"frm_vmipaddress_a_c_ip_num": num,
			"frm_action": "add",
			"frm_change": "Add"
		}
		
		page = self.panel.sess.post(post_target, data=post_vars).text
		
	def transfer_to_live(self, target):
		post_target = "%s/display.php" % self.panel.target
		post_vars = {
			"frm_o_o[0][class]": "vps",
			"frm_o_o[0][nname]": self.username,
			"frm_vps_c_syncserver": target,
			"frm_action": "update",
			"frm_subaction": "livemigrate",
			"frm_change": "Update"
		}

		page = self.panel.sess.post(post_target, data=post_vars).text

		if "Switching the Servers has been run in the background." not in page:
			raise Exception("Transfer of %s to %s failed. Maybe an incorrect destination node was specified?" % (self.username, target))
			
	def transfer_to(self, target):
		post_target = "%s/display.php" % self.panel.target
		post_vars = {
			"frm_o_o[0][class]": "vps",
			"frm_o_o[0][nname]": self.username,
			"frm_vps_c_syncserver": target,
			"frm_action": "update",
			"frm_subaction": "switchserver",
			"frm_change": "Update"
		}

		page = self.panel.sess.post(post_target, data=post_vars).text

		if "Switching the Servers has been run in the background." not in page:
			raise Exception("Transfer of %s to %s failed. Maybe an incorrect destination node was specified?" % (self.username, target))
			
	def boot(self):
		get_target = "%s/display.php" % self.panel.target
		get_vars = {
			"frm_o_o[0][class]": "vps",
			"frm_o_o[0][nname]": self.username,
			"frm_action": "update",
			"frm_subaction": "boot"
		}

		page = self.panel.sess.get(get_target, params=get_vars).text

class Mailserver(object):
	def __init__(self, ip, port, ssl, user, password):
		if ssl == True:
			self.smtp = smtplib.SMTP_SSL()
		else:
			self.smtp = smtplib.SMTP()
			
		self.smtp.set_debuglevel(0)
		self.smtp.connect(ip, port)
		self.smtp.login(user, password)
		
	def send(self, to, subject, body):
		from_addr = "BlueVM <admin@bluevm.com>"
		date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
		msg = "From: %s\nTo: %s\nSubject: %s\n\n%s\n" % (from_addr, to, subject, body)
		
		self.smtp.sendmail(from_addr, to, msg)
		
	def quit(self):
		self.smtp.quit()

def send_mail(to, subject, body):
	f = open("email.txt", "a")
	f.write("To: %s\nSubject: %s\n\n%s\n\n\n" % (to, subject, body))
	f.close()
	
	mailserv = Mailserver("smtp.sendgrid.net", 465, True, "user", "pass")
	mailserv.send(to, subject, body)
	mailserv.quit()
	
def generate_url(email):
	global db
	c = db.cursor()
	c.execute("SELECT * FROM emails WHERE `EmailAddress` = ?", (email,))
	result = c.fetchall()[0]
	return "http://transfer.bluevm.com/?email=%s&key=%s" % (result[1], result[2])

panel = Panel("http://manage.bluevm.com:8888")
panel.login("admin", "password")
print "Logged in."

c = db.cursor()

c.execute("SELECT * FROM emails")
emails = c.fetchall()
total = len(emails)
done = 0

try:
	resumed = (sys.argv[1] == "--resume")
except IndexError, e:
	resumed = False

if resumed == False:
	for email in emails:
		c.execute("SELECT * FROM entries WHERE `EmailAddress` = ?", (email[1],))
		entries = c.fetchall()
		
		if len(entries) > 0:
			send_mail(email[1], "Migration process started", mail_start % ("\n\n".join(entry[2] for entry in entries), generate_url(email[1])))
		
		done += 1
		
		sys.stdout.write("Sent %d of %d announcement emails.\n" % (done, total))

while True:
	c.execute("SELECT * FROM servers WHERE `Busy` = 2")
	servers = c.fetchall()
	
	for server in servers:
		c.execute("SELECT * FROM entries WHERE `TargetNode` = ? AND `Position` = ?", (server[1], server[3]))
		vpses = c.fetchall()
		
		c.execute("UPDATE servers SET `Busy` = 4 WHERE `Id` = ?", (server[0],))
		
		if len(vpses) > 0:
			send_mail(vpses[0][3], "VPS migration failed", mail_vps_error % (vpses[0][2], generate_url(vpses[0][3])))
			sys.stderr.write("WARNING: Transfer of %s to %s failed! Further transfers for this server have been aborted.\n" % (vpses[0][2], server[1]))
		else:
			sys.stderr.write("WARNING: Transfer of VPS to %s failed! Further transfers for this server have been aborted.\n" % (server[1]))
	
	c.execute("SELECT * FROM servers WHERE `Busy` = 0")
	servers = c.fetchall()
	
	if len(servers) > 0:
		for server in servers:
			c.execute("SELECT * FROM entries WHERE `TargetNode` = ? AND `Position` = ? LIMIT 1", (server[1], server[3]))
			results = c.fetchall()
			
			if len(results) > 0:
				last = results[0]
				
				vps = panel.Vps(last[2])
				ip_list = vps.get_ip_addresses()
				ip_count = len(ip_list)

				if ip_count > 0:
					vps.delete_ip_addresses(ip_list)
					sys.stderr.write("[%s] Deleted %d IP addresses: %s\n" % (last[2], ip_count, ", ".join(ip_list)))

					vps.add_ip_addresses_num(ip_count)
					sys.stderr.write("[%s] Added %d IP addresses from pool.\n" % (last[2], ip_count))
					
				result = panel.run_command(server[1], "mkdir /vz/root/%s" % last[1])
				
				try:
					if result.strip() == "":
						sys.stdout.write("[%s] Fixed root directory.\n" % last[2])
				except AttributeError, e:
					sys.stderr.write("[%s] WARNING: Could not fix root directory" % last[2])
					
				vps.boot()
				sys.stdout.write("[%s] Booted.\n" % last[2])
					
				send_mail(last[3], "VPS migration finished", mail_vps_success % (last[2], "\n\n".join(vps.get_ip_addresses()), generate_url(last[3])))

			
			c.execute("SELECT * FROM entries WHERE `TargetNode` = ? AND `Finished` = 0 ORDER BY `Position` ASC LIMIT 1", (server[1],))
			entries = c.fetchall()
			
			if len(entries) == 0:
				c.execute("UPDATE servers SET `Busy` = 3 WHERE `Id` = ?", (server[0],))
				sys.stdout.write("Server %s finished migrating.\n" % server[1])
			else:
				eid = entries[0][0]
				c.execute("UPDATE entries SET `Finished` = 1 WHERE `Id` = ?", (eid,))
				c.execute("UPDATE servers SET `Busy` = 1, `Current` = `Current` + 1 WHERE `Id` = ?", (server[0],))
				
				send_mail(entries[0][3], "VPS migration started", mail_vps_start % (entries[0][2], generate_url(entries[0][3])))
				sys.stdout.write("[%s] Started transfer to %s\n" % (entries[0][2], entries[0][4]))
				
				vps = panel.Vps(entries[0][2])
				
				try:
					vps.transfer_to(entries[0][4])
				except Exception, e:
					c.execute("UPDATE servers SET `Busy` = 4 WHERE `Host` = ?", (entries[0][4],))
					c.execute("UPDATE entries SET `Finished` = 3 WHERE `Id` = ?", (entries[0][0],))
					send_mail(entries[0][3], "VPS migration failed", mail_vps_error % (entries[0][2], generate_url(entries[0][3])))
					sys.stderr.write("[%s] WARNING: Transfer to %s failed! Further transfers for this server have been aborted.\n" % (entries[0][2], entries[0][4]))
	else:
		c.execute("SELECT * FROM servers WHERE `Busy` != 3 AND `Busy` != 4")
		
		if len(c.fetchall()) == 0:
			sys.stdout.write("All migrations done. Check the log for any errors.\n")
			exit(0)
	
		
	time.sleep(5)

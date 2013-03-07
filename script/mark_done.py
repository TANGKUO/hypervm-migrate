#!/usr/bin/python

import oursql, sys

db = oursql.connect(host="localhost", user="root", passwd="", db="transfer")
c = db.cursor()

server = sys.argv[1]

c.execute("UPDATE servers SET `Busy` = 0 WHERE `Host` = '%s'" % server)
c.execute("UPDATE entries SET `Finished` = 2 WHERE (`Finished` = 3 OR `Finished` = 1) AND `TargetNode` = '%s'" % server)


#!/usr/bin/python
from rollingBackup import *

#rule
week = 5 #keep at least 3 backups in the current week
month = 8 #keep at least 4 backups in the current month
year = 20 #keep at least 6 backups in a year

#backup file name pattern
pattern = r'.+(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})\.sql' #name like 20110130.databasebackup.tar.gz


#call
rackup(year, month, week, pattern, '/home/tim/Desktop/backups/', 1)

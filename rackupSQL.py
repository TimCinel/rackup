#!/usr/bin/python
from rollingBackup import *

#rule parameters
week = 5 #keep backups at least 5 days back (independant of other backups)
month = 8 #keep at least 8 backups in the current month (independant of other backups)
year = 20 #keep at least 20 backups in a year (independant other backups)

#backup file name pattern
pattern = r'.+(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})\.sql' #matches names like cryptech.20110130.sql

#do a dry run, ( dryRun = 0 ) to perform deletes
rackup(year, month, week, pattern, '/home/tim/Desktop/backups/', dryRun = 1)

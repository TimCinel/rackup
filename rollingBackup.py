#Rackup Tool (Rolling Backup tool) by Tim Cinel
#
#Purpose: Manage archive files used for backup purposes.
#		  More sepecifically, it is meant to limit the number of days', weeks'
#		  and months' backup. 
#		  
#		  For instance, let's say you mirror your web server's file structure daily then
#		  dump it in a tarball with a timestamp. This script could allow you to limit
#		  the system to keep 5 days' instances within a week, two instances in a month,
#		  and 4 most recent instances in a year.
#
#How it (will hopefully) work:
#
#		  

import os
import re
import calendar
from datetime import date
from datetime import timedelta

def rackup(year, month, week, pattern, directory, dryRun = 1):
    rule = {'year':year, 'month':month, 'week':week}
    namePattern = re.compile(pattern)
    rackupWithRule(rule, namePattern, directory, dryRun);

def spread(unitFrequency, unitRange):
    return [day*unitRange/unitFrequency + unitRange/(2*unitFrequency) for day in range(0, unitFrequency)]


def yearSpread(date, rule):
    return spread(rule['year'], 366 if calendar.isleap(date.year) else 365)
    

def monthSpread(date, rule):
    return spread(rule['month'], calendar.monthrange(date.year, date.month)[1])


def yearFilter(year, theYearSpread, startFrom=0, endAt = 0):
    days = []
    startOfYear = date(year, 1, 1)

    for dayOfYear in theYearSpread:
        if dayOfYear >= startFrom and (0 == endAt or dayOfYear <= endAt):
            days.append(startOfYear + timedelta(days=dayOfYear))

    return days;

def monthFilter(year, month, theMonthSpread, startFrom=0, endAt = 0):
    days = []
    startOfMonth = date(year, month, 1)

    for dayOfMonth in theMonthSpread:
        if dayOfMonth >= startFrom and (0 == endAt or dayOfMonth <= endAt):
            days.append(startOfMonth + timedelta(days=dayOfMonth))

    return days;

def rackupWithRule(rule, namePattern, directory, dryRun = 1):
    #get a list of all files
    files  = os.listdir(directory)

    #we need to find the earliest date to start processing from
    today = date.today()
    earliestYear = latestYear = today.year

    #build a list of backup files (files that match pattern) and their associated dates
    backupFiles = [];
    instances = [];
    for filename in files:
        try:
            backupDate = namePattern.search(filename).groupdict()
            instances.append(date(int(backupDate['year']), int(backupDate['month']), int(backupDate['day'])))
            backupFiles.append(filename)
            earliestYear = instances[-1].year if instances[-1].year < earliestYear else earliestYear
        except:
            pass

    filesAndDates = zip(backupFiles, instances)
    allDays = [];

    ##########
    # YEAR 
    ##########
    currentYear = earliestYear
    while currentYear <= latestYear:
        allDays.extend(yearFilter(currentYear, yearSpread(date(currentYear,1,1), rule), startFrom=0, endAt=0 if currentYear != latestYear else today.timetuple()[7]))
        currentYear += 1

    ##########
    # MONTH
    ##########
    #The last month from today's month number (ie. today's the 15th of Dec, this will do Nov 15 onwards)
    if today.day < calendar.monthrange(today.year, today.month)[1]:
        #we're not at the very end of the month, so we should keep some of last month
        lastMonth = date(today.year if today.month > 1 else today.year - 1, today.month - 1 if today.month > 1 else 12, 1)
        allDays.extend(monthFilter(lastMonth.year, lastMonth.month, monthSpread(lastMonth, rule), today.day))
    
    #The current month up to today
    allDays.extend(monthFilter(today.year, today.month, monthSpread(today, rule), 0, today.day))

    
    ##########
    # WEEK 
    ##########
    daysRemaining = rule['week']
    currentDay = today;
    while daysRemaining:
        allDays.append(currentDay)
        currentDay -= timedelta(days=1)
        daysRemaining -= 1

    ####################################
    # GENERATE LIST OF FILES TO DELETE 
    ####################################
    allDays = list(set(allDays))
    allDays.sort()

    toDelete = [];
    toKeep = []; #not neccessary, good for dry runs

    for fileAndDate in filesAndDates:
        if fileAndDate[1] not in allDays:
            toDelete.append(fileAndDate[0])
        else:
            toKeep.append(fileAndDate[0])

    ##############################
    # DELETE FILES OR PRINT OUTPUT
    ##############################
    if dryRun == 0:
        for fileName in toDelete:
            os.remove(directory + fileName)
    else:
        print "Dates generated:"
        for day in allDays:
            print "%d-%d-%d" % (day.year, day.month, day.day)

        print "Would have deleted:"
        for file in toDelete:
            print file;

        print "Would have kept:"
        for file in toKeep:
            print file;





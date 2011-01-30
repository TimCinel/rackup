#Rackup Tool (Rolling Backup tool) by Tim Cinel
#
#Purpose: Manage archive files used for backup purposes.
#		  More sepecifically, it is meant to limit the number of days', weeks'
#		  and months' backup. 
#		  
#		  For instance, let's say you mirror your web server's file structure daily then
#		  dump it in a tarball with a timestamp. This script could allow you to keep at 
#         least 5 days' instances within a week, two instances in a month, and 4 instances 
#         in a year.
#

import os
import re
import calendar
from datetime import date
from datetime import timedelta

def spread(unitFrequency, unitRange):
    """ Builds a list of unitFrequncy integers evenly distributed across 
        unitRange, padded by unitPeriod/2 ( or unitRange/(2*unitFrequency) ) 

        Returns the list of integers
    """
    return [day*unitRange/unitFrequency + unitRange/(2*unitFrequency) for day in range(0, unitFrequency)]


def yearSpread(date, rule):
    """ Builds a list of #rule['year'] integers evenly distributed across
        the number of days in date.year

        Returns the list of integers
    """
    return spread(rule['year'], 366 if calendar.isleap(date.year) else 365)
    

def monthSpread(date, rule):
    """ Builds a list of #rule['year'] integers evenly distributed across
        the number of days in date.month

        Returns the list of integers
    """
    return spread(rule['month'], calendar.monthrange(date.year, date.month)[1])


def spreadFilter(dateStart, spread, startFrom=0, endAt = 0):
    """ Creates a list of dates from dateStart offset by integers listed in
        spread within bounds of startFrom and endAt

        Returns the list of dates
    """
    days = []

    for day in spread:
        if day >= startFrom and (0 == endAt or day <= endAt):
            days.append(dateStart + timedelta(days=day))

    return days;



def rackup(year, month, week, pattern, directory, dryRun = 1):
    """ Creates a rule based on year, month and week frequencies, then applies
        the rule to files matching re pattern (with named groups 'year', 'month'
        and 'week') in directory. 

        No action is performed if dryRun == 1.

        Summary of intended actions is always printed
    """

    rule = {'year':year, 'month':month, 'week':week}
    namePattern = re.compile(pattern)
    rackupWithRule(rule=rule, namePattern=namePattern, directory=directory, dryRun=dryRun);


def rackupWithRule(rule, namePattern, directory, today = date.today(), dryRun = 1):
    """ Applies the rackup rule to files matching namePattern in directory,
        using today as today's date (change for testing).

        No action is performed if dryRun == 1.

        Summary of intended actions is always printed
    """

    #get a list of all files
    files  = os.listdir(directory)

    #we need to find the earliest date to start processing from
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

    #don't consider files from the future (could be a system clock problem)
    filesAndDates = [fileAndDate for fileAndDate in filesAndDates if fileAndDate[1] <= today]

    allDays = [];

    ##########
    # YEAR 
    ##########
    currentYear = earliestYear
    while currentYear <= latestYear:
        spread = yearSpread(date(currentYear,1,1), rule);
        endAt = 0 if currentYear != latestYear else today.timetuple()[7]

        allDays.extend(spreadFilter(date(currentYear,1,1), spread, 0, endAt))
        #allDays.extend(yearFilter(currentYear, yearSpread(date(currentYear,1,1), rule), startFrom=0, endAt=0 if currentYear != latestYear else today.timetuple()[7]))
        currentYear += 1

    ##########
    # MONTH
    ##########
    if today.day < calendar.monthrange(today.year, today.month)[1]:
        #we're not at the very end of the month, so we should keep some of last month
        lastMonth = date(today.year if today.month > 1 else today.year - 1,today.month - 1 if today.month > 1 else 12,1)
        spread = monthSpread(lastMonth, rule);

        allDays.extend(spreadFilter(date(lastMonth.year,lastMonth.month,1),spread,today.day,0))
    
    #The current month up to today
    allDays.extend(spreadFilter(date(today.year,today.month,1), monthSpread(today, rule), 0, today.day))

    
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
            print "Deleting: %s" % (fileName)
            os.remove(directory + fileName)
    else:
        print "Dates accepted:"
        for day in allDays:
            print "%d-%d-%d" % (day.year, day.month, day.day)

        print "Would have deleted:"
        for file in toDelete:
            print file;

        print "Would have kept:"
        for file in toKeep:
            print file;


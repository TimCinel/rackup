#logon2 Rolling Backup tool (Rollup tool)
#
#Purpose: Manage archive files used for backup purposes.
#		  More sepecifically, it is meant to limit the number of days', weeks'
#		  and months' backp. 
#		  
#		  For instance, let's say you mirror your web server's file structure daily then
#		  dump it in a tarball with a timestamp. This script could allow you to limit
#		  the system to keep 5 days' instances within a week, two instances in a month,
#		  and 4 most recent instances in a year. Then perhaps keep one per year for any
#		  longer period.
#		  
#How it (will hopefully) work:
#		  Smaller timeframes have highest priority, so daily limits will be applied before
#		  weekly limits and so on. Also, limits are exclusive - that is the limit placed on
#		  yearly instances will not "count" the instances that have been allowed by the monthly,
#		  weekly, or daily limits.
#		  
#		  Unless the moment at which instances should be kept is explicitly stated (ie. Only
#		  Mondays and Tuesdays, or the 30th of each month or July and August), the script
#		  will automatically distance the instances as much as possible, so as to cover greater
#		  difference.
#		  

import os

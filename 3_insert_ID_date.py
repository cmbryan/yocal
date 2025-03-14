#!/usr/bin/python3
# York Orthodox Calendar Project v2
# Fr Deacon David Hoskin   2018

# Dependencies: 
#   python3, sqlite3, apsw python sqlite wrapper, the datetime and calendar modules.

# This script populates these columns of the Year_ Tables:
# id, date, date_key, day_name, day_num, ord, month, year.
#  id indexes each day of the year (January 1st = 1)
#  date is in the format 'YY-MM-DD'
#  date_key is in the format 'MM-DD' and references data from fixed tables which are common to all years. 
#  day_name is given in full, e.g. 'Saturday'
#  day_num is in the form 1 - 31
#  ord is the ordinal date 2nd, 10th, 21st, etc.
#  month is given in full, eg 'January'
#  year is in full - e.g. 2018 


# First import the SQLite wrapper for Python:

import apsw

# Import the date handling modules:

import datetime
from datetime import date
from datetime import timedelta
from datetime import datetime
import calendar

# Open the database as 'cal' and set the cursor to 'cur':

cal = apsw.Connection('YOCal.db')
cur = cal.cursor()

# Begin:

cur.execute('BEGIN TRANSACTION')

# Get the first and last years to have a table in the database.
# Set initial values and scan for the actual values.
 
yr = 1999         # We scan upwards from here
yr_final = 2100   # We scan downwards from here

name = ''
while name == '' and yr < 2100:
   yr += 1
   cur.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name= ?''', ('Year_'+str(yr),))
   name = cur.fetchone()
   if not name: name = ''

name = ''
while name == '' and yr_final > 1999:
   yr_final -= 1
   cur.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name= ?''', ('Year_'+str(yr_final),))
   name = cur.fetchone()
   if not name: name = ''

print('Tables for the years '+str(yr)+'-'+str(yr_final)+' will be populated')

# Cycle through the range of years:

while yr <= yr_final:

    # Set the number of days in this year to 365 or 366  

    num_days = 365
    if calendar.isleap(yr): num_days = 366         
     
    # Set the current table name:
    tn = "Year_" + str(yr)

    # Set the row counter to its start value:
    row = 1

    # Set the date to its start value:
    thisdate = date(yr,1,1)

    # For each day... one row per day    

    while row <= num_days:
        
        # Set variables for this row

        wkday = thisdate.strftime('%A')
        dynum = int(thisdate.strftime('%d'))
        month = thisdate.strftime('%B')
        key = thisdate.strftime('%m-%d')

        # Determine the Ordinal form of this date

        if dynum == 1 or dynum == 21 or dynum == 31:
            suff = 'st'
        elif dynum == 2 or dynum == 22:
            suff = 'nd'
        elif dynum == 3 or dynum == 23:
            suff = 'rd'
        else: suff = 'th' 
        ordnl = str(dynum) + suff

        # Insert the data into the first six column of this row
        cur.execute(
                '''INSERT or IGNORE INTO %s 
                (id, date, date_key, day_name, day_num, ord, month, year) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?
                )''' % tn, (row, str(thisdate), str(key), wkday, dynum, ordnl, month, yr))
        
        # Update the row and date
 
        row += 1
        thisdate = thisdate + timedelta(1)

    # Update the year
    yr += 1

# write to database, close it and sign off
cur.execute("COMMIT")

cal.close()

x = input('\n   All done... Press Enter to exit')

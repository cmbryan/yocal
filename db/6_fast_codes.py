#!/usr/bin/python3
# York Orthodox Calendar Project v2
# Fr Deacon David Hoskin   2018

# Dependencies: python3, sqlite3, apsw python sqlite wrapper, the datetime module.

# This script determines the Fast Codes for each day of a specific year or series
# of years and then populates the 'fast' column of the appropriate year table(s).
# Information about the fast seasons is added to the season column.

# Columns 'id', 'date', 'day_name' and 'date_key' must be already populated.
# The fixed tables 'Pascha' and 'Menaion' must already exist and be populated.

# f3 = strict fast; f2 = wine and oil allowed; f1 = fish wine and oil allowed

# My sources for Fast Rules include:
# 'The Book of the Typikon' - Bp Khoury's English translation of the Antiochian
#   Typikon (edited by Archpriest John Morris, 2011 )
# The website of the Antiochian Orthodox Christian Archdiocese of North America:
# http://ww1.antiochian.org/1157652263
# The website of the St Raphael Clergy Brotherhood, Diocese of Wichita and Mid-America: 
# http://www.dowama.org/content/typikon

# First import the SQLite wrapper for Python:

import apsw

# Import the date handling modules:

import datetime
from datetime import date
from datetime import timedelta

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
    
    # Set table name to that of the current year:

    tn = 'Year_' + str(yr)

    # Set reference date for calculations which use the table ids.
    # The last day of the previous year is treated as id = 0:

    base_date = date(yr-1,12,31)
     
    # Get the date of this year's Pascha from the Pascha table:

    cur.execute("SELECT pascha_date FROM pascha WHERE year = ?", (yr,))
    x = cur.fetchone()[0]
    pascha = datetime.datetime.strptime(x, '%Y-%m-%d').date()

    # Get its id on the current Year table:

    pascha_id = (pascha - base_date).days

    # RULE: THROUGHOUT THE YEAR, in the absence of other factors,
    # all Wednesdays and Fridays are 'f3'

    # So initially we set all Wednesdays and Fridays to f3 - the easy bit...:

    cur.execute(
            '''UPDATE %s SET fast = "f3" 
            WHERE day_name IN ("Wednesday","Friday")''' % tn)

    # We now work through the year making the necessary modifications.

    # RULE: Following the Nativity the days are fast free until the Eve of the Theophany:
 
    theoph_id = 6

    cur.execute(
            '''UPDATE %s SET fast = "Fast free" WHERE id < ? AND day_name IN ("Wednesday","Friday")
            ''' % tn, (theoph_id-1,))

    # NB The rule about the Eve of the Theophany we leave until later...
     
    # RULE: The Theophany is fast free:
 
    cur.execute(
            '''UPDATE %s SET fast = "Fast free" WHERE id = ? AND day_name IN ("Wednesday","Friday")
            ''' % tn, (theoph_id,))
    cur.execute(
            '''UPDATE %s SET fast = Null WHERE id = ?''' % tn, (theoph_id,))
           
    # THE TRIODION

    # The start of the Triodion is 70 days before Pascha so its id is:

    triod_id = pascha_id - 70
    
   # RULE: The first week of the Tiodion is 'Fast free week':

    cur.execute(
            '''UPDATE %s SET fast = "Fast free week" 
            WHERE id BETWEEN ? AND ?''' % tn, (triod_id+1, triod_id+6))

    # RULE: The third week of the Tiodion is Cheesefare week:

    cur.execute(
            '''UPDATE %s SET fast = "Cheesefare week:  abstain only from meat" 
            WHERE id BETWEEN ? AND ?''' % tn, (triod_id+15, triod_id+21))


    # GREAT LENT begins on the Monday following Cheesefare Sunday. 
    # Cheesefare Sunday is 49 days before Pascha:

    cheese_id = pascha_id - 49

    # Update the season column between the start of Lent and Holy Saurday

    cur.execute(
            '''UPDATE %s SET season = "Great Lent begins" 
            WHERE id = ?''' % tn, (cheese_id+1,))

    cur.execute(
            '''UPDATE %s SET season = "Lenten Fast" 
            WHERE id BETWEEN ? AND ?''' % tn, (cheese_id+2,pascha_id-1))

    # RULE: The weekdays of Lent are normally f3, and Saturdays and Sundays are f2.
    # Set all weekdays of Lent up to Holy Friday to f3:

    cur.execute(
            '''UPDATE %s SET fast = "f3" WHERE id BETWEEN ? AND ? 
            AND day_name NOT IN ("Saturday","Sunday")
            ''' % tn, (cheese_id+1, pascha_id-1))
    
    # Set the Saturdays and Sundays of Lent to f2:

    cur.execute(
            '''UPDATE %s SET fast = "f2" WHERE id BETWEEN ? AND ? 
            AND day_name IN ("Saturday","Sunday")
            ''' % tn, (cheese_id+1, pascha_id-1))
    
    # Exceptions: Palm Sunday is 'f1'
    #             Holy Thursday is 'f3, wine allowed':
    #             Holy Saturday is 'f3, wine allowed':

    cur.execute(
            '''UPDATE %s SET fast = "f1" WHERE id = ?''' % tn, (pascha_id-7,))
    cur.execute(
            '''UPDATE %s SET fast = "strict fast, wine allowed" WHERE id = ?''' % tn, (pascha_id-3,))
    cur.execute(
            '''UPDATE %s SET fast = "strict fast, wine allowed" WHERE id = ?''' % tn, (pascha_id-1,))
  
    # THE PASCHA AND PENTECOST SEASON

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # RULE: The period from Pascha to Ascension is fast free 

    cur.execute(
            '''UPDATE %s SET fast = "The Paschal season is fast free" WHERE id BETWEEN ? AND ? AND day_name IN ("Wednesday","Friday")
            ''' % tn, (pascha_id, pascha_id+38))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # NB In some traditions the fast-free period is only until Thomas Sunday
    # In that case, comment out the above UPDATE and un-comment the following:

    # RULE: The period from Pascha to Thomas Sunday is fast free 

    #cur.execute(
    #        '''UPDATE %s SET fast = Null WHERE id BETWEEN ? AND ?
    #        ''' % tn, (pascha_id, pascha_id+7))
 
    # RULE On the Wednesday and Fridays between Thomas Sunday and Pentecost
    #      the fast is 'f2'

    #cur.execute(
    #        '''UPDATE %s SET fast = "f2" WHERE day_name IN ("Wednesday", "Friday") AND id BETWEEN ? AND ?
    #        ''' % tn, (pascha_id+10, pascha_id+47))

    # RULE On the Wednesdays of Mid-Pentecost and the Leavetaking of Pascha
    #      the fast is 'f1'

    #cur.execute(
    #        '''UPDATE %s SET fast = "f1" WHERE id IN (?, ?)
    #        ''' % tn, (pascha_id+24, pascha_id+38))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      
    # RULE: The week of Pentecost is fast free:

    cur.execute(
            '''UPDATE %s SET fast = "Fast free" WHERE id BETWEEN ? AND ? AND day_name IN ("Wednesday","Friday")
            ''' % tn, (pascha_id+49, pascha_id+56))

    # RULE: The APOSTLES’ FAST begins on the Monday following All Saints Sunday 
    # (i.e. 57 days after Pascha) and ends on the day before the feast of SS Peter and Paul.
    # Wednesdays and Fridays are f3 (these are already set), and other days are f1. 
    # (NB Slav usage is different)

    # Get the Apostles id:

    apos_id = (date(yr,6,29) - base_date).days

    # Update the season column between the start and end of the fast

    cur.execute(
            '''UPDATE %s SET season = "Apostles’ Fast begins" 
            WHERE id = ?''' % tn, (pascha_id+57,))

    cur.execute(
            '''UPDATE %s SET season = "Apostles’ Fast" 
            WHERE id BETWEEN ? AND ?''' % tn, (pascha_id+58,apos_id-1))

    # And then set the f1 days...:

    cur.execute(
            '''UPDATE %s SET fast = "f1" WHERE id BETWEEN ? AND ? 
            AND day_name NOT IN ("Wednesday","Friday")
            ''' % tn, (pascha_id+57, apos_id-1))
 
    # RULE: The DORMITION FAST begins on August 1st and ends on August 14th 
    # The weekdays are f3. Saturdays and Sundays are f2.

    # Get the Dormition id:

    dorm_id = (date(yr,8,15) - base_date).days

    # Update the season column between the start and end of the fast

    cur.execute(
            '''UPDATE %s SET season = "Dormition Fast begins" 
            WHERE id = ?''' % tn, (dorm_id-14,))

    cur.execute(
            '''UPDATE %s SET season = "Dormition Fast" 
            WHERE id BETWEEN ? AND ?''' % tn, (dorm_id-13,dorm_id-1))

    # Set the weekdays of the fast to f3: 

    cur.execute(
            '''UPDATE %s SET fast = "f3" WHERE id BETWEEN ? AND ? 
            AND day_name NOT IN ("Saturday","Sunday")
            ''' % tn, (dorm_id-14, dorm_id-1))
    
    # and set the Saturdays and Sundays of the fast to f2:

    cur.execute(
            '''UPDATE %s SET fast = "f2" WHERE id BETWEEN ? AND ? 
            AND day_name IN ("Saturday","Sunday")
            ''' % tn, (dorm_id-14, dorm_id-1))
     
    # Exception: The TRANSFIGURATION on August 6th is f1.

    # Get the Tranfiguration id and update the fast:

    transf_id = (date(yr,8,6) - base_date).days
    cur.execute(
            '''UPDATE %s SET fast = "f1" WHERE id = ?''' % tn, (transf_id,))
   
    # RULE: The NATIVITY FAST begins on November 15th and ends on December 24th. 
    # Wednesdays and Fridays are f3 (already set). The other days are f1 until
    # December 12th when weekdays become f3 and Saturday and Sunday f2.  
    # (NB Slav usage is different)

    # Get the id of the Nativity:

    nat_id = (date(yr,12,25) - base_date).days

    # Update the season column between the start and end of the fast

    cur.execute(
            '''UPDATE %s SET season = "Nativity Fast begins" 
            WHERE id = ?''' % tn, (nat_id-40,))

    cur.execute(
            '''UPDATE %s SET season = "Nativity Fast" 
            WHERE id BETWEEN ? AND ?''' % tn, (nat_id-39,nat_id-1))

    # Set the f1 days of the fast...:

    cur.execute(
            '''UPDATE %s SET fast = "f1" WHERE id BETWEEN ? AND ? 
            AND day_name NOT IN ("Wednesday","Friday")
            ''' % tn, (nat_id-40, nat_id-14))

    # Set the f2 days of the fast...:

    cur.execute(
            '''UPDATE %s SET fast = "f2" WHERE id BETWEEN ? AND ? 
            AND day_name IN ("Saturday","Sunday")
            ''' % tn, (nat_id-13, nat_id-1))

    # Set the f3 days of the fast...:

    cur.execute(
            '''UPDATE %s SET fast = "f3" WHERE id BETWEEN ? AND ? 
            AND day_name IN ("Monday","Tuesday","Thursday")
            ''' % tn, (nat_id-13, nat_id-1))
  
    # RULE: Following the Nativity the days are fast free until the Eve of the Theophany 

    cur.execute(
            '''UPDATE %s SET fast = "Fast free" WHERE id > ? AND day_name IN ("Wednesday","Friday")
            ''' % tn, (nat_id-1,))

    # FEAST DAYS COINCIDING WITH A FAST:
    
    # RULE:
    # a) When any fast day coincides with a Class 2 Commemoration (of the Theotokos) it becomes f1.
    # b) When a f3 fast day coincides with a Class 3, 4, or K Commemoration it usually becomes f2. This is also true for a few Class 5 Commems which are marked as Class X.

    # Get the instances of Feasts on a fast day
    # But exclude the Feasts of George, Mark and James son of Zebedee 
    #     which, if in Lent,will be transferred.
    # And exclude Holy Week:
   
    cur.execute(
            '''SELECT Menaion.class, Menaion.date_key, %s.fast
               FROM Menaion
               JOIN %s
               ON Menaion.date_key = %s.date_key
               WHERE Menaion.class IN ("2", "3", "4", "K", "X") 
               AND %s.fast IN ("f2","f3")
               AND Menaion.date_key NOT IN ('04-23','04-25','04-30')
               AND %s.id NOT BETWEEN ? AND ? 
               ''' % (tn, tn, tn, tn, tn), (pascha_id-7,pascha_id))

    matches = cur.fetchall()

    for match in matches:
        feast = match[0]        
        dkey = match[1]
        fast = match[2]
        
        # Initially set all the instances to f2
        # - this takes care of case b):

        cur.execute('''UPDATE %s SET fast = "f2" 
                       WHERE date_key = ?''' % tn, (dkey,))

        # Now we need reset Class 2 feasts falling on a fast to f1 - Case a):

        if feast == "2":
            cur.execute('''UPDATE %s SET fast = "f1" 
                        WHERE date_key = ?''' % tn, (dkey,))

    # The ANNUNCIATION always falls in Lent and must be set to f1:

    cur.execute(
            '''UPDATE %s SET fast = "f1" WHERE date_key = ?''' % tn, ('03-25',))

    # The Afterfeast of the ANNUNCIATION always falls in Lent and is set to f2:

    cur.execute(
            '''UPDATE %s SET fast = "f2" WHERE date_key = ? 
            AND day_name NOT IN ("Saturday","Sunday")''' % tn, ('03-26',))

    # IF the feast of HARALAMPOS (02-10) or of the FORERUNNER (02-24) fall on Soul Sabbath 
    # (Saturday before Meatfare Sunday) it is transferred to the previous Friday (triod_id +12)
    # which becomes f2:

    cur.execute(
            '''UPDATE %s SET fast = "f2" WHERE id = ? AND Major_commem NOT IN (Null, "")''' % tn, (triod_id+12,))

    # FEAST DAYS OF THE 12 APOSTLES

    # RULE: ** Current practice allows no provision for relaxing the fast **
    #       However, Khoury, chap X says:
    #       When such a feast day coincides with a fast day it becomes f1

    # AFTERFEASTS OF OUR LORD AND OF THE THEOTOKOS

    # RULE: ** Current practice allows no provision for relaxing the fast **
    #       However, Khoury, chap X says:
    #       Fast days become f1 during these afterfeasts unless they fall 
    #       in Great Lent or in the Dormition Fast. 

    # SPECIAL FAST DAYS

    # RULE: The Eve of the Theophany (Jan 5),
    #       The Beheading of the Baptist (Aug 29),
    #       The Exaltation of the Cross (Sep 14)
    #       The Eve of the Nativity (Dec 24)
    #       are f3 on weekdays, or f2 on Saturdays and Sundays.

    # Set these when they fall on a weekday to f3:

    cur.execute(
            '''UPDATE %s SET fast = "f3" WHERE date_key IN ('01-05', '08-29', '09-14', '12-24')
            AND day_name NOT IN ("Saturday","Sunday")
            ''' % tn)

    # and when they fall on a Saturday or Sunday set to f2:

    cur.execute(
            '''UPDATE %s SET fast = "f2" WHERE date_key IN ('01-05', '08-29', '09-14', '12-24')
            AND day_name IN ("Saturday","Sunday")
            ''' % tn)    
 
    # NOW CHANGE THE FAST CODES TO MEANINGFUL TEXT
 
    cur.execute('''SELECT date_key, fast, season FROM %s WHERE fast !="" ''' % tn)
    data = cur.fetchall()
    
    for d_key, fast, season in data:
         if season =="" or season == None:
            txt = "Fast day: "
         else:
            txt = season + ": "
         if fast == "f1":
            txt += "fish, wine and oil allowed"
         elif fast == "f2":
            txt += "wine and oil allowed"
         elif fast == "f3":
            txt += "strict fast"
         elif fast == "strict fast, wine allowed":
            txt += fast
         else:
            txt = fast
          
         cur.execute('''UPDATE %s SET fast = ? WHERE date_key = ?''' % tn, (txt, d_key))
 
    
    # Move on to the next year:

    yr += 1

# Write the data to the table 

cur.execute('COMMIT') 

cal.close()

print('Finished stage 6')

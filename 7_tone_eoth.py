#!/usr/bin/python3
# York Orthodox Calendar Project v2
# Fr Deacon David Hoskin   2018

# Dependencies: python3, sqlite3, apsw python sqlite wrapper, the datetime module.

# This script determines the Tone and Eothinon for each Sunday and then 
# populates the these columns of the appropriate year table(s).

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
     
    # Get the date of THIS YEAR'S Pascha from the Pascha table:

    cur.execute("SELECT pascha_date FROM pascha WHERE year = ?", (yr,))
    x = cur.fetchone()[0]
    pascha = datetime.datetime.strptime(x, '%Y-%m-%d').date()

    # Get its id on the Year table:  

    pascha_id = (pascha - base_date).days

    # Get the date of LAST YEAR'S Pascha from the Pascha table:

    cur.execute("SELECT pascha_date FROM pascha WHERE year = ?", (yr-1,))
    x = cur.fetchone()[0]
    last_pascha = datetime.datetime.strptime(x, '%Y-%m-%d').date()

    # The TONES follow a repeated cycle of EIGHT WEEKS. The cycle starts with Tone 2
    # on the third Sunday Pascha and ends on the 5th Sunday of Lent.
    # The intervening Sundays, viz. Palm Sunday, Pascha and Thomas Sunday are Festal.
    # Pentecost and feasts of the Lord falling on a Sunday are also Festal.

    # Starting with Tone 2 on Pascha 3 of LAST YEAR, cycle through the Sunday Tones
    # until the first Sunday of THIS YEAR is reached:

    tone = 2
    sun = last_pascha + timedelta(14)

    while sun <= base_date:
        tone = (tone % 8) +1
        sun = sun + timedelta(7)

    # 'sun' and 'tone' are now set for the first Sunday of this year, and we get its id on the Year table.

    first_sun = sun
    first_sun_id = (first_sun - base_date).days

    # Using the Year table ids, set the Tones for the Sundays of this year 
    # until Lent 5 is reached:

    sun_id = first_sun_id
   
    while sun_id < pascha_id-13:

        text = "Tone " + str(tone) 
       
        cur.execute(
                '''UPDATE %s SET tone = ? WHERE id = ?''' % tn, (text, sun_id))

        tone = (tone % 8) +1
        sun_id += 7
 
    # Set the Tone to Festal for the next three Sundays:

    text ="Tone of the feast"
    
    while sun_id < pascha_id +14:

        cur.execute(
                '''UPDATE %s SET tone = ? WHERE id = ?''' % tn, (text, sun_id))

        sun_id += 7

    # Pascha 3 has now been reached so, starting with Tone 2, 
    # set the Tone for rest of the year.

    # First get the id of the last day of the year (it will be 365 or 366):

    last_day_id = (date(yr,12,31) - base_date).days

    tone = 2

    while sun_id <= last_day_id:

        text = "Tone " + str(tone)

        cur.execute(
                '''UPDATE %s SET tone = ? WHERE id = ?''' % tn, (text, sun_id))

        tone = (tone % 8) +1
        sun_id += 7
    
    # Set the Tone for OTHER FESTAL SUNDAYS.

    text ="Tone of the feast"

    # One of these is Pentecost:

    cur.execute(
            '''UPDATE %s SET tone = ? WHERE id = ?''' % tn, (text, pascha_id +49))
    
    # The following Class 1 feasts, if they fall on a Sunday, take a festal Tone: 
    # Elevation of the Cross (09-14), Nativity (12-25), Theophany (01-06), Transfiguation (08-06). 

    # Get the feasts, and update:

    cur.execute(
            '''SELECT date_key FROM %s 
            WHERE Day_name = "Sunday" AND date_key IN ('09-14','12-25','01-06','08-06')
            ''' % tn)

    feasts = cur.fetchall()
    if feasts:
       for feast in feasts:
          cur.execute(
                    '''UPDATE %s SET tone = ? WHERE date_key = ?''' % tn, (text,feast[0]))
    
    # The EOTHINONS follow a repeated cycle of ELEVEN WEEKS. The cycle starts with Tone 1
    # on the All Saints Sunday (56 days after Pascha) and ends on the 5th Sunday of Lent.
    # The sequence from Palm Sunday to Pentecost is:
    #              Festal - Festal - 1 - 4 - 5 - 7 - 8 - 10 - Festal 
    # Place this sequence in a tuple:

    seq = ('Eothinon of the feast','Eothinon of the feast','Eothinon 1','Eothinon 4','Eothinon 5','Eothinon 7','Eothinon 8','Eothinon 10','Eothinon of the feast')

    # First find the Eothinon of the first Sunday in the year.
    # The method used for the Tones is applied here:

    # Starting with Eothinon 1 on All Saints Sunday of LAST YEAR, cycle through the Sundays
    # until the first Sunday of THIS YEAR is reached:

    eoth = 1
    sun = last_pascha + timedelta(56)

    while sun <= base_date:
        eoth = (eoth % 11) +1
        sun = sun + timedelta(7)

    # 'eoth' and 'sun' are now set for the first Sunday of this year.
    # Set the Sundays up to Lent 5:

    sun_id = first_sun_id

    while sun_id < pascha_id-13:

        text = "Eothinon " + str(eoth)

        cur.execute(
                '''UPDATE %s SET eothinon = ? WHERE id = ?''' % tn, (text, sun_id))

        eoth = (eoth % 11) +1
        sun_id += 7
 
    # Set the Eothinon to the fixed sequence for the next nine Sundays:

    for text in seq:

        cur.execute(
                '''UPDATE %s SET eothinon = ? WHERE id = ?''' % tn, (text, sun_id))

        sun_id += 7

    # All Saints Sunday has now been reached so, starting with Eothinon 1, 
    # set the Eothinon for rest of the year.

    eoth = 1

    while sun_id <= last_day_id:

        text = "Eothinon " + str(eoth)

        cur.execute(
                '''UPDATE %s SET eothinon = ? WHERE id = ?''' % tn, (text, sun_id))

        eoth = (eoth % 11) +1
        sun_id += 7

    # Set the Eothinon for OTHER FESTAL SUNDAYS: Both Class 1 and Class 2.
    # Class 2 feasts of the Theotokos falling on a Sunday also take a festal eothinon.
    # Nativity (09-08), Entrance (11-21), Meeting (02-02), Annunciation (03-25), Dormition (08-15) 

    text ="Eothinon of the feast"
     
    cur.execute(
            '''SELECT date_key FROM %s 
            WHERE Day_name = "Sunday" AND date_key IN 
            ('09-14','12-25','01-06','08-06','09-08','11-21','02-02','03-25','08-15')
            ''' % tn)

    feasts = cur.fetchall()
    if feasts:
       for feast in feasts:
            cur.execute('''UPDATE %s SET eothinon = ? WHERE date_key = ?''' % tn, (text,feast[0]))

    # Move on to the next year:

    yr += 1

# Write the data to the table 

cur.execute('COMMIT') 
   
cal.close()

x = input('\n   All done... Press Enter to exit')

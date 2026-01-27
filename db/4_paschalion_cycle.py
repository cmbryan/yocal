#!/usr/bin/python3
# York Orthodox Calendar Project v2
# Fr Deacon David Hoskin   2018

# Dependencies: python3, sqlite3, apsw python sqlite wrapper, the datetime module.

# Where the cycle of daily lections and their associated codes appears in the annual calendar largely depends on the date of the previous and forthcoming Paschas. This script binds the cycle to actual calendar dates and populates the Year tables accordingly.
# 
# The A_Lections and G_Lections tables provide the raw data which is then written to Year table columns 'a_code' 'g_code' 'desig_a' 'desig_g' 'apos' 'gosp' 'extra' 'x_code'.
#
# The ten occasions when the Liturgy of St Basil is used are marked in the 'basil' column.
#
# The fixed tables 'Pascha' 'A_Lections' 'G_Lections' must already exist and be populated.
# The id column and all the date columns of the year table must already be populated.

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

# Set variables for the ids of key points in the Lections tables.
# The Apostle and Gospel entries largely run parallel, so one id sometimes suffices for both lections. These variables hold good for any year.

# We need the lection table ids for:
#        Pascha (A1Sun, J1Sun), 
#        The start of the Triodion (E33Sun, L16Sun)
#        E16Sat and M16Sat for the Saturday eight days before the Tiodion.
#        Also E32Sat and L15Sat. These ids can be taken from the Triodion ids
#            as come immediately before the Triodion ids in the Lection tables
#        Holy Saturday which has the code G7Sat
# We can get all of these from the G_Lections table as those ids will hold good for the A_Lections table also: 

cur.execute('''SELECT g_id FROM G_Lections WHERE code = "J1Sun"''') 
lect_id_pascha = cur.fetchone()[0]

cur.execute('''SELECT g_id FROM G_Lections WHERE code = "M16Sat"''') 
lect_id_sat_b_triod = cur.fetchone()[0]

cur.execute('''SELECT g_id FROM G_Lections WHERE code = "L16Sun"''') 
lect_id_triod = cur.fetchone()[0]

cur.execute('''SELECT g_id FROM G_Lections WHERE code = "G7Sat"''') 
lect_id_holy_sat = cur.fetchone()[0]

# Create lists of the Sunday codes for the Sundays between the Sunday after
# the Theophany and the start of the Triodion. 
# With the New Calendar there may be 1 to 6 such Sundays:

# If 1 Sunday, the Apostle and Gospel codes are:
b_triod_1 = [('E32Sun','L15Sun')]

# If 2 Sundays:
b_triod_2 = [('E29Sun','L12Sun'), ('E32Sun', 'L15Sun')]

# If 3 Sundays:
b_triod_3 = [('E29Sun', 'L12Sun'), ('E32Sun','L15Sun'), ('E17Sun', 'M17Sun')]

# The lists for 4 or five Sundays depend on whether 14th of Luke was used in
# December. 'L14Sun' is reserved for Sundays falling on Dec 1st, 2nd or 3rd. 

# If 4 Sundays and L14Sun was NOT used:
b_triod_4a = [('E29Sun','L12Sun'), ('E31Sun','L14Sun'), ('E32Sun','L15Sun'), ('E17Sun','M17Sun')]

# If 4 Sundays and L14Sun Whttps://www.w3schools.com/python/python_mysql_update.aspAS used:
b_triod_4b = [('E29Sun','L12Sun'), ('E32Sun','L15Sun'), ('E16Sun','M16Sun'), ('E17Sun','M17Sun')]

# If 5 Sundays and L14Sun was NOT used:
b_triod_5a = [('E29Sun','L12Sun'), ('E31Sun','L14Sun'), ('E32Sun','L15Sun'), ('E16Sun','M16Sun'), ('E17Sun','M17Sun')]

# If 5 Sundays and L14Sun WAS used:
b_triod_5b = [('E29Sun','L12Sun'), ('E32Sun','L15Sun'), ('E15Sun','M15Sun'), ('E16Sun','M16Sun'), ('E17Sun','M17Sun')]

# If 6 Sundays:
b_triod_6 = [('E29Sun','L12Sun'), ('E31Sun','L14Sun'), ('E32Sun','L15Sun'), ('E15Sun','M15Sun'), ('E16Sun','M16Sun'), ('E17Sun','M17Sun')]

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

    # The date of the first day (nyd for 'New Year's Day') of this year is:

    nyd = date(yr,1,1)

    # Its id is 1

    nyd_id = 1

    # The date of the last day of this year is:

    end_yr = date(yr,12,31)

    # Get its id on the current Year table. It may be 365 or 366:

    end_yr_id = (end_yr - base_date).days

    # Get the date of this year's Pascha from the Pascha table:

    cur.execute("SELECT pascha_date FROM pascha WHERE year = ?", (yr,))
    x = cur.fetchone()[0]
    pascha = datetime.datetime.strptime(x,'%Y-%m-%d').date()
        
    # Get its id on the current Year table:

    pascha_id = (pascha - base_date).days

    # The Triodion begins 70 days before Pascha, so:

    triod_id = (pascha_id - 70)

    # Get the date of LAST YEAR's Pascha from the Pascha table:

    cur.execute("SELECT pascha_date FROM pascha WHERE year = ?", (yr-1,))
    x = cur.fetchone()[0]
    last_pascha = datetime.datetime.strptime(x, '%Y-%m-%d').date()

    # Get the date of last year's Lukan Jump
    # This is the Monday after the Sunday after the Exaltation of the Cross - SunAX

    # Set the date of SAX initially to the day after the Cross and update until a 
    # Sunday is reached
 
    sunax = date(yr-1,9,14) + timedelta(1)
    
    while sunax.weekday() != 6:
        sunax += timedelta(1)

    # Add another day to get the Monday after for the Lukan Jump

    last_jump = sunax + timedelta(1)


    #
    # THE PERIOD BETWEEN THE BEGINNING OF THE YEAR AND THE START OF THE TRIODION
    # __________________________________________________________________________

# What happens between the Sunday after the Theophany and the start of the Triodion is
# particularly arcane. PLEASE READ THIS FIRST in order to understand the code: 

# The SUNDAY designations and lections between the Theophany and the start of the
# Triodion follow one of several patterns governed by the number of Sundays which need 
# to be filled.

# Meanwhile the DAILY lections follow the Epistle cycle until the Saturday of the 32nd week,
# and the Gospel cycle is followed until the Saturday of the 15th week of Luke.
# The remaining days are filled by repeating a section of the Epistle cycle and of the 
# Matthew cycle so that the Saturday of the 16th week of each cycle is reached eight days
# before the Triodion begins.


    # Determine the Apostle and Gospel codes for the first day of the year.

    # The Epistle Cycle started on the Monday after Pentecost in the previous year.
    # This 50 days after Pascha.

    E1 = last_pascha + timedelta(50)

    # The start of this year is how many whole weeks later?

    n = (nyd - E1).days // 7

    n += 1   # n weeks AFTER week 1 brings us to week n+1

    # The Epistle Code is in the format 'E21Wed', so the code for January 1st is:

    E_code_nyd = "E" + str(n) + nyd.strftime("%a")

    # The Gospel Cycle began with the 'Lukan Jump' on the Monday after
    # the Sunday after the Exaltation of the Cross (Sept 14th).
    
    G1 = last_jump
    
    # The start of this year is how many whole weeks later?
    n = (nyd - G1).days // 7

    n += 1   # n weeks AFTER week 1 brings us to week n+1

    # The Gospel Code is in the format 'L13Thu', so the code for January 1st is:

    G_code_nyd = "L" + str(n) + nyd.strftime("%a")

    # Get the ids from the Lections tables corresponding to the code of nyd:

    cur.execute('''SELECT a_id FROM A_Lections WHERE code = ?''', (E_code_nyd,))
    a_id = cur.fetchone()[0]
    
    cur.execute('''SELECT g_id FROM G_Lections WHERE code = ?''', (G_code_nyd,))
    g_id = cur.fetchone()[0]

    #    
    # First we tackle the WEEKDAY EPISTLES. The Sundays will be overwritten later.
    #
    
    # Get and write the data up to E32Sat first setting the counters.

    yr_tbl_id = 1
    
    while a_id < (lect_id_triod-7):

        cur.execute('''UPDATE %s SET
                desig_a = (SELECT designation FROM A_Lections WHERE A_Lections.a_id = ?), 
                apos = (SELECT lection FROM A_Lections WHERE A_Lections.a_id = ?),
                a_code = (SELECT code FROM A_Lections WHERE A_Lections.a_id = ?)
                WHERE id = ?''' % tn, (a_id, a_id, a_id, yr_tbl_id)) 
    
        # Update the counters:

        yr_tbl_id += 1
        a_id += 1

    # We can now backfill the remaining dates starting with the eighth day before the Triodion
    # which is always E16Sat.

    # We need to backfill until the day after E32Sat
    # The variable yr_tbl_id is currently set to that value, so we save it

    yr_tbl_id_done = yr_tbl_id

    # Now set the counters to their new initial values:

    yr_tbl_id = triod_id -8
    a_id = lect_id_sat_b_triod 

    while yr_tbl_id >= yr_tbl_id_done:

        cur.execute('''UPDATE %s SET
                desig_a = (SELECT designation FROM A_Lections WHERE A_Lections.a_id = ?), 
                apos = (SELECT lection FROM A_Lections WHERE A_Lections.a_id = ?),
                a_code = (SELECT code FROM A_Lections WHERE A_Lections.a_id = ?)
                WHERE id = ?''' % tn, (a_id, a_id, a_id, yr_tbl_id)) 
        
        # Update the counters... downwards:

        yr_tbl_id -= 1
        a_id -= 1

    #
    #The process is now repeated for the WEEKDAY GOSPEL lections:
    #

    # Get and write the data up to L15Sat, first setting the counters.

    yr_tbl_id = 1
    
    while g_id < (lect_id_triod-7):

        cur.execute('''UPDATE %s SET
                desig_g = (SELECT designation FROM G_Lections WHERE G_Lections.g_id = ?), 
                gosp = (SELECT lection FROM G_Lections WHERE G_Lections.g_id = ?),
                g_code = (SELECT code FROM G_Lections WHERE G_Lections.g_id = ?)
                WHERE id = ?''' % tn, (g_id, g_id, g_id, yr_tbl_id)) 
    
        # Update the counters:

        yr_tbl_id += 1
        g_id += 1

    # We can now backfill the remaining dates starting with the eighth day before the Triodion
    # which is always M16Sat.

    # We need to backfill until the day after L15Sat
    # The variable yr_table_id is currently set to that value, so we save it

    yr_tbl_id_done = yr_tbl_id

    # Now set the counters to their new initial values:

    yr_tbl_id = triod_id -1
    g_id = lect_id_sat_b_triod 

    while yr_tbl_id >= yr_tbl_id_done:

        cur.execute('''UPDATE %s SET
                desig_g = (SELECT designation FROM G_Lections WHERE G_Lections.g_id = ?), 
                gosp = (SELECT lection FROM G_Lections WHERE G_Lections.g_id = ?),
                g_code = (SELECT code FROM G_Lections WHERE G_Lections.g_id = ?)
                WHERE id = ?''' % tn, (g_id, g_id, g_id, yr_tbl_id)) 
    
        # Update the counters... downwards:

        yr_tbl_id -= 1
        g_id -= 1


# Next we set the data associated with the Theophany.
# NB The Saturday and Sunday before the feast are marked only when they fall on Dec 31st or between Jan 2-5. We can ignore Dec 31st as that was in last year's table.

# The Saturday and Sunday before the Theophany:

    data = [("SatBT","Saturday"), ("SunBT","Sunday")]

    for code, day in data:

        cur.execute('''UPDATE %s SET
                desig_a = (SELECT designation FROM A_Lections WHERE A_Lections.code = ?), 
                apos = (SELECT lection FROM A_Lections WHERE A_Lections.code = ?),
                a_code = ?,
                desig_g = (SELECT designation FROM G_Lections WHERE G_Lections.code = ?),
                gosp = (SELECT lection FROM G_Lections WHERE G_Lections.code = ?),
                g_code = ?
                WHERE day_name = ? AND id BETWEEN 2 AND 5
                ''' % tn, (code, code, code, code, code, code, day)) 
    
# The Saturday and Sunday after the Theophany:
# NB When the Theophany falls on a Saturday, the Sunday after the Theophany is celebrated, not on the following day, but 8 days later:

    data = [("SatAT","Saturday"), ("SunAT","Sunday")]

    for code, day in data:

        if day == "Saturday": x = 7
        else: x = 8

        cur.execute('''UPDATE %s SET
                desig_a = (SELECT designation FROM A_Lections WHERE A_Lections.code = ?), 
                apos = (SELECT lection FROM A_Lections WHERE A_Lections.code = ?),
                a_code = ?,
                desig_g = (SELECT designation FROM G_Lections WHERE G_Lections.code = ?),
                gosp = (SELECT lection FROM G_Lections WHERE G_Lections.code = ?),
                g_code = ?
                WHERE day_name = ? AND id BETWEEN ? AND ?
                ''' % tn, (code, code, code, code, code, code, day, x, x+6)) 
    
#    
# Set the Sundays between the Sunday after the Theophany and the start of the Triodion
#

# What is the Year table id of the Sunday after the Theophany?

    cur.execute('''SELECT id FROM %s WHERE a_code = "SunAT"''' % tn)
    sun_a_theoph_id = cur.fetchone()[0]

# Calculate the number of weeks from the Sunday after the Theophany to the start of the Triodion
   
    suns = (triod_id - sun_a_theoph_id) // 7
  
# The number of Sundays BETWEEN these two dates is one fewer:

    suns -= 1  

# Was L14Sun used in the previous December? It is reserved for a Sunday falling on Dec 1-3, so it will have been used if December 1st was a Friday, Saturday,or Sunday.

# If weekday > 4 (i.e. it is Fri, Sat or Sun) then we use the 'b' list prepared earlier.

    if int(date(yr-1,12,1).strftime("%w")) >4: choice = "b"
    else: choice = "a"

# So which list do we choose?

    if    suns == 1: sun_list = b_triod_1        
    elif  suns == 2: sun_list = b_triod_2
    elif  suns == 3: sun_list = b_triod_3
    elif  suns == 4 and choice == "a": sun_list = b_triod_4a
    elif  suns == 4 and choice == "b": sun_list = b_triod_4b
    elif  suns == 5 and choice == "a": sun_list = b_triod_5a
    elif  suns == 5 and choice == "b": sun_list = b_triod_5b
    else: sun_list = b_triod_6

# Start with the Sunday following the Sunday after the Theophany:

    sun_id = sun_a_theoph_id +7

# Cycle through the Sundays in the appropriate list:

    for a_code, g_code in sun_list:

        cur.execute('''UPDATE %s SET
                desig_a = (SELECT designation FROM A_Lections WHERE A_Lections.code = ?), 
                apos = (SELECT lection FROM A_Lections WHERE A_Lections.code = ?),
                a_code = ?,
                desig_g = (SELECT designation FROM G_Lections WHERE G_Lections.code = ?),
                gosp = (SELECT lection FROM G_Lections WHERE G_Lections.code = ?),
                g_code = ?
                WHERE id = ?''' % tn, (a_code, a_code, a_code, g_code, g_code, g_code, sun_id)) 
    
# Update sun_id to the following Sunday:

        sun_id += 7

#
# THE PERIOD FROM BEGINNING OF THE TRIODION TO THE END OF THE YEAR
# ________________________________________________________________
    
# This presents less of a challenge.
#
# First we find the data for every day from the Monday before the Sunday of the Publican and the 
# Pharisee (start of the Triodion) to Great and Holy Saturday 
#
    day_id = triod_id-6
    lect_id = lect_id_triod-6
    
    while day_id < pascha_id:

        cur.execute('''UPDATE %s SET
                desig_a = (SELECT designation FROM A_Lections WHERE A_Lections.a_id = ?), 
                apos = (SELECT lection FROM A_Lections WHERE A_Lections.a_id = ?),
                a_code = (SELECT code FROM A_Lections WHERE A_Lections.a_id = ?),
                desig_g = (SELECT designation FROM G_Lections WHERE G_Lections.g_id = ?),
                gosp = (SELECT lection FROM G_Lections WHERE G_Lections.g_id = ?),
                g_code = (SELECT code FROM G_Lections WHERE G_Lections.g_id = ?)
                WHERE id = ?''' % tn, (lect_id, lect_id, lect_id, lect_id, lect_id, lect_id, day_id)) 
    
        # Update the counters:

        day_id += 1
        lect_id += 1
        
    # Now we find the data for every day from Pascha to the end of the year
    # For the Apostle readings and for most of the Gospels, this can be done in one
    # continuous run because the Lection tables begin with Pascha.
    # Thus the a_id and g_id for Pascha in the Lection tables is = 1.    
    #
    # We'll assume for the moment that there is no Lukan Jump and fix that later.
    
    day_id = pascha_id
    
    lect_id = 1
    
    while day_id <= end_yr_id:

        cur.execute('''UPDATE %s SET
                desig_a = (SELECT designation FROM A_Lections WHERE A_Lections.a_id = ?), 
                apos = (SELECT lection FROM A_Lections WHERE A_Lections.a_id = ?),
                a_code = (SELECT code FROM A_Lections WHERE A_Lections.a_id = ?),
                desig_g = (SELECT designation FROM G_Lections WHERE G_Lections.g_id = ?),
                gosp = (SELECT lection FROM G_Lections WHERE G_Lections.g_id = ?),
                g_code = (SELECT code FROM G_Lections WHERE G_Lections.g_id = ?)
                WHERE id = ?''' % tn, (lect_id, lect_id, lect_id, lect_id, lect_id, lect_id, day_id)) 

        # Update the counters:

        day_id += 1
        lect_id += 1
        
    # The Gospel series switches to Luke on the Monday following the Sunday
    # after the Exaltation of the Cross. This is the 'Lukan Jump'. It is therefore 
    # necessary to overwrite the Gospel lections from that date to the end of the year.

    # Find the Year table id of this date:

    cur.execute('''SELECT id FROM %s 
        WHERE month = "September" AND day_name ="Monday" AND day_num BETWEEN 16 AND 22''' % tn)
    jump_id = cur.fetchone()[0]
    
    # The code on this date is L1Mon. Find the g_id of this code on the G_Lection table

    cur.execute('''SELECT g_id FROM G_Lections WHERE code = "L1Mon"''')
    g_id = cur.fetchone()[0]

    # Armed with these references, update the Gospel Lections from the Jump to the year end

    day_id = jump_id

    while day_id <= end_yr_id:

        cur.execute('''UPDATE %s SET
                desig_g = (SELECT designation FROM G_Lections WHERE G_Lections.g_id = ?),
                gosp = (SELECT lection FROM G_Lections WHERE G_Lections.g_id = ?),
                g_code = (SELECT code FROM G_Lections WHERE G_Lections.g_id = ?)
                WHERE id = ?''' % tn, (g_id, g_id, g_id, day_id)) 

        # Update the counters:

        day_id += 1
        g_id += 1

    # Now add in the data for the Saturday and Sunday before and after the Cross.

    before_x = [("SatBX","Saturday"),("SunBX","Sunday")]

    for code, day in before_x:

        cur.execute('''UPDATE %s SET
                desig_a = (SELECT designation FROM A_Lections WHERE A_Lections.code = ?),
                apos = (SELECT lection FROM A_Lections WHERE A_Lections.code = ?),
                a_code = ?,
                desig_g = (SELECT designation FROM G_Lections WHERE G_Lections.code = ?),
                gosp = (SELECT lection FROM G_Lections WHERE G_Lections.code = ?),
                g_code = ?
                WHERE month = "September" AND day_name = ? AND day_num BETWEEN 7 AND 13
                ''' % tn, (code, code, code, code, code, code, day)) 

    after_x = [("SatAX","Saturday"),("SunAX","Sunday")]

    for code, day in after_x:

        cur.execute('''UPDATE %s SET
                desig_a = (SELECT designation FROM A_Lections WHERE A_Lections.code = ?),
                apos = (SELECT lection FROM A_Lections WHERE A_Lections.code = ?),
                a_code = ?,
                desig_g = (SELECT designation FROM G_Lections WHERE G_Lections.code = ?),
                gosp = (SELECT lection FROM G_Lections WHERE G_Lections.code = ?),
                g_code = ?
                WHERE month = "September" AND day_name = ? AND day_num BETWEEN 15 AND 21
                   ''' % tn, (code, code, code, code, code, code, day)) 

    

    # The Sundays between the Lukan Jump and the year end have some awkward variations.
    # Viz. A Sunday falling on: 
    #                       Oct 11-17 is Luke 4 & Fathers of 7th EC
    #                       Oct 30-Nov 5 is Luke 5
    #                       Nov 24-30 is Luke 13
    #                       Dec 1-3 is Luke 14
    #                       Dec 4-10 is Luke 10
    #                       Dec 11-17 is  Sunday of Holy Forefathers / Luke 11
    # Otherwise the Sundays are of Luke in sequence omitting Luke 4, 5, 10, 11, 13, 14.
    #
    # The first 2 Sundays after the Lukan Jump are, as expected, L1Sun and L2Sun.
    # The last 2 before the Nativity are always the Sunday of the Holy Forefathers and the 
    # Sunday before the Nativity.
    # All of this resolves into three patterns depending on the date of the Sunday
    # after the Exaltation of the Cross (SunAX). 

    # Get the day of the month of the Sunday after the Exaltation
    cur.execute('''SELECT day_num FROM %s 
        WHERE month = "September" AND day_name ="Sunday" AND day_num BETWEEN 15 AND 21''' % tn)
    sunax_day = cur.fetchone()[0]
    
    # If SunAX day is 15, 16 or 17:
    series_1 = ("L1Sun","L2Sun","L3Sun","L4Sun","L6Sun","L7Sun","L5Sun","L8Sun","L9Sun","L13Sun","L14Sun","L10Sun","SFF","SunBN","SunAN")   
 
    # If SunAX day is 18 or 19:
    series_2 = ("L1Sun","L2Sun","L3Sun","L4Sun","L6Sun","L5Sun","L7Sun","L8Sun","L9Sun","L13Sun","L10Sun","SFF","SunBN","SunAN")   

    # If SunAX day is 20 or 21:
    series_3 = ("L1Sun","L2Sun","L4Sun","L3Sun","L6Sun","L5Sun","L7Sun","L8Sun","L9Sun","L13Sun","L10Sun","SFF","SunBN","SunAN")   
 
    if sunax_day <18: series = series_1
    elif sunax_day < 20: series = series_2
    else: series = series_3

    sun_id = jump_id -1

    for code in series:

        sun_id += 7 
    
        cur.execute('''UPDATE %s SET
                desig_g = (SELECT designation FROM G_Lections WHERE G_Lections.code = ?),
                gosp = (SELECT lection FROM G_Lections WHERE G_Lections.code = ?),
                g_code = ?
                WHERE id = ?''' % tn, (code, code, code, sun_id)) 
        
    # Four of these Sundays have a reserved Apostle reading
    # Three of them are: SFF, SunBN, SunAN 
    
    three = ("SFF", "SunBN", "SunAN")

    for code in three:

        cur.execute('''UPDATE %s SET
                desig_a = (SELECT designation FROM A_Lections WHERE A_Lections.code = ?),
                apos = (SELECT lection FROM A_Lections WHERE A_Lections.code = ?),
                a_code = ?
                WHERE g_code = ?''' % tn, (code, code, code, code)) 

    # The fourth is L4Sun which is the Sunday of Fathers of the 7th EC ("F7EC")
                    
    cur.execute('''UPDATE %s SET
                desig_a = (SELECT designation FROM A_Lections WHERE A_Lections.code = ?),
                apos = (SELECT lection FROM A_Lections WHERE A_Lections.code = ?),
                a_code = ?
                WHERE g_code = ?''' % tn, ("F7EC", "F7EC", "F7EC", "L4Sun")) 

    # The above assumed that the Sunday before the Nativity (SunBN) would be followed by the Sunday after the Nativity. However:
    # 1. The Sunday following SunBN may fall on Dec 25th and thus be the Nativity.
    # 2. The Saturday / Sunday following SunBN may fall on Dec 31st and will designated the Sat / Sunday before the Theophany because SatAN / SunAN are not observed if they fall later than Dec 30th. 

    # 1 will be dealt with in a moment, but we must address 2 by overwriting the data. 

    code = "SatBT"

    cur.execute('''UPDATE %s SET
                desig_a = (SELECT designation FROM A_Lections WHERE A_Lections.code = ?),
                apos = (SELECT lection FROM A_Lections WHERE A_Lections.code = ?),
                a_code = ?,
                desig_g = (SELECT designation FROM G_Lections WHERE G_Lections.code = ?),
                gosp = (SELECT lection FROM G_Lections WHERE G_Lections.code = ?),
                g_code = ?
                WHERE id = ? AND day_name = "Saturday"
                ''' % tn, (code, code, code, code, code, code, end_yr_id)) 

    code = "SunBT"

    cur.execute('''UPDATE %s SET
                desig_a = (SELECT designation FROM A_Lections WHERE A_Lections.code = ?),
                apos = (SELECT lection FROM A_Lections WHERE A_Lections.code = ?),
                a_code = ?,
                desig_g = (SELECT designation FROM G_Lections WHERE G_Lections.code = ?),
                gosp = (SELECT lection FROM G_Lections WHERE G_Lections.code = ?),
                g_code = ?
                WHERE id = ? AND day_name = "Sunday"
                ''' % tn, (code, code, code, code, code, code, end_yr_id)) 

    # Set the Saturdays before and after the Nativity:
    
    code = "SatBN"

    cur.execute('''UPDATE %s SET
                desig_a = (SELECT designation FROM A_Lections WHERE A_Lections.code = ?),
                apos = (SELECT lection FROM A_Lections WHERE A_Lections.code = ?),
                a_code = ?,
                desig_g = (SELECT designation FROM G_Lections WHERE G_Lections.code = ?),
                gosp = (SELECT lection FROM G_Lections WHERE G_Lections.code = ?),
                g_code = ?
                WHERE month = "December" AND day_name = "Saturday" AND day_num BETWEEN 18 AND 24
                ''' % tn, (code, code, code, code, code, code)) 
    
    code = "SatAN"

    cur.execute('''UPDATE %s SET
                desig_a = (SELECT designation FROM A_Lections WHERE A_Lections.code = ?),
                apos = (SELECT lection FROM A_Lections WHERE A_Lections.code = ?),
                a_code = ?,
                desig_g = (SELECT designation FROM G_Lections WHERE G_Lections.code = ?),
                gosp = (SELECT lection FROM G_Lections WHERE G_Lections.code = ?),
                g_code = ?
                WHERE month = "December" AND day_name = "Saturday" AND day_num BETWEEN 26 AND 30
                ''' % tn, (code, code, code, code, code, code)) 
    

    # There are exceptions from earlier in the year that need addressing. 
 
    # The Third Sunday after Pentecost is normally for All Saints of Britain & Ireland, but if this coincides with SS Peter & Paul (Jun 29) or the Sunday of the Fathers of the 4th EC, it is deferred to the 4th after Pentecost.

    if pascha.strftime("%m-%d") in ['04-20','05-03','05-04','05-05','05-06']:
        cur.execute('''UPDATE %s SET
                desig_g = "3rd of Matthew" 
                WHERE desig_a = "3rd after Pentecost"''' % tn)
        cur.execute('''UPDATE %s SET
                desig_g = "4th of Matthew, Sunday of All Saints of Britain & Ireland" 
                WHERE desig_a = "4th after Pentecost"''' % tn)
                
    # The Sunday between July 13-19 is observed as the Sunday of the Fathers of the 4th EC (F4EC)

    cur.execute('''UPDATE %s SET
                desig_a = (SELECT designation FROM A_Lections WHERE A_Lections.code = "F4EC"), 
                apos = (SELECT lection FROM A_Lections WHERE A_Lections.code = "F4EC"),
                a_code = "F4EC",       
                desig_g = (SELECT designation FROM G_Lections WHERE G_Lections.code = "F4EC"),
                gosp = (SELECT lection FROM G_Lections WHERE G_Lections.code = "F4EC"),
                g_code = "F4EC"
                WHERE month = "July" AND day_name = "Sunday" AND day_num BETWEEN 13 AND 19''' % tn)

    
    # The four fixed-date feasts of Our Lord, viz, the Exaltation of the Cross, the Nativity
    # the Theophany and the Transifiguration, need no daily readings. All the data will be
    # supplied from the Menaion table. We therefore clear these dates:

    cross = str(yr) + "-09-14"
    nativity = str(yr) + "-12-25"
    theoph = str(yr) + "-01-06"
    transfig = str(yr) + "-08-06"

    cur.execute(
            '''UPDATE %s SET a_code = Null, g_code = Null, desig_a = Null, desig_g = Null,
            apos = Null, gosp = Null
            WHERE date IN (?, ?, ?, ?)''' % tn, (cross, nativity, theoph, transfig))

    #
    # Now add the extra Lections for those few days for which they are appointed
    #

    cur.execute('''SELECT extra, code FROM G_Lections WHERE extra != "" ''')
    data = cur.fetchall()

    for extra, code in data:
        x_code = "x"+code
        cur.execute(
            '''UPDATE %s SET extra = ?, x_code = ? WHERE g_code = ?''' % tn, (extra, x_code, code))

    #
    # Finally mark in the 'Basil' column the occasions when the Liturgy of St Basil is used.
    #

    text = "Liturgy of St Basil"
 
    # 1. The five Sundays of Lent, Holy Thursday and Holy Saturday. We use the codes:

    basils = ('G1Sun', 'G2Sun', 'G3Sun', 'G4Sun', 'G5Sun', 'G7Thu', 'G7Sat')
    for basil in basils:
        cur.execute(
                '''UPDATE %s SET basil = ? WHERE a_code = ?''' % tn, (text, basil))

    # 2. The feast of St Basil, January 1st. Use the date_key:

    basil = "01-01"    
    cur.execute(
            '''UPDATE %s SET basil = ? WHERE date_key = ?''' % tn, (text,basil))

    # 3. The Eve the Nativity and of the Theophany if Monday - Friday. Use the date_key:

    basils = ('01-05','12-24')
    for basil in basils:
        cur.execute(
                '''UPDATE %s SET basil = ? WHERE date_key = ? AND day_name NOT IN ("Saturday","Sunday")''' % tn, (text,basil))

    # 4. The Nativity and the Theophany if a Sunday or Monday. Use the date_key:

    basils = ('01-06','12-25')
    for basil in basils:
        cur.execute(
                '''UPDATE %s SET basil = ? WHERE date_key = ? AND day_name IN ("Sunday","Monday")''' % tn, (text,basil))

    # Move on to the next year:

    yr += 1

# write to database, close it and sign off
cur.execute("COMMIT")

cal.close()

print('Finished stage 4')

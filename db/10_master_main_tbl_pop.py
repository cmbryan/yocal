#!/usr/bin/python3
# York Orthodox Calendar Project v2
# Fr Deacon David Hoskin   2018

# Dependencies: python3, sqlite3, apsw python sqlite wrapper.

# Populate the yocal_main table of YOCal_master.db from the Year tables of YOCal.db

import apsw
import sys

yr = int(sys.argv[1]) if len(sys.argv) > 1 else None
yr_final = int(sys.argv[2]) if len(sys.argv) > 2 else None

cal = apsw.Connection('YOCal.db')
cur = cal.cursor()

# Get the first and last years to have a table in the database.
# This gives a max and min for the range of yoars created in the new database.

# Set initial values and scan for the actual values.
yr_first = 1999         # We scan upwards from here
yr_last = 2100   # We scan downwards from here

name = ''
while name == '' and yr_first < 2100:
   yr_first += 1
   cur.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name= ?''', ('Year_'+str(yr_first),))
   name = cur.fetchone()
   if not name: name = ''

name = ''
while name == '' and yr_last > 1999:
   yr_last -= 1
   cur.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name= ?''', ('Year_'+str(yr_last),))
   name = cur.fetchone()
   if not name: name = ''

if yr is None:
   # Get the range of years for which tables will be created
   print('A continuous series of year tables can be created betwenn 2000 and 2099') 
   yr = int(input('Please enter the start year: '))

assert yr_first <= yr <= yr_last, f'Please enter a starting year between {yr_first} and {yr_last}'

if yr_final is None:
   yr_final_ = int(input('Please enter the final year for the new database: '))

assert yr <= yr_final <= yr_last, f'Please enter a final year between {yr} and {yr_last}'

print(f'Tables for the years {yr}-{yr_final} will be populated')

# Attach the YOCal_Master.db

cur.execute('''ATTACH DATABASE 'YOCal_Master.db' as master''')

# Begin:

cur.execute("BEGIN TRANSACTION")

# Cycle through the range of years:

while yr <= yr_final:

    tn = "Year_" + str(yr)

    # Add everything except explanatory_notes
    cur.execute('''INSERT INTO master.yocal_main
               SELECT 
               date, day_name, day_num, ord, month, year, fast, tone, eothinon, desig_a, desig_g,
               major_commem, fore_after, basil, class_5, british,
               a_code, g_code, c_code, x_code, is_comm_apos, is_comm_gosp, NULL
               FROM %s''' % tn)

    yr += 1

# Add explanatory notes
with open('explanatory_notes.csv','r') as fh:
    for row in fh:
        if row:
            date, text = row.split('|')
            cur.execute('''
                UPDATE master.yocal_main
                SET explanatory_notes = ?
                WHERE date = ?
            ''', (text.rstrip(), date))

cur.execute("COMMIT")

cur.execute('''DETACH master''')

cal.close()

print('Finished stage 10')
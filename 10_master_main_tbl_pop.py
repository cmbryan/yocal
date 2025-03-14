#!/usr/bin/python3
# York Orthodox Calendar Project v2
# Fr Deacon David Hoskin   2018

# Dependencies: python3, sqlite3, apsw python sqlite wrapper.

# Populate the yocal_main table of YOCal_master.db from the Year tables of YOCal.db

import apsw

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

yr_ = input('Please enter the start year for the new database: ')
yr = int(yr_)
if yr < yr_first or yr > yr_last: 
   yr_ = input('That is not a valid response. One more try: ')
   yr = int(yr_)
   if yr < yr_first or yr > yr_last: sys.exit

yr_final_ = input('Please enter the final year for the new database: ')
yr_final = int(yr_final_)
if yr_final < yr or yr_final > yr_last: 
   yr_final_ = input('That is not a valid response. One more try: ')
   yr_final = int(yr_final_)

   if yr_final < yr or yr_final > yr_last: sys.exit

print('Tables for the years '+yr_+'-'+yr_final_+' will be populated')

# Attach the YOCal_Master.db

cur.execute('''ATTACH DATABASE 'YOCal_Master.db' as master''')

# Begin:

cur.execute("BEGIN TRANSACTION")

# Cycle through the range of years:

while yr <= yr_final:

    tn = "Year_" + str(yr)

    cur.execute('''INSERT INTO master.yocal_main
               SELECT 
               date, day_name, day_num, ord, month, year, fast, tone, eothinon, desig_a, desig_g,
               major_commem, fore_after, basil, class_5, british,
               a_code, g_code, c_code, x_code, is_comm_apos, is_comm_gosp
               FROM %s''' % tn)

    yr += 1


cur.execute("COMMIT")

cur.execute('''DETACH master''')

cal.close()

x = input('\n   All done... Press Enter to exit')

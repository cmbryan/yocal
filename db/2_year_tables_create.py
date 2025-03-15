#!/usr/bin/python3
# York Orthodox Calendar Project v2
# Fr Deacon David Hoskin   2018

# Dependencies: python3, sqlite3, apsw python sqlite wrapper.

# Creates Year Tables.
# These are then populated using the scripts which follow.
#
# It might be thought superfluous to include a 'year' column as 
# this remains constant for each year. However, the presence of
# this column makes life easier when contructing multi-year, or 
# liturgical year resources from a combination of Year tables.

# First import the SQLite wrapper for Python:

import apsw
import sys

yr = int(sys.argv[1]) if len(sys.argv) > 1 else None
yr_final = int(sys.argv[2]) if len(sys.argv) > 2 else None

if yr is None:
   # Get the range of years for which tables will be created
   print('A continuous series of year tables can be created betwenn 2000 and 2099') 
   yr = int(input('Please enter the start year: '))

assert 2000 <= yr <= 2099, 'Please enter a year between 2000 and 2099'

if yr_final is None:
   yr_final = int(input('Please enter the final year: '))

assert yr <= yr_final <= 2099, 'Please enter a year between 2000 and 2099'

print(f'Tables for the years {yr}-{yr_final} will be created')

# Open the database as 'cal' and set the cursor to 'cur':
cal = apsw.Connection('YOCal.db')
cur = cal.cursor()

# Begin:
cur.execute("BEGIN TRANSACTION")

# Create a year table for each year of the given series:

while yr <= yr_final:
    tn = "Year_" + str(yr)
    cur.execute('''CREATE TABLE %s (
            id INTEGER PRIMARY KEY,
            date DATE,
            date_key TEXT,
            day_name TEXT,
            day_num INTEGER,
            ord TEXT,
            month TEXT,
            year INTEGER,
            fast TEXT,
            tone INTEGER,
            eothinon INTEGER,
            desig_a TEXT,
            desig_g TEXT,
            major_commem TEXT,
            fore_after TEXT,
            season TEXT,
            basil INTEGER,
            class_5 TEXT,
            british TEXT,
            apos TEXT,
            gosp TEXT,
            apos_comm TEXT,
            gosp_comm TEXT,
            extra TEXT,
            is_comm_apos INTEGER, 
            is_comm_gosp INTEGER, 
            a_code TEXT,
            g_code TEXT,
            c_code,
            x_code
    )''' % tn)
  
    yr += 1

# Write the data to the database, close it and sign off: 

cur.execute("COMMIT")

cal.close()

print('Finished stage 2')
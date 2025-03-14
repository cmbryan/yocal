#!/usr/bin/python3
# York Orthodox Calendar Project v2
# Fr Deacon David Hoskin   2018

# Dependencies: python3, sqlite3, apsw python sqlite wrapper.

# Creates a Master Table in a new database.

import apsw

cal = apsw.Connection('YOCal_Master.db')
cur = cal.cursor()

# Begin:

cur.execute("BEGIN TRANSACTION")

# Create the Main table:

#cur.execute('''CREATE TABLE yocal_main (
#            date DATE,
#            day_name TEXT,
#            day_num INTEGER,
#            ord TEXT,
#            month TEXT,
#            year INTEGER,
#            fast TEXT,
#            tone TEXT,
#            eothinon TEXT,
#            desig_a TEXT,
#            desig_g TEXT,
#            major_commem TEXT,
#            fore_after TEXT,
#            basil TEXT,
#            class_5 TEXT,
#            british TEXT,
#            a_code TEXT,
#            g_code TEXT,
#            c_code TEXT,
#            x_code TEXT,
#            is_comm_apos INTEGER, 
#            is_comm_gosp INTEGER
#            )''')

# Create the Lection table:

cur.execute('''CREATE TABLE yocal_lections (
            code TEXT,
            lect_1 TEXT,
            text_1 TEXT,
            lect_2 TEXT,
            text_2 TEXT,
            mod_1 TEXT,
            mod_2 TEXT,
            id INTEGER PRIMARY KEY AUTOINCREMENT            
            )''')

cur.execute("COMMIT")

cal.close()

x = input('\n   All done... Press Enter to exit')

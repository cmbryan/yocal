#!/usr/bin/python3
# York Orthodox Calendar Project
# Fr Deacon David Hoskin   2019

# =============================================================================
# This script selects data from the yocal_lections table of YOCal_Master.db 
# and writes an sql file in MySQL format.
# This sql file can then be used to import the table into the website database. 
# Please note that any existing web table of the same name must first be dropped.

# [NB The script 'util_correct_sql_file_for_upload.py' is now redundant.]
# =============================================================================

# First import the SQLite wrapper for Python:

import apsw

# Open the database as 'cal' and set the cursor to 'cur':

cal = apsw.Connection('YOCal_Master.db')
cur = cal.cursor()

# Get the name of the table which the sql file will create:

# tbl = input('\nThe table on the website is currently named either "yocal_lections" (1),\n or "yocal_lections2" (2)? \n Please enter 1 or 2 for these option or enter the table name of your choice:\n')
# if tbl == "1": table = "yocal_lections"
# elif tbl == "2": table = "yocal_lections2"
# else: table = tbl

table = "yocal_lections2"

# Get a name for the sql file and open it for writing

v = input('\nThe file created will be named <' + table + '_vN_upload.sql>\n Please enter the version number: ')

file_name = 'SQL_uploads/' + table + '_v' + v + '_upload.sql'
f = open(file_name, "w+")

# Begin:

cur.execute("BEGIN TRANSACTION")

# Add the 'Create Table' statement:

txt = "CREATE TABLE "+table+" (code TEXT NULL,lect_1 TEXT NULL,text_1 MEDIUMTEXT NULL,lect_2 TEXT NULL,text_2 MEDIUMTEXT NULL);\n" 

# Get the number of rows
cur.execute("""SELECT COUNT(*) FROM yocal_lections""")
end = cur.fetchone()[0]
print(end)
# Get the lection data row by row using it to create an 'Insert Into' statement:

header = "INSERT INTO " + table + " (code,lect_1,text_1,lect_2,text_2) VALUES ("
tail = ");\n"

entry = 1
while entry <= end:
   cur.execute('''SELECT code, lect_1, text_1, lect_2, text_2 FROM yocal_lections WHERE rowid = ?''', (entry,))
   data = cur.fetchone()
   txt += header

   for datum in data:
      if datum != '' and datum is not None:
         # Escape all apostrophes:
         datum = datum.replace("'","''")
      else: datum = ''
      # Enclose each item in single quotes and add a final comma
      txt += "'" + datum + "',"

   # strip the final comma and add the tail instead
   txt = txt.rstrip(',')
   txt += tail

   # update the index
   entry += 1

# Strip the final line-break
txt = txt.rstrip('\n')

cur.execute("COMMIT")

# Write the complete text to file
f.write(txt)

# Close everything
f.close()
cal.close()

# Report back
print("\nThe file <" + file_name + "> has been created and saved.")
x = input('   ... Press Enter to exit')

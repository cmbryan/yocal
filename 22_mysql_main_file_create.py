#!/usr/bin/python3
# York Orthodox Calendar Project
# Fr Deacon David Hoskin   2019

# =============================================================================
# This script selects data from the yocal_main table of YOCal_Master.db
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

tbl = input('\nThe table on the website is currently named "yocal_main"\n Press ENTER to keep this name or enter the table name of your choice:\n')
if tbl == "": table = "yocal_main"
else: table = tbl

# Get a name for the sql file and open it for writing

v = input('\nThe file created will be named <' + table + '_vN_upload.sql>\n Please enter the version number: ')

file_name = 'SQL_uploads/' + table + '_v' + v + '_upload.sql'
f = open(file_name, "w+")

# Begin:

cur.execute("BEGIN TRANSACTION")

# Add the 'Create Table' statement:

txt = "CREATE TABLE "+table+" (date_full DATE, day_name TEXT, day_num INTEGER, ord TEXT, mnth TEXT, yr INTEGER, fast TEXT, tone TEXT, eothinon TEXT, desig_a TEXT, desig_g TEXT, major_commem TEXT, fore_after TEXT, basil TEXT, class_5 TEXT, british TEXT, a_code TEXT, g_code TEXT, c_code TEXT, x_code TEXT, is_comm_apos INTEGER, is_comm_gosp INTEGER);\n"

# Get the number of rows
cur.execute("""SELECT COUNT(*) FROM yocal_main""")
end = cur.fetchone()[0]

# Get the data row by row using it to create an 'Insert Into' statement:
entry = 1
header = "INSERT INTO " + table + " VALUES ("
tail = ");\n"

while entry <= end:
   cur.execute('''SELECT * FROM yocal_main WHERE rowid = ?''', (entry,))
   data = cur.fetchone()
   txt += header

   for datum in data:
      # Change None type to empty string
#      if datum == None: datum =''

      # Escape all apostrophes in text values but ignore integers:
      if type(datum) == int and datum <1:
         datum = 0
         print(datum)
      if not str(datum).isdigit():
         if datum == None: datum =''
         datum = datum.replace("'","''")
         # Enclose each item in single quotes
         datum = "'"+datum+"'"
      # Add to text with a final comma
      txt += str(datum) + ","

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

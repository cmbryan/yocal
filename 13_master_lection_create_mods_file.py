#!/usr/bin/python3
# York Orthodox Calendar Project
# Fr Deacon David Hoskin   2018

# ==================================================================================
# This script creates a .csv file of Lection corrections from the given database  ==================================================================================

# First import the SQLite wrapper for Python:

import apsw

db_name = input('Give the filename of the source database.\nFor YOCal_Master.db press Enter: ')
if db_name == '': db_name = 'YOCal_Master.db'
print('\n')

# Open the database as 'cal' and set the cursor to 'cur':

cal = apsw.Connection(db_name)
cur = cal.cursor()

cur.execute('''SELECT COUNT(code) FROM yocal_lections''')
records = cur.fetchone()[0]

# Cycle through the records, collecting the data

record = 1
txt = ''
while record < records + 1:
   code = mod_1 = mod_2 = ''
   print('\033[A   ',record,'    ')
   cur.execute('''SELECT * FROM yocal_lections WHERE id = %d''' % record)
   data = cur.fetchone() 
   code = data[0]
   if data[5]: mod_1 = data[5].replace('\n','%')
   if data[6]: mod_2 = data[6].replace('\n','%')

   txt += code + '\t' + mod_1 + '\t' + mod_2 + '\n'
   
   record += 1
   
txt = txt[:-1]

file_out = input('\nEnter the name of the .csv file to be written\nFor mods.csv press Enter: ')
if file_out == '': file_out = 'mods.csv'

# Open the output file and write the text 
f_out = open(file_out, 'w')
f_out.write(txt)

# Close output files
f_out.close()

# Close the database and report back: 
cal.close()
print('\n... The file ' + file_out + ' has been saved in the DB folder.\n')
x = input('   ... Press Enter to exit')

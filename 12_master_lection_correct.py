#!/usr/bin/python3
# York Orthodox Calendar Project
# Fr Deacon David Hoskin   2018

# ==================================================================================
# This script makes appropriate corrections to the lections: 
#  1.To the opening words where the entry point is part way through a verse or
#    where a preposition referring back to a previous verse is not easily understood.
#  2.Where parts of verses need to be moved or removed - e.g. Luke 8:5-8a, 9-15, 8b
# It should be run after the table has been populated by script 10.
# It renders script 11b redundant. 
# ==================================================================================

# First import the SQLite wrapper for Python:

import apsw

# Open the database as 'cal' and set the cursor to 'cur':

cal = apsw.Connection('YOCal_Master.db')
cur = cal.cursor()

# Begin:

cur.execute("BEGIN TRANSACTION")

cur.execute('''SELECT COUNT(code) FROM yocal_lections''')
records = cur.fetchone()[0]

# Create a list of codes with a mod but did not need updating
no_mod = ["These mods may be redundant: ",]

def emend(txt,mod):
   global no_mod
   flag = 0
   items = mod.split('\n')
   for item in items:
      mods = item.split('|')
      if len(mods) != 2:    # If not two items: flag 1000 and return.
         flag = 1000
         pass
      elif txt.find(mods[0]) >0:  # Update needed: set text, update flag.
         txt = txt.replace(mods[0],mods[1])
         flag += 1
      elif txt.find(mods[1]) >0:
         no_mod.append(code)   # Text already updated: Why?
         no_mod.append(mods[0])
      else: flag = 1000                 # Texts do not match: flag 1000.
   return txt,flag

# Cycle through the records, correcting text_1 and text_2 from mod_1 and mod_2

record = 1
print('\n')

while record < records + 1:
   tmp_txt = ''
   cur.execute('''SELECT * FROM yocal_lections WHERE id = %d''' % record)
   data = cur.fetchone() 
   code = data[0]
   txt_1 = data[2]
   txt_2 = data[4]
   mod_1 = data[5]
   mod_2 = data[6]

# Emend the text for each reading. 
# The returned value of n_txt is [txt, flag]:
#   - If flag > 999 neither the search or replace values were found.
#   - If flag == 0 the text is already emended: no need to do anything.
#   - If flag > 0 the emended text is used to update the DB.
 
   if txt_1 and mod_1:
      n_txt = emend(txt_1,mod_1) 
      if n_txt[1] > 999:
        tmp_txt = '     Problem: ' + code + ' - text/mod 1\n\n'
      elif n_txt[1] > 0:
         cur.execute('''UPDATE yocal_lections SET text_1 = ? WHERE code = ?''' , (n_txt[0],code))

   if txt_2 and mod_2:
      n_txt = emend(txt_2,mod_2) 
      if n_txt[1] > 999:
        tmp_txt += '     Problem: ' + code + ' - text/mod 2\n\n'
      elif n_txt[1] > 0:
         cur.execute('''UPDATE yocal_lections SET text_2 = ? WHERE code = ?''' , (n_txt[0],code))

   print('\033[A   ',record, tmp_txt)
   record += 1

# Write the data to the database, close it and report back: 

cur.execute('COMMIT') 
cal.close()
if len(no_mod) < 50 and len(no_mod) > 1: print(no_mod,'\n')
print('\033[A   ... All done\n')

x = input('   ... Press Enter to exit')

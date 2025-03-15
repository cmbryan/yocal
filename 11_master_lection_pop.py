#!/usr/bin/python3
# York Orthodox Calendar Project
# Fr Deacon David Hoskin   2018

# This script supplies the text of the readings to the Lection table.

# First import the 're' module and the SQLite wrapper for Python:

import os
import re
import apsw

# Open the database as 'cal' and set the cursor to 'cur'
# and attach YOCal_Master.db as master:
cal = apsw.Connection('YOCal.db')
cur = cal.cursor()
cur.execute('''ATTACH DATABASE 'YOCal_Master.db' as master''')

# Begin:
cur.execute("BEGIN TRANSACTION")

# Is the lections table already populated?
# If not, populate the code, lect_1, lect_2 columns.  
cur.execute('''SELECT COUNT(code) FROM master.yocal_lections''')
records = cur.fetchone()[0]
if records < 2:

   # First the unique Gospel codes
   cur.execute('''INSERT INTO master.yocal_lections (code)
               SELECT (code) FROM G_Lections 
               WHERE (code LIKE 'J%' OR code LIKE 'M%' OR code LIKE 'L%')''')

   # Then the Apostle codes and lections
   cur.execute('''INSERT INTO master.yocal_lections (code, lect_1)
               SELECT code, lection FROM A_Lections''')

   # Then update lect_2 for codes which appear in the Gospel table
   cur.execute('''SELECT code, lection FROM G_Lections''')
   result = cur.fetchall()
   for a, b in result:
      cur.execute('''UPDATE master.yocal_lections SET lect_2 = ? WHERE code = ?''' , (b,a))

   # Now create new codes and entries where there are extra lections
   extra = ['L18Sat','G7Wed']
   for ext in extra:
      x = 'x' + ext
      cur.execute('''SELECT extra FROM G_Lections WHERE code = ?''',(ext,))
      lect = cur.fetchone()[0]
      if ext == 'G7Wed':
         cur.execute('''INSERT INTO master.yocal_lections (code, lect_1) VALUES (?,?)''', (x,lect))
      else:
         two_lect = lect.split('; ')
         cur.execute('''INSERT INTO master.yocal_lections (code, lect_1, lect_2) VALUES (?,?,?)''', (x,two_lect[0],two_lect[1]))


   # Now add entries for the lections from the Menaion table.
   cur.execute('''INSERT INTO master.yocal_lections (code, lect_1, lect_2)
               SELECT date_key, apostle, gospel FROM Menaion WHERE apostle IS NOT '' ''')

   # Finally add entries from the X_Lections table
   cur.execute('''INSERT INTO master.yocal_lections (code, lect_1, lect_2)
               SELECT code, apostle, gospel FROM X_Lections''')

                
else: input('The code and lection fields are already populated. ENTER continue.')

# The first five letters of the Book uniquely identify it.
# Provide dictionaries to give the Bible Book No. and the Book Name

Bible = {
   'Matth':'41|MAT|Matthew|According to Matthew',
   'Mark ':'42|MRK|Mark|According to Mark',
   'Luke ':'43|LUK|Luke|According to Luke',
   'John ':'44|JHN|John|According to John',
   'Acts ':'45|ACT|Acts|Acts of the Apostles',
   'Roman':'46|ROM|Romans|Letter to the Romans',
   '1 Cor':'47|1CO|1 Corinthians|First Letter to the Corinthians',
   '2 Cor':'48|2CO|2 Corinthians|Second Letter to the Corinthians',
   'Galat':'49|GAL|Galatians|Letter to the Galatians',
   'Ephes':'50|EPH|Ephesians|Letter to the Ephesians',
   'Phili':'51|PHP|Philippians|Letter to the Philippians',
   'Colos':'52|COL|Colossians|Letter to the Colossians',
   '1 The':'53|1TH|1 Thessalonians|First Letter to the Thessalonians',
   '2 The':'54|2TH|2 Thessalonians|Second Letter to the Thessalonians',
   '1 Tim':'55|1TI|1 Timothy|First Letter to Timothy',
   '2 Tim':'56|2TI|2 Timothy|Second Letter to Timothy',
   'Titus':'57|TIT|Titus|Letter to Titus',
   'Phile':'58|PHM|Philemon|Letter to Philemon',
   'Hebre':'59|HEB|Hebrews|Letter to the Hebrews',
   'James':'60|JAS|James|Letter of James',
   '1 Pet':'61|1PE|1 Peter|First Letter of Peter',
   '2 Pet':'62|2PE|2 Peter|Second Letter of Peter',
   '1 Joh':'63|1JN|1 John|First Letter of John',
   '2 Joh':'64|2JN|2 John|Second Letter of John',
   '3 Joh':'65|3JN|3 John|Third Letter of John',
   'Jude ':'66|JUD|Jude|Letter of Jude',
   'Revel':'67|REV|Revelation|Revelation to John',
   'Genes':'01|GEN|Genesis|Genesis',
   'Exodu':'02|EXO|Exodus|Exodus',
   'Levit':'03|LEV|Leviticus|Leviticus',
   'Numbe':'04|NUM|Numbers|Numbers',
   'Deute':'05|DEU|Deuteronomy|Deuteronomy',
   'Joshu':'06|JOS|Joshua|Joshua',
   'Judge':'07|JDG|Judges|Judges',
   'Ruth ':'08|RUT|Ruth|Ruth',
   '1 Kin':'09|1SA|1 Kingdoms|The First book of Kingdoms',
   '2 Kin':'10|2SA|2 Kingdoms|The Second book of Kingdoms',
   '3 Kin':'11|1KI|3 Kingdoms|The Third book of Kingdoms',
   '4 Kin':'12|2KI|4 Kingdoms|The Fourth book of Kingdoms',
   '1 Chr':'13|1CH|1 Paralipomenon|The First book of Paralipomenon',
   '2 Chr':'14|2CH|2 Paralipomenon|The Second book of Paralipomenon',
   '2 Esd':'15|EZR|2 Esdras|The Second book of Esdras',
   'Nehem':'16|NEH|Nehemiah|Nehemiah', 
   'Esthe':'70|ESG|Esther|Esther', 
   'Job  ':'18|JOB|Job|Job', 
   'Psalm':'19|PSA|Psalms|The Psalms of David', 
   'Prove':'20|PRO|Proverbs|Proverbs of solomon', 
   'Eccle':'21|ECC|Ecclesiastes|Ecclesiastes', 
   'Song ':'22|SNG|Song of songs|Song of Songs', 
   'Isaia':'23|ISA|Isaiah|Isaiah',
   'Jerem':'24|JER|Jeremiah|Jeremiah', 
   'Lamen':'25|LAM|Lamentations|The Lamentations of Jeremiah', 
   'Ezeki':'26|EZK|Ezekiel|Ezekiel',
   'Danie':'B2|DAG|Daniel|Daniel',
   'Hosea':'28|HOS|Hosea|Hosea',
   'Joel ':'29|JOL|Joel|Joel',
   'Amos ':'30|AMO|Amos|Amos',
   'Obadi':'31|OBA|Obadiah|Obadiah', 
   'Jonah':'32|JON|Jonah|Jonah',
   'Micah':'33|MIC|Micah|Micah',
   'Nahum':'34|NAM|Nahum|Nahum',
   'Habak':'35|HAB|Habakkuk|Habakkuk', 
   'Zepha':'36|ZEP|Zephaniah|Zephaniah', 
   'Hagga':'37|HAG|Haggai|Haggai',
   'Zecha':'38|ZEC|Zechariah|Zechariah', 
   'Malac':'39|MAL|Malachi|Malachi',
   '1 Esd':'82|1ES|1 Esdras|The First book of Esdras',
   'Tobit':'68|TOB|Tobit|Tobit',
   'Judit':'69|JDT|Judith|Judith',
   '1 Mac':'78|1MA|1 Maccabees|The First book of Maccabees',
   '2 Mac':'79|2MA|2 Maccabees|The Second book of Maccabees',
   '3 Mac':'80|3MA|3 Maccabees|The Third book of Maccabees',
   '4 Mac':'81|4MA|4 Maccabees|The Fourth book of Maccabees',
   'Wisdo':'71|WIS|Wisdom of Solomon|Wisdom of Solomon',
   'Sirac':'72|SIR|Sirach|Wisdom of Sirach',
   'Epist':'74|LJE|Epistle of Jeremiah|An Epistle of Jeremiah',
   'Baruc':'73|BAR|Baruch|Baruch',
   'Susan':'76|SUS|Susanna|Susanna',
   'Hymn ':'75|S3Y|Hymn of the Three Holy Children|The Hymn of the Three Holy Children',
   'Bel a':'77|BEL|Bel and the Dragon|Bel and the Dragon' 
}

# --------------------------------------------------------
# Function to pre-format a given reference into bite-sized bits.
# The bits are passed in turn to the following function to get the text.
# The returned chunks of text are then assembled. 
# --------------------------------------------------------

def lect_txt(lection):
   txt = ""

# Each complete reference ends with "; ". Split the text here.
   lects = lection.split("; ")
   txt = ""
   for lect in lects:

# If there is a header such as "Vespers: ", split it off for use later.
      if (lect.find(": ")>0):
         splits = lect.split(": ")
         lect = splits[1]
         header = splits[0]+": \n<br>"
         
         print(lect," ",header)
      else: header = ""

# If the reference is a problem, simplify it and correct manually.
      if lect == 'Luke 8:5-8a, 9-15, 8b': lect = "Luke 8:5-8a,9-15,8b"
      true_lect = lect
      if lect == "Luke 8:5-8a,9-15,8b":
         lect = "Luke 8:5-15"

# The txt containing any header and the reference itself duly formatted.
      txt = txt+"<em>"+header+true_lect+"</em><br>"

   # Identify the Book from the lection 'lect' and get its details
      book = lect[0:5]
      book = re.sub(r'\d$',r' ',book)

   # If the reference has not been found, tell us about it. 
      if book not in Bible: print("\nProblem lection: ",lect + '\n')         

      else:
         info = Bible[book].split('|')
         bk_num = info[0]
         bk_code = info[1]
         bk_name = info[2]

   # Is the reading from the OT?
         try: bk_num_int = int(bk_num)
         except: bk_num_int = 1
         if bk_num_int not in range(41,67):
            global OT_rdg
            OT_rdg = 1

      # From the lection, discard the bk name 
      # leaving the chapter and verse data 'ref'
         bk_len = len(bk_name)
         ref = lect[bk_len+1:]

      # Find the name of the book source file and open it
         f_name = f'USFM/{bk_num}{bk_code}OBBE.SFM'
         if not os.path.exists(f_name):
            f_name = f'USFM/{bk_num}{bk_code}_obbe.SFM'
         f = open(f_name,'r')
      # Split up the ref so that each fragment can be retrieved.  
      # The initial chapter num is followed by ':', so split it off.
         chap = ref.split(':')[0]

      # If there are any ';' (there shouldn't be) 
      # divide at this point into blocks.
         blocks = ref.split(";")
         for block in blocks:
            block = block.strip()

          # Divide into parts at the commas. 
          # These many mark a new chapter, or another group of verses. 
            parts = block.split(",")
            for part in parts:
               part = part.strip()

              # '-' indicates a range. 
              # Again, this may or may not include a change of chapter.
               segs = part.split('-')
               seg1 = segs[0]

              # If there is a new chapter shown by the presence of a ':'
              # Shred seg1 at that point into the start chapter and verse.
               if (seg1.count(':') > 0):
                  shred = seg1.split(':')
                  ch_begin = shred[0]
                  chap = ch_begin
                  vs_begin = shred[1]

              # Otherwise the initial chapter num prevails, 
              # and seg1 contains the start verse. 
               else:
                  ch_begin = chap
                  vs_begin = seg1         

              # If there is a range, shown by a '-', 
              # then get the end of the range from seg2
              # Shred, if necessary, as before to get a new chapter.
               if (part.count('-') > 0):
                  seg2 = segs[1]
                  if (seg2.count(':') > 0):
                     shred = seg2.split(':')
                     ch_end = shred[0]
                     chap = ch_end
                     vs_end = shred[1]
                  else:
                     ch_end = chap
                     vs_end = seg2
               else:
                  ch_end = ch_begin
                  vs_end = vs_begin

               # Finally get the text using the get_txt function 
               # and add it to our master 'txt' together with a '…'
               # so that breaks in the continuity of the reading are identified.
               txt += get_txt(ch_begin, vs_begin, ch_end, vs_end, f)+" … "

               # As the loop completes, the whole text is assembled

         # Remove the trailing unneeded '…' and any spaces.
         txt = re.sub(r'… $','',txt)
         txt = txt.strip()

         # Remove redundant quotation marks from interrupted speech
         txt = re.sub(r'’ … ‘',' … ',txt)

         #  Ensure reading ends with full stop
         if txt[-1:].isalpha(): txt += '.'
         if txt[-1:] in (';', ':', ','): txt = txt[:-1] + '.'
         if txt[-2:] == ' –': txt = txt[:-2] + '.'
         if txt[-1:] == '’':
            if txt[-2:-1].isalpha(): txt = txt[:-1] + '.’'
            if txt[-2:-1] in (';', ':', ','): txt = txt[:-2] + '.’'
            if txt[-3:-1] == ' –': txt = txt[:-3] + '.’'

         # Square brackets are removed
         txt = txt.replace('[','')
         txt = txt.replace(']','')

         txt += '<br><br>'
         
         f.close()

   return (txt)

# ---------------
# End of Function
# ---------------

# -------------------------------------------------------------
# Function to get the text from a pre-formatted reference.
# This function is called recursively by the previous function.
# -------------------------------------------------------------
 
def get_txt(ch_b, vs_b, ch_e, vs_e, f):
   txt1 = ''
   line = ''
   f.seek(0)              

   # Lines of text are checked until the start references are found.
   # The text is then read line by line until the end references are found.
   while ('\\c ' + ch_b) not in line:
      line=f.readline()
   while ('\\v ' + vs_b) not in line:
      line=f.readline()
   txt1 = line      
   if ch_e == ch_b:
      while ('\\v ' + vs_e) not in line:
         line=f.readline()
         txt1 += line
   else:
      while ('\\c ' + ch_e) not in line:
         line=f.readline()
         txt1 += line
      while ('\\v ' + vs_e) not in line:
         line=f.readline()
         txt1 += line

   # The final verse may contain >1 line of text, so keep reading.
   # Stop when a new chapter or verse is found or EOF is reached (line == '').

   line=f.readline()
   while '\\v' not in line and '\\c' not in line and line != '':
      txt1 += line
      line=f.readline()

   #  Ensure reading does not begin or end with spaces

   txt1 = txt1.strip() 

   # The text is stripped of its codes
   txt1 = re.sub(r'(\\s.*\n)','',txt1)
   txt1 = re.sub(r'(\\c.*\n)','',txt1)
   txt1 = re.sub(r'(\\v \d+ )','',txt1)
   txt1 = re.sub(r'(\\q3 *(\n)*)','<br>&emsp;',txt1)
   txt1 = re.sub(r'(\\q4 *(\n)*)','<br>&emsp;&emsp;',txt1)
   txt1 = re.sub(r'(\\qx *)','<br><br>',txt1)
   txt1 = re.sub(r'(\\q\d* *)','',txt1)
   txt1 = re.sub(r'(\\m *)','',txt1)
   txt1 = re.sub(r'(\\rq.*\\rq\*)','',txt1)
   # txt1 = re.sub(r'(\\f.*\\f\*)','',txt1)

   # Lines are joined by replacing new lines with a space
   txt1 = re.sub(r'(\n)',' ',txt1)

 # Footnotes are removed
   while txt1.count('\\f +') > 0:
         subtxt1 = txt1.split('\\f +',1)[0]
         subtxt2 = txt1.split('\\f*',1)[1]
         txt1 = subtxt1 + subtxt2

   # Paragraph codes stripped.
   # In the case of \pi3 the new line and intent are retained
   # txt1 = re.sub(r'(\\pi3\\n‘)','\\n   ',txt1)
  # txt1 = re.sub(r'(\\pi3 *‘)','<br>   ',txt1)
  # In the case of \pi the opening quotation mark of the new para is removed 
   # - but first we need to know if any exist
   pi_count = txt1.count('\\pi')
   txt1 = re.sub(r'(\\pi ‘)',' ',txt1)
   txt1 = re.sub(r'(\\p.? *)','',txt1)

   # Excess spaces are removed
   txt1 = re.sub(r'(  +)',' ',txt1)
   txt1 = txt1.strip()

   #  Missing opening or closing quotation marks are added

   #  Temporarily substitute possessive inverted commas
   #  Possessives such as James’, widows’ need individual attention 
   txt1 = txt1.replace('’s','#s')
   for poss in ('Jesus’', 'James’', 'Barnabas’', 'postles’', 'arisees’', 'masters’', 'widows’', 'wives’', 'disciples’', 'saints’', 'horses’', 'Publius’', 'demons’'):
      txt1 = txt1.replace(poss,poss[:-1]+'#')
 
   # Find the relative positions of quotation marks
   # and add an extra one at the beginning or end as required
   first_o = txt1.find('‘')
       # If no '‘' is found, -1 is returned. Change this to be greater than
       # the likely length of the text to simply what follows.
   if first_o == -1: first_o = 9999 
   first_c = txt1.find('’')
   last_o = txt1.rfind('‘')
   last_c = txt1.rfind('’')
 
   if first_c >= 0 and first_o > first_c: txt1 = '‘' + txt1
   if last_o >= 0 and last_c < last_o: txt1 += '’'

   # With no quotation marks in sight, a section of continuous speech
   # may be recognised by the presence of \pi tags.
   # In which case, add opening and closing quotaion marks.
   if last_o == -1 and last_c == -1 and pi_count > 0:
      txt1 = '‘' + txt1 + '’'

   #  Reverse the substitutions
   txt1 = txt1.replace('#','’')

   return txt1

# ---------------
# End of Function
# ---------------

# -----------
# MAIN SCRIPT
# -----------

# Get the number of rows
cur.execute('''SELECT COUNT(*) FROM yocal_lections''')
end = cur.fetchone()[0]

# Get the lection references row by row and update the text columns
#######
#entry = 767         # To test an individual entry or range of entries
#while entry <= 767: # uncomment these lines and comment out the following two.
#######
entry = 1
while entry <= end:

   OT_rdg = 0

   cur.execute('''SELECT code, lect_1, lect_2 FROM yocal_lections WHERE rowid = ?''', (entry,))
   row = cur.fetchone()
   print(entry, row)
#for row in cur:
   code = row[0]   
   lect_1 = row[1]
   lect_2 = row[2]

# For each lection which exists get the text using the lect_txt function
   if lect_1 == "" or lect_1 is None:
      text_1 = ""
   else: 
      text_1 = lect_txt(lect_1)
      text_1 = text_1.replace('[','')
      text_1 = text_1.replace(']','')
   if lect_2 == "" or lect_2 is None:
      text_2 = ""
   else: 
      text_2 = lect_txt(lect_2)
      text_2 = text_2.replace('[','')
      text_2 = text_2.replace(']','')

# Add comment if readings are from the OT
   OT_txt = '<em><small>The text and chapter and verse references of the Old Testament readings are those of the Septuagint</em></small><br><br>'
   if OT_rdg == 1:
      if text_2 == "": text_1 += OT_txt
      else: text_2 += OT_txt

# Update the database with the text
   cur.execute('''UPDATE yocal_lections SET text_1 = ?, text_2 = ? WHERE code = ?''', (text_1, text_2, code))
   entry += 1

# Are the mods columns to be updated?
mods = input('\nDo you want to update the modification columns from mods.csv? ')
if mods == 'y' or mods == 'Y':
   # Open the csv file and read the text 
   f = open('mods.csv','r')
   for row in f:
      row = row.replace('%','\n')
      items = row.split('\t')
      if items[2] != '': items[2] = items[2].rstrip()
      cur.execute('''UPDATE yocal_lections SET mod_1 = ?, mod_2 = ? WHERE code = ?''', (items[1], items[2], items[0]))

   print('\nThe mod columns have been updated.\n') 

   # Close source file
   f.close()


cur.execute("COMMIT")

cal.close()

# Draw attention to the changes needed
print()
print("The Text fields have now been populated.\nIf the Mod fields are also populated, please run the script\n '11_master_lection_correct.py' for required changes")

x = input('   ... Press Enter to exit')

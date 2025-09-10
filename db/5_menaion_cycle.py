#!/usr/bin/python3
# York Orthodox Calendar Project v2
# Fr Deacon David Hoskin   2018

# --------------------------------------------------------------------------------
# Dependencies: python3, sqlite3, apsw python sqlite wrapper, the datetime module.
# --------------------------------------------------------------------------------

# This script populates the Year tables with the events of fixed date.
# For the most part this is straightforward copying exercice from the Menaion table
# of the major, Class 5 and British Isles and Ireland commemorations.
#
# Whether the Apostle reading, or both the Apostle and Gospel for a major commemoration
# (Class 4 and above) are preferred over the daily readings at the Liturgy will depend
# on whether or not they fall on a Sunday. The appropriate column (is_comm_apos, is_comm_gosp)
# is set only after checking whether or not it is a Sunday, the data being drawn from the
# is_sun_apos, is_sun_gosp, is_wkdy_apos and is_wkdy_gosp columns of the Menaion table.
#
# Certain of the 'fixed' commemorations are, on occasion, transferred. These are
# considered separately.
#
# The Forefeasts, Afterfeasts and Leavetakings of such major feasts that have them are
# recorded in the fore_after column.
#
# The Year Table columns major_commem, fore_after, class_5, british are populated.
#
# The fixed table 'Menaion' must already exist and be populated.
# The scripts 3_insert_ID_date and 4_paschalion_cycle must have been run and the relevant
# Year table columns populated.

# =======================================================================================

# Import the SQLite wrapper for Python:

import apsw

# Import the date handling modules:

import datetime
from datetime import date
from datetime import timedelta
import calendar

# Open the database as 'cal' and set the cursor to 'cur':

cal = apsw.Connection('YOCal.db')
cur = cal.cursor()

# Begin:

cur.execute('BEGIN TRANSACTION')

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

    # Get the Year table id of Pascha using the Gospel Code already set:

    cur.execute('''SELECT id FROM %s WHERE g_code = "J1Sun"''' % tn)
    pascha_id = cur.fetchone()[0]

    # Set reference date for calculations which use the table ids.
    # The last day of the previous year is treated as id = 0:

    base_date = date(yr-1,12,31)

    # Get the end of year id on the current Year table. It may be 365 or 366:

    end_yr_id = (date(yr,12,31) - base_date).days

    # Copy the Global (Class 5), British commemorations, Forefeasts, Afterfeasts
    # and Leavetakings to the Year table. This is done by matching the date_key
    # on the Menaion table to that on the Year table.

    row =1

    while row <= end_yr_id:

        # Get and date_key and day_name for the row ID

        cur.execute('''SELECT date_key, day_name FROM %s WHERE id = ?''' % tn, (row,))
        result = cur.fetchone()
        d_key = result[0]
        d_name = result[1]

        # Set the is_apos and is_gosp variables according to whether or not it is a Sunday:

        if d_name == "Sunday":
            is_apos = "is_sun_apos"
            is_gosp = "is_sun_gosp"
        else:
            is_apos = "is_wkdy_apos"
            is_gosp = "is_wkdy_gosp"
        cur.execute('''UPDATE %s SET
            class_5 = (SELECT class_5 FROM Menaion WHERE date_key = ?),
            british = (SELECT british FROM Menaion WHERE date_key = ?),
            fore_after = (SELECT fore_after FROM Menaion WHERE date_key = ?),
            is_comm_apos = (SELECT %s FROM Menaion WHERE date_key = ?),
            is_comm_gosp = (SELECT %s FROM Menaion WHERE date_key = ?)
            WHERE date_key = ?
            ''' % (tn, is_apos, is_gosp), (d_key, d_key, d_key, d_key, d_key, d_key))

        # If the Eve of the Nativity or Theophany falls on Saturday or Sunday
        # ignore the major data and continue to next row because
        # this date is celebrated as the Saturday or Sunday before the feast.

        if (d_key == '12-24' or d_key == '01-05') and (d_name == 'Saturday' or d_name == 'Sunday'):
           row += 1
           continue

# Copy the major commemorations and associated data to the Year table. We also take the commem lections for almost all the first 34 days of the year (from the Circumcision to the afterfeast of the Presentation) and use them as the apos and gosp entries. The weekdays, except the Saturdays before and after the Theophany, will have no lections set. For the exceptions see below.

        if d_key not in ("02-10","02-24","04-23","04-25","04-30","05-02","05-08"):
            cur.execute('''SELECT major FROM Menaion WHERE date_key = ?''', (d_key,))
            major = cur.fetchone()[0]
            if major != "": #or d_key.split("-")[0] == "01" or d_key == "02-03":
               cur.execute('''UPDATE %s SET
                major_commem = ?,
                apos_comm = (SELECT apostle FROM Menaion WHERE date_key = ?),
                gosp_comm = (SELECT gospel FROM Menaion WHERE date_key = ?),
                is_comm_apos = (SELECT %s FROM Menaion WHERE date_key = ?),
                is_comm_gosp = (SELECT %s FROM Menaion WHERE date_key = ?),
                c_code = ?
                WHERE date_key = ?
                ''' % (tn, is_apos, is_gosp), (major, d_key, d_key, d_key, d_key, d_key, d_key))

# Override is_apos and is_gosp on the Saturdays before and after the Theophany and the Saturday before the Elevation of the Cross
               cur.execute('''UPDATE %s SET 
                is_comm_apos = 0, is_comm_gosp = 0
                WHERE a_code = "SatBT"''' % tn)
               cur.execute('''UPDATE %s SET
                is_comm_apos = 0, is_comm_gosp = 0
                WHERE a_code = "SatAT"''' % tn)
               cur.execute('''UPDATE %s SET
                is_comm_apos = 0, is_comm_gosp = 0
                WHERE a_code = "SatBX"''' % tn)

        row += 1

# Jan 24 & 26 have no commem lections and provision is made on a year by year basis as follows:

# NB Readings are only needed for those years where the dates fall on a weekday. The four readings, apos and gosp, for Jan 24 & 26 are:

# 2023: Galatians 5:22-6:2 = E27Sat      / Matthew 22:35-46 = M15Sun
#       2 Corinthians 1:21-2:4 = E14Sun  / Matthew 25:14-30 = M16Sun
# 2024: Galatians 5:22-6:2 = E27Sat      / Matthew 14:22-34 = M9Sun
#       1 Corinthians 3:9-17 = E9Sun     / Matthew 22:2-14 = M14Sun
# 2025: Galatians 5:22-6:2 = E27Sat      / Luke 21:37-22:8 = L12Fri
#       (Jan 26 2025 is a Sunday)
# 2026: Galatians 5:22-6:2 = E27Sat      / Luke 17:3-10 = L15Sat
#       (Jan 26 2026 is within the Week of the Publican & Pharisee)
# 2027: (Jan 24 2027 is a Sunday)
#       James 3:1-10 = E32Tue            / Mark 11:11-23 = L15Tue
# 2028: Galatians 5:22-6:2 = E27Sat      / Mark 10:46-52 = L15Mon
#       James 3:11-4:6 = E32Wed          / Mark 11:22-26 = L15Wed
# 2029: Galatians 5:22-6:2 = E27Sat      / Mark 12:28-37 = L16Wed
#       2 Peter 1:1-10 = E33Fri          / Mark 13:1-8 = L16Fri
# 2030: Galatians 5:22-6:2 = E27Sat      / Mark 11:27-33 = L15Thu
#       1 Thessalonians 5:14-23 = E32Sat / Luke 17:3-10 = L15Sat
    
#    four_lects = {
#        2023: ["E27Sat","M15Sun","E14Sun","M16Sun"],
#        2024: ["E27Sat","M9Sun","E9Sun","M14Sun"],
#        2025: ["E27Sat","L12Fri","",""],
#        2026: ["E27Sat","L15Sat","",""],
#        2027: ["","","E32Tue","L15Tue"],
#        2028: ["E27Sat","L15Mon","E32Wed","L15Wed"],
#        2029: ["E27Sat","L16Wed","E33Fri","L16Fri"],
#        2030: ["E27Sat","L15Thu","E32Sat","L15Sat"]
#}  

#    if yr in four_lects:
#        apos24 = four_lects[yr][0]
#        gosp24 = four_lects[yr][1]
#        apos26 = four_lects[yr][2]
#        gosp26 = four_lects[yr][3]

#        if apos24 != "":
#            cur.execute('''UPDATE %s SET a_code = ? WHERE date_key = "01-24"
#                ''' % tn,(apos24,))
#        if gosp24 != "":
#            cur.execute('''UPDATE %s SET g_code = ? WHERE date_key = "01-24"
#                ''' % tn,(gosp24,))
#        if apos26 != "":
#            cur.execute('''UPDATE %s SET a_code = ? WHERE date_key = "01-26"
#                ''' % tn,(apos26,))
#        if gosp26 != "":
#            cur.execute('''UPDATE %s SET g_code = ? WHERE date_key = "01-26"
#                ''' % tn,(gosp26,))

# Now we fill the remaining blank apos and gosp entries for the first 34 days of the year

    row_id = 1
    while row_id < 35:
        cur.execute('''SELECT apos, gosp FROM %s WHERE id = ?
            ''' % tn,(row_id,))
        ag = cur.fetchone()
        if ag == None:
            cur.execute('''UPDATE %s SET
              apos = (SELECT apos_comm FROM %s WHERE id = ?),
              apos_comm = NULL''' % tn,(row_id,))
            cur.execute('''UPDATE %s SET
              gosp = (SELECT gosp_comm FROM %s WHERE id = ?),
              gosp_comm = NULL''' % tn,(row_id,))
        row_id += 1
         

    # Five major feasts may be transferred. They are:
    #    02-10    Haralampos moves to 02-09 if the 10th is the Saturday of All Souls.
    #    02-24    The Forerunner (1st & 2nd findings of the head)
    #                    moves to 02-23 if the 24th is the Saturday of All Souls.
    #    04-23    George moves to Bright Monday if it falls ealier.
    #    04-25    Mark moves to Bright Tuesday if it falls on Bright Monday,
    #                 else, if it falls between Palm Sunday and Bright Monday, it is reduced to Class 5.
    #    05-08    John moves to Bright Tuesday if it falls on Bright Monday (it can fall no earlier).

    # Two Class 4 feasts are reduced to Class 5 if they fall earlier than Bright Wednesday.
    # (Neither can fall before Palm Sunday):  
    #    04-30    James of Zebedee.
    #    05-02    Translation of the Relics of St Athanasius
   
    # Set the ids for these seven to their normal dates:

    hara_id = (date(yr,2,10) - base_date).days
    frunner_id = (date(yr,2,24) - base_date).days
    george_id = (date(yr,4,23) - base_date).days
    mark_id = (date(yr,4,25) - base_date).days
    james_id = (date(yr,4,30) - base_date).days
    athan_id = (date(yr,5,2) - base_date).days
    john_id = (date(yr,5,8) - base_date).days

    # Soul Sabbath falls 57 days before Pascha. Its Year table id is therefore:

    soul_sab_id = pascha_id - 57

    # If Haralampos or the Forerunner coincide with Soul Sabbath, move their id back one day and set the 'Transferred' text:

    if hara_id == soul_sab_id:
        hara_id -= 1
        hara_txt = " (Transferred from February 10th)"
    else: hara_txt = ""

    if frunner_id == soul_sab_id:
        frunner_id -= 1
        frunner_txt = " (Transferred from February 24th)"
    else: frunner_txt = ""

    # Similarly reset the other three if needed:

    if george_id < pascha_id +1:
        george_id = pascha_id +1
        george_txt = " (Transferred from April 23rd)"
    else: george_txt = ""

    if mark_id == pascha_id +1:
        mark_id = pascha_id +2
        mark_txt = " (Transferred from April 25th)"
    else: mark_txt = ""
    
    if john_id == pascha_id +1:
        john_id = pascha_id +2
        john_txt = " (Transferred from May 8th)"
    else: john_txt = ""



    # Assemble the data for all except those destined to be Class 5.

    data = [("02-10",hara_id,hara_txt),("02-24",frunner_id,frunner_txt),("04-23",george_id,george_txt),("05-08",john_id,john_txt)]

    if mark_id > pascha_id +1 or mark_id < pascha_id -7:
        data += [("04-25",mark_id,mark_txt)]

    if james_id > pascha_id +2:
        data += [("04-30",james_id,"")]

    if athan_id > pascha_id +1:
        data += [("05-02",athan_id,"")]

    # Cycle through, collecting the data for the feast from its original date_key position in
    # the Menaion table and placing it in its actual location for this year in the Year table.

    for d_key, yr_tbl_id, txt in data:

        # Get the Day Name for the Table ID

        cur.execute('''SELECT day_name FROM %s WHERE date_key = ?''' % tn, (d_key,))
        d_name = cur.fetchone()[0]

        # Set the is_apos and is_gosp variables according to whether or not it is a Sunday:

        if d_name == "Sunday":
            is_apos = "is_sun_apos"
            is_gosp = "is_sun_gosp"
        else:
            is_apos = "is_wkdy_apos"
            is_gosp = "is_wkdy_gosp"

        # if is_apos != 1: is_apos = 0
        # if is_gosp != 1: is_apos = 0

        # Get and set the major_commem column adding the 'transferred' text if it exists

        cur.execute('''SELECT major FROM Menaion WHERE date_key = ?''', (d_key,))
        major = cur.fetchone()[0]
        major = major + txt

        cur.execute('''UPDATE %s SET major_commem = ?, c_code = ? WHERE id = ?''' % tn, (major, d_key, yr_tbl_id))

        # Get and set the rest of the data

        cur.execute('''UPDATE %s SET
                apos_comm = (SELECT apostle FROM Menaion WHERE date_key = ?),
                gosp_comm = (SELECT gospel FROM Menaion WHERE date_key = ?),
                is_comm_apos = (SELECT %s FROM Menaion WHERE date_key = ?),
                is_comm_gosp = (SELECT %s FROM Menaion WHERE date_key = ?)
                WHERE id = ?
                ''' % (tn, is_apos, is_gosp), (d_key, d_key, d_key, d_key, yr_tbl_id))

    # If a feast has been transferred forwards, add a note on its original date.

    if george_txt:
       cur.execute('''UPDATE %s SET class_5 = ("[The commemoration of the Great Martyr George is transferred to Bright Monday] " || class_5) WHERE date_key = "04-23"''' % tn)

    if mark_txt:
       cur.execute('''UPDATE %s SET class_5 = ("[The commemoration of the Holy Apostle and Evangelist Mark is transferred to Bright Tuesday] " || class_5) WHERE date_key = "04-25"''' % tn)

    if john_txt:
       cur.execute('''UPDATE %s SET class_5 = ("[The commemoration of the Holy Apostle and Evangelist John is transferred to Bright Tuesday] " || class_5) WHERE date_key = "05-08"''' % tn)

    # Otherwise add the commem to the Class 5 list

    if mark_id < pascha_id +1 and mark_id > pascha_id -8:
        cur.execute('''UPDATE %s SET class_5 = ("Holy Apostle and Evangelist Mark (1st C). " || class_5) WHERE date_key = "04-25"''' % tn)

    if james_id < pascha_id +3:
        cur.execute('''UPDATE %s SET class_5 = ("Holy Apostle James the son of Zebedee, brother of Saint John the Theologian (44). " || class_5) WHERE date_key = "04-30"''' % tn)

    if athan_id < pascha_id +3:
         cur.execute('''UPDATE %s SET class_5 = ("Translation of the relics of Saint Athanasius the Great, Patriarch of Alexandria (373). " || class_5) WHERE date_key = "05-02"''' % tn)

    # If the Presentation falls on a Sunday before the triodion the Gospel for the feast is used
    pres_id = (date(yr,2,2) - base_date).days
    if pres_id < pascha_id - 70:
        cur.execute('''UPDATE %s SET is_comm_gosp = 1
                WHERE id = %s''' % (tn, pres_id))

    # If the Feast of St Athanasius falls on Pascha or Thomas Sunday his Apostle reading is suppressed
    athan_id = (date(yr,5,2) - base_date).days
    if athan_id == pascha_id or athan_id == pascha_id + 7:
        cur.execute('''UPDATE %s SET is_comm_apos = 0
                WHERE id = %s''' % (tn, athan_id))

     # If a feast falls on the Ascension both Apostle and Gospel readings are suppressed
    cur.execute('''UPDATE %s SET is_comm_apos = 0, is_comm_gosp = 0
                WHERE id = %s''' % (tn, pascha_id+39))
  
 # If a feast - e.g. Metrophanes - falls on Pentecost the festal Apostle reading is supressed
    cur.execute('''UPDATE %s SET is_comm_apos = 0
                WHERE id = %s''' % (tn, pascha_id+49))

    # Check that the Afterfeast and Leavetaking of the Meeting in the Temple (nominally Feb 9th) does not overrun the Sunday of the Prodigal Son which is 63 days before Pascha.

    prodigal_id = pascha_id - 63
    meeting_id = (date(yr,2,2) - base_date).days

    if prodigal_id < meeting_id + 8:

        # Set new_leave to the day before the Sun of the Prodigal:

        new_leave_id = prodigal_id - 1

        # Update the table with the new leavetaking provided there is at least one day between
        # the Meeting and the Sunday of the Prodigal.

        if new_leave_id > meeting_id:
            cur.execute('''UPDATE %s SET fore_after = "Leavetaking of the Meeting of the Lord in the Temple"
                    WHERE id = ?''' % tn, (new_leave_id,))

        # Delete any references to Afterfeast or Leaving which were initially placed
        # on or after the Sunday of the Prodigal

            x_id = prodigal_id
            while x_id < meeting_id + 8:
                cur.execute('''UPDATE %s SET fore_after = "" WHERE id = ?''' % tn, (x_id,))
                x_id += 1

    # We will also set the Afterfeasts and Leavetakings from the Pentecostarion.
    # They run from the eve of the Ascension (pascha + 38) to the eve of All Saints Sunday (pascha + 55)

    cur.execute('''UPDATE %s SET fore_after = "Leavetaking of Pascha" WHERE id = ?''' % tn, (pascha_id+38,))
    cur.execute('''UPDATE %s SET fore_after = "Afterfeast of the Ascension" WHERE id BETWEEN ? AND ?''' % tn, (pascha_id+40, pascha_id+46))
    cur.execute('''UPDATE %s SET fore_after = "Leavetaking of the Ascension" WHERE id = ?''' % tn, (pascha_id+47,))
    cur.execute('''UPDATE %s SET fore_after = "Afterfeast of Pentecost" WHERE id BETWEEN ? AND ?''' % tn, (pascha_id+50, pascha_id+54))
    cur.execute('''UPDATE %s SET fore_after = "Leavetaking of Pentecost" WHERE id = ?''' % tn, (pascha_id+55,))

    # In non Leap Years the commemorations for Feb 29th need to be appended to Feb 28th:

    if not calendar.isleap(yr):
          cur.execute('''UPDATE %s SET
            class_5 = (class_5 || " John Cassian the Roman, confessor (435) (t/f from Feb 29th).")
            WHERE date_key = "02-28" ''' % tn)
          cur.execute('''UPDATE %s SET
            british = (british || " Oswald of Worcester and York (t/f from Feb 29th).")
            WHERE date_key = "02-28" ''' % tn)

    # St. Raphael (Hawaweeny) is commemorated on the first Saturday of November.
    # We need to add his name to the class_5 list for the appropriate day.

    # What is the date key of the first Saturday of November?

    cur.execute('''SELECT date_key FROM %s
            WHERE month = "November" AND day_num < 8 AND Day_name = "Saturday"''' % tn)
    d_key = cur.fetchone()[0]

    # Add Hawaweeny and update the table

    cur.execute('''UPDATE %s SET
            class_5 = (class_5 || " Raphael (Hawaweeny) Bishop of Brooklyn (1915).")
            WHERE date_key = ?''' % tn, (d_key,))


    # St. Joseph the Betrothed, St. David the Psalmist & St. James the brother of the Lord are added to the class_5 list on the last Sunday of December, but if that is the 25th, the Nativity, they are added to Dec 26th.

    # What is the date key of the last Sunday of December?
    cur.execute('''SELECT date_key FROM %s
            WHERE month = "December" AND day_num > 24 AND Day_name = "Sunday"''' % tn)
    d_key = cur.fetchone()[0]

    # If the date key is for the Nativity, update it to the 26th.    
    if d_key == '12-25': d_key = '12-26'

    # Add the extra commemorations to beginning of the class_5 list for that day and update the table.
    cur.execute('''UPDATE %s SET
            class_5 = ("St. Joseph the Betrothed. St. David the Psalmist. St. James the brother of the Lord. " || class_5)
            WHERE date_key = ?''' % tn, (d_key,))


    # Stephen (12-27) does not have a Gospel if it falls on a Saturday

    cur.execute('''UPDATE %s SET
            is_comm_gosp = 0
            WHERE date_key = "12-27" AND day_name = "Saturday"''' % tn)

    # Finally where the only lections provided are by commem date, move that data from commen status to be the default for the day.

    row =1

    while row <= end_yr_id:

        # Get the data for the row ID

        cur.execute('''SELECT date_key, apos_comm, gosp_comm, a_code, c_code FROM %s WHERE id = ?''' % tn, (row,))
        result = cur.fetchone()
        d_key  = result[0]
        q_apos = result[1]
        q_gosp = result[2]
        q_code = result[3]
        q_comm = result[4]

        # If there is no q_code, set to work:

        blank = None
        nil = "0"
        if q_code == blank:
            print(d_key)
            cur.execute('''UPDATE %s SET apos = ? WHERE date_key = ?
            ''' % tn, (q_apos, d_key))
            cur.execute('''UPDATE %s SET gosp = ? WHERE date_key = ?
            ''' % tn, (q_gosp, d_key))
            cur.execute('''UPDATE %s SET a_code = ? WHERE date_key = ?
            ''' % tn, (q_comm, d_key))
            cur.execute('''UPDATE %s SET g_code = ? WHERE date_key = ?
            ''' % tn, (q_comm, d_key))
            cur.execute('''UPDATE %s SET is_comm_apos = ? WHERE date_key = ?
            ''' % tn, (nil, d_key))
            cur.execute('''UPDATE %s SET is_comm_gosp = ? WHERE date_key = ?
            ''' % tn, (nil, d_key))
            cur.execute('''UPDATE %s SET c_code = NULL WHERE date_key = ?
            ''' % tn, (d_key,))
            cur.execute('''UPDATE %s SET apos_comm = NULL WHERE date_key = ?
            ''' % tn, (d_key,))
            cur.execute('''UPDATE %s SET gosp_comm = NULL WHERE date_key = ?
            ''' % tn, (d_key,))

        row += 1
    # Move on to the next year:
    yr += 1
"""
    # January 3 is a special case. When it falls on ...
    # ... Sat or Sun, it is the Sat or Sun before the Theophany.
    # ... Friday is has its own readings.
    # ... Mon or Weds the unused SatBT readings are used.
    # ... Tues or Thurs the unused SunBT readings are used.
    # (i.e. when there is no Sat/SunBT because it was the Sat/SunAN or the Circumsion)

    cur.execute('''SELECT day_name FROM %s WHERE date_key = "01-03"''' % tn)
    result = cur.fetchone()
    day_name  = result[0]

    if day_name in ['Monday','Wednesday']:
        cur.execute('''UPDATE %s SET
        apos = "1 Timothy 3:13-4:5", gosp = "Matthew 3:1-6",
        a_code = "SatBT", g_code = "SatBT"
        WHERE date_key = "01-03"
        ''' % tn)

    if day_name in ['Tuesday','Thursday']:
        cur.execute('''UPDATE %s SET
         apos = "2 Timothy 4:5-8", gosp = "Mark 1:1-8",
        a_code = "SunBT", g_code = "SunBT"
        WHERE date_key = "01-03"
        ''' % tn)
"""      

# Write the data to the table

cur.execute('COMMIT')

cal.close()

print('Finished stage 5')

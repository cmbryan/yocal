from dataclasses import dataclass
import sqlite3
from typing import List
from jinja2 import Environment, FileSystemLoader
from datetime import date, datetime
import argparse
import os


@dataclass
class Antiphon:
    verses: List[str]
    chorus: str


def get_data(cursor, target_date):
    """Fetches the main data for a given date from the database."""
    query = "SELECT * FROM yocal_main WHERE date = ?"
    cursor.execute(query, (target_date.strftime("%Y-%m-%d"),))
    return dict(cursor.fetchone())


def get_antiphons(cursor, target_date):
    antiphons = []
    for antiphon_number in range(1, 4):
        cursor.execute("""
            SELECT FA.Is_Chorus, T.Content FROM Festal_Antiphons FA
            JOIN Texts T ON FA.Content_Ref = T.rowid
            WHERE Menaion_Ref = (SELECT rowid FROM Menaion WHERE date_key = ?)
                AND Number = ?
        """, (target_date.strftime("%m-%d"), antiphon_number))
        result = [dict(r) for r in cursor.fetchall()]
        if not result:
            break

        antiphons.append(
            Antiphon(
                verses=[r['Content'] for r in result if not r['Is_Chorus']],
                chorus=[r['Content'] for r in result if r['Is_Chorus']][0]
            )
        )

    return antiphons


def get_entrance_hymn(cursor, target_date):
    cursor.execute("""
        SELECT T.Content FROM Entrance_Hymns EH
        JOIN Texts T ON EH.Content_Ref = T.rowid
        WHERE Menaion_Ref = (SELECT rowid FROM Menaion WHERE date_key = ?)
    """, (target_date.strftime("%m-%d"),))
    result = cursor.fetchone()
    return result[0] if result else None


def get_apolytikia(cursor, data):
    apolytikia = ([], [])

    # Resurrectional troparia
    if data['day_name'] == 'Sunday':
        res = cursor.execute("""
            SELECT RT.Title, T.Content FROM Troparia RT
            JOIN Texts T ON RT.Content_Ref = T.rowid
            WHERE Title=?
        """, (f"Resurrectional Troparion, {data['tone'].lower()}",)).fetchone()
        # Only has a result if the tone is not 'Tone of the feast'
        if res:
            apolytikia[0].append(res)

    # Major feasts
    festal_key = data["major_commem"] or data["fore_after"]
    res = cursor.execute("""
        SELECT T.Content FROM Troparia RT
        JOIN Texts T ON RT.Content_Ref = T.rowid
        WHERE Title=?
    """, (festal_key,)).fetchone()
    if res:
        apolytikia[0].append((f"For the {festal_key}", res[0]))

    return apolytikia


def main():
    """Main function to get tone and render the template."""
    parser = argparse.ArgumentParser(description='Get the tone of the week for a given date.')
    parser.add_argument('--date', help='Date in YYYY-MM-DD format')
    args = parser.parse_args()

    target_date = datetime.strptime(args.date, '%Y-%m-%d').date() if args.date else date.today()

    main_db_path = '/home/chris/Documents/yocal/db/yocal/YOCal_Master.db'
    static_db_path = '/home/chris/Documents/yocal/db/yocal/YOCal.db'
    with sqlite3.connect(main_db_path) as main_conn, \
            sqlite3.connect(static_db_path) as static_conn:
        main_conn.row_factory = sqlite3.Row
        static_conn.row_factory = sqlite3.Row

        main_cur = main_conn.cursor()
        static_cur = static_conn.cursor()

        data = get_data(main_cur, target_date)

        # Derive additional Kliros elements from festal data
        data['antiphons'] = get_antiphons(static_cur, target_date)
        data['entrance_hymn'] = get_entrance_hymn(static_cur, target_date)
        data['apolytikia'] = get_apolytikia(static_cur, data)
    
    # Set up Jinja2 environment
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(script_dir))
    template = env.get_template("cc_template.html")
    
    # Render the template
    output = template.render(
        **data,
    )
    
    print(output)

if __name__ == "__main__":
    main()

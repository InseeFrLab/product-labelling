import sqlite3 as lite

con = lite.connect('db.sqlite3')

with con:
    cur = con.cursor()
    cur.execute("SELECT * FROM endpoints_labellisationfromlist")

    rows = cur.fetchall()

    for row in rows:
        print(row)

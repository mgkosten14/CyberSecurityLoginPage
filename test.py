import sqlite3

# Drops the table to start with.
# with sqlite3.connect("instance/var/db/database.db") as conn:
#     c = conn.cursor()
#     c.execute("DROP TABLE IF EXISTS account")
#     conn.commit()


# UNCOMMENT THE BELOW: This creates an admin user, with access to all pages
with sqlite3.connect("instance/var/db/database.db") as conn:
    c = conn.cursor()
    c.execute("UPDATE account SET accounting = 1, engineering = 1, reports = 1 WHERE uname = 'admin'")
    conn.commit()

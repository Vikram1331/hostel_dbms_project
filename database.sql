import sqlite3
import os

# Ensure the 'db' folder exists
if not os.path.exists('db'):
    os.makedirs('db')

# Connect to database
conn = sqlite3.connect('db/database.db')
cursor = conn.cursor()

# Drop tables if they already exist (for fresh start)
cursor.execute('DROP TABLE IF EXISTS student')
cursor.execute('DROP TABLE IF EXISTS admin')
cursor.execute('DROP TABLE IF EXISTS attendance')
cursor.execute('DROP TABLE IF EXISTS guest_invite')

# Create tables
cursor.execute('''
    CREATE TABLE student (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE guest_invite (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_email TEXT NOT NULL,
        guest_name TEXT NOT NULL,
        visit_date TEXT NOT NULL,
        invite_code TEXT UNIQUE NOT NULL
    )
''')

# Insert Dummy Students
cursor.execute('''
    INSERT INTO student (email, password) VALUES 
    ('student1@example.com', 'password1'),
    ('student2@example.com', 'password2')
''')

# Insert Dummy Admins
cursor.execute('''
    INSERT INTO admin (email, password) VALUES 
    ('admin1@example.com', 'adminpass1'),
    ('admin2@example.com', 'adminpass2')
''')

# Insert Dummy Attendance Records
cursor.execute('''
    INSERT INTO attendance (email, date, status) VALUES 
    ('student1@example.com', '2025-05-06', 'Present'),
    ('student2@example.com', '2025-05-06', 'Absent')
''')

# Insert Dummy Guest Invites
cursor.execute('''
    INSERT INTO guest_invite (student_email, guest_name, visit_date, invite_code) VALUES 
    ('student1@example.com', 'Guest A', '2025-05-10', 'abcd1234'),
    ('student2@example.com', 'Guest B', '2025-05-11', 'efgh5678')
''')

# Save (commit) changes
conn.commit()
conn.close()

print("✅ Database and tables created successfully with dummy data!")

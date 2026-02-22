import sqlite3

DB_FILE = 'wedding_planner.db'

def create_tables():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Guests
    c.execute('''
    CREATE TABLE IF NOT EXISTS guests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        rsvp TEXT,
        dietary TEXT,
        plus_ones INTEGER,
        kids INTEGER,
        hotel INTEGER,
        phone TEXT,
        table_number INTEGER,
        gift_amount REAL
    )
    ''')

    # Services
    c.execute('''
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service TEXT,
        name TEXT,
        price REAL,
        contact TEXT,
        other_info TEXT
    )
    ''')

    # Expenses
    c.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service TEXT,
        price REAL,
        paid REAL
    )
    ''')

    # Tasks
    c.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        completed INTEGER
    )
    ''')

    # Table configuration
    c.execute('''
    CREATE TABLE IF NOT EXISTS table_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        num_tables INTEGER,
        seats_per_table INTEGER
    )
    ''')

    conn.commit()
    conn.close()
    print("All tables created successfully!")

def add_sample_data():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Optional sample guests
    sample_guests = [
        ('Alice', 'Yes', 'Veg', 1, 0, 1, '0740000000', None, 100),
        ('Bob', 'No', '', 0, 1, 0, '0740000001', None, 50)
    ]
    c.executemany('''
    INSERT INTO guests (name, rsvp, dietary, plus_ones, kids, hotel, phone, table_number, gift_amount)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_guests)

    # Optional sample services
    sample_services = [
        ('Catering', 'Gourmet Ltd', 1200.0, 'catering@example.com', 'Includes drinks'),
        ('Photography', 'PhotoPro', 800.0, 'photo@example.com', 'Full day coverage')
    ]
    c.executemany('''
    INSERT INTO services (service, name, price, contact, other_info)
    VALUES (?, ?, ?, ?, ?)
    ''', sample_services)

    # Optional sample expenses
    sample_expenses = [
        ('Catering', 1200.0, 600.0),
        ('Photography', 800.0, 200.0)
    ]
    c.executemany('''
    INSERT INTO expenses (service, price, paid)
    VALUES (?, ?, ?)
    ''', sample_expenses)

    # Optional sample tasks
    sample_tasks = [
        ('Book venue', 1),
        ('Send invitations', 0)
    ]
    c.executemany('''
    INSERT INTO tasks (title, completed)
    VALUES (?, ?)
    ''', sample_tasks)

    # Optional table configuration
    c.execute('''
    INSERT INTO table_config (num_tables, seats_per_table)
    VALUES (?, ?)
    ''', (10, 8))

    conn.commit()
    conn.close()
    print("Sample data inserted successfully!")

if __name__ == "__main__":
    create_tables()
    add_sample_data()
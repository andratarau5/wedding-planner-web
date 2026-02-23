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
            table_assignment INTEGER,
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
    
    # Tables config (MATCHES app.py exactly)
    c.execute('''
        CREATE TABLE IF NOT EXISTS tables_config (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            num_tables INTEGER DEFAULT 0,
            seats_per_table INTEGER DEFAULT 0
        )
    ''')
    c.execute('INSERT OR IGNORE INTO tables_config (id, num_tables, seats_per_table) VALUES (1, 0, 0)')
    
    conn.commit()
    conn.close()
    print("✅ All tables created successfully!")

def add_sample_data():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Sample guests
    sample_guests = [
        ('Alice', 'Yes', 'Veg', 1, 0, 1, '0740000000', 0, 100.0),
        ('Bob', 'No', '', 0, 1, 0, '0740000001', 0, 50.0)
    ]
    c.executemany('''
        INSERT OR IGNORE INTO guests (name, rsvp, dietary, plus_ones, kids, hotel, phone, table_assignment, gift_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_guests)
    
    # Sample services
    sample_services = [
        ('Catering', 'Gourmet Ltd', 1200.0, 'catering@example.com', 'Includes drinks'),
        ('Photography', 'PhotoPro', 800.0, 'photo@example.com', 'Full day coverage')
    ]
    c.executemany('''
        INSERT OR IGNORE INTO services (service, name, price, contact, other_info)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_services)
    
    # Sample expenses
    sample_expenses = [
        ('Catering', 1200.0, 600.0),
        ('Photography', 800.0, 200.0)
    ]
    c.executemany('''
        INSERT OR IGNORE INTO expenses (service, price, paid)
        VALUES (?, ?, ?)
    ''', sample_expenses)
    
    # Sample tasks
    sample_tasks = [
        ('Book venue', 1),
        ('Send invitations', 0)
    ]
    c.executemany('''
        INSERT OR IGNORE INTO tasks (title, completed)
        VALUES (?, ?)
    ''', sample_tasks)
    
    conn.commit()
    conn.close()
    print("✅ Sample data inserted!")

if __name__ == "__main__":
    create_tables()
    add_sample_data()

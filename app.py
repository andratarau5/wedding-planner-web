from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from weasyprint import HTML
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database
DB_PATH = 'wedding_planner.db'

# Wedding date
WEDDING_DATE = datetime(2026, 7, 11)

# -------------------------------
# Database helper functions
# -------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Guests table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS guests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        rsvp TEXT DEFAULT 'No Response',
        dietary TEXT DEFAULT '',
        plus_ones INTEGER DEFAULT 0,
        kids INTEGER DEFAULT 0,
        hotel BOOLEAN DEFAULT 0,
        phone TEXT DEFAULT '',
        gift_amount REAL DEFAULT 0,
        table_assignment INTEGER
    )
    ''')

    # Services table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service TEXT,
        name TEXT,
        price REAL,
        contact TEXT,
        other_info TEXT
    )
    ''')

    # Expenses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service TEXT,
        price REAL,
        paid REAL
    )
    ''')

    # Tasks table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        completed BOOLEAN DEFAULT 0
    )
    ''')

    # Tables configuration
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tables_config (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        num_tables INTEGER DEFAULT 0,
        seats_per_table INTEGER DEFAULT 0
    )
    ''')

    # Ensure there's a single row for tables config
    cursor.execute('INSERT OR IGNORE INTO tables_config (id, num_tables, seats_per_table) VALUES (1,0,0)')

    conn.commit()
    conn.close()

# Initialize DB on startup
if not os.path.exists(DB_PATH):
    init_db()

# -------------------------------
# Home
# -------------------------------
@app.route('/')
def home():
    today = datetime.now()
    days_left = (WEDDING_DATE - today).days
    return render_template('home.html', wedding_date=WEDDING_DATE, days_left=days_left)

# -------------------------------
# Guests
# -------------------------------
@app.route('/guests')
def index():
    conn = get_db_connection()
    guests = conn.execute('SELECT * FROM guests').fetchall()
    conn.close()

    attending_count = sum(1 + g['plus_ones'] for g in guests if g['rsvp'].lower() == 'yes')
    declined_count = sum(1 for g in guests if g['rsvp'].lower() == 'no')
    total_kids = sum(g['kids'] for g in guests)
    total_adults = len(guests) + sum(g['plus_ones'] for g in guests)
    grand_total = total_adults + total_kids

    return render_template('index.html',
                           guests=guests,
                           attending_count=attending_count,
                           declined_count=declined_count,
                           total_kids=total_kids,
                           total_adults=total_adults,
                           grand_total=grand_total)

@app.route('/add', methods=['GET', 'POST'])
def add_guest():
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO guests (name, rsvp, dietary, plus_ones, kids, hotel, phone, gift_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['name'], 'No Response', '', 0, 0, 0, '', 0
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_guest.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_guest(id):
    conn = get_db_connection()
    guest = conn.execute('SELECT * FROM guests WHERE id = ?', (id,)).fetchone()
    if not guest:
        return "Guest not found", 404

    if request.method == 'POST':
        conn.execute('''
            UPDATE guests
            SET rsvp=?, dietary=?, plus_ones=?, kids=?, hotel=?, phone=?
            WHERE id=?
        ''', (
            request.form['rsvp'],
            request.form['dietary'],
            int(request.form.get('plus_ones', 0)),
            int(request.form.get('kids', 0)),
            1 if request.form.get('hotel') == 'yes' else 0,
            request.form.get('phone', ''),
            id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit_guest.html', guest=guest, id=id)

@app.route('/delete/<int:id>')
def delete_guest(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM guests WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/search')
def search_guest():
    query = request.args.get('q', '').strip().lower()
    conn = get_db_connection()
    filtered = []
    if query:
        filtered = conn.execute("SELECT * FROM guests WHERE LOWER(name) LIKE ?", (f'%{query}%',)).fetchall()
    conn.close()
    return render_template('search_results.html', guests=filtered, query=query)

# -------------------------------
# Services
# -------------------------------
@app.route('/services')
def services():
    conn = get_db_connection()
    services = conn.execute('SELECT * FROM services').fetchall()
    conn.close()
    return render_template('service.html', services=services)

@app.route('/services/add', methods=['GET', 'POST'])
def add_service():
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO services (service, name, price, contact, other_info)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            request.form['service'],
            request.form['name'],
            float(request.form['price']),
            request.form['contact'],
            request.form.get('other_info', '')
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('services'))
    return render_template('add_service.html')

@app.route('/services/edit/<int:id>', methods=['GET', 'POST'])
def edit_service(id):
    conn = get_db_connection()
    service = conn.execute('SELECT * FROM services WHERE id=?', (id,)).fetchone()
    if request.method == 'POST':
        conn.execute('''
            UPDATE services
            SET service=?, name=?, price=?, contact=?, other_info=?
            WHERE id=?
        ''', (
            request.form['service'],
            request.form['name'],
            float(request.form['price']),
            request.form['contact'],
            request.form.get('other_info', ''),
            id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('services'))
    conn.close()
    return render_template('edit_service.html', service=service)

@app.route('/services/delete/<int:id>')
def delete_service(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM services WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('services'))

# -------------------------------
# Expenses
# -------------------------------
@app.route('/expenses')
def expenses():
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses').fetchall()
    conn.close()
    return render_template('expenses.html', expenses=expenses)

@app.route('/expenses/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO expenses (service, price, paid)
            VALUES (?, ?, ?)
        ''', (
            request.form['service'],
            float(request.form['price']),
            float(request.form['paid'])
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('expenses'))
    return render_template('add_expense.html')

@app.route('/expenses/edit/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    conn = get_db_connection()
    expense = conn.execute('SELECT * FROM expenses WHERE id=?', (id,)).fetchone()
    if request.method == 'POST':
        conn.execute('''
            UPDATE expenses
            SET service=?, price=?, paid=?
            WHERE id=?
        ''', (
            request.form['service'],
            float(request.form['price']),
            float(request.form['paid']),
            id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('expenses'))
    conn.close()
    return render_template('edit_expense.html', expense=expense)

@app.route('/expenses/delete/<int:id>')
def delete_expense(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('expenses'))

# -------------------------------
# Budget
# -------------------------------
@app.route('/budget')
def budget_overview():
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses').fetchall()
    guests = conn.execute('SELECT * FROM guests').fetchall()
    conn.close()

    total_cost = sum(e['price'] for e in expenses)
    total_paid = sum(e['paid'] for e in expenses)
    expenses = [
        {**dict(e), 'remaining': e['price'] - e['paid']}
        for e in expenses
    ]


    total_gifts = sum(g['gift_amount'] for g in guests)
    final_budget = total_gifts - total_cost

    return render_template('budget.html',
                           expenses=expenses,
                           total_cost=total_cost,
                           total_paid=total_paid,
                           total_gifts=total_gifts,
                           final_budget=final_budget)

# -------------------------------
# Tasks
# -------------------------------
@app.route('/tasks', methods=['GET', 'POST'])
def tasks_view():
    conn = get_db_connection()
    if request.method == 'POST':
        conn.execute('INSERT INTO tasks (title, completed) VALUES (?,0)', (request.form['title'],))
        conn.commit()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()

    total = len(tasks)
    completed = sum(1 for t in tasks if t['completed'])
    percent = int((completed / total) * 100) if total else 0
    return render_template('tasks.html', tasks=tasks, total=total, completed=completed, percent=percent)

@app.route('/tasks/toggle/<int:id>', methods=['POST'])
def toggle_task(id):
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id=?', (id,)).fetchone()
    if task:
        conn.execute('UPDATE tasks SET completed=? WHERE id=?', (0 if task['completed'] else 1, id))
        conn.commit()
    conn.close()
    return redirect(url_for('tasks_view'))

@app.route('/tasks/delete/<int:id>', methods=['POST'])
def delete_task(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('tasks_view'))

# -------------------------------
# Table configuration & assignments
# -------------------------------
@app.route('/configure_tables', methods=['GET', 'POST'])
def configure_tables():
    conn = get_db_connection()
    config = conn.execute('SELECT * FROM tables_config WHERE id=1').fetchone()
    if request.method == 'POST':
        conn.execute('UPDATE tables_config SET num_tables=?, seats_per_table=? WHERE id=1', (
            int(request.form['num_tables']),
            int(request.form['seats_per_table'])
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('tables_view'))
    conn.close()
    return render_template('tables_config.html', config=config)

@app.route('/tables_view')
def tables_view():
    conn = get_db_connection()
    config = conn.execute('SELECT * FROM tables_config WHERE id=1').fetchone()
    guests = conn.execute('SELECT * FROM guests').fetchall()
    conn.close()

    num_tables = config['num_tables']
    tables = {i: [] for i in range(1, num_tables + 1)}
    for g in guests:
        t = g['table_assignment']
        if t and t in tables:
            tables[t].append(g['name'])
    return render_template('tables_view.html', tables=tables)

@app.route('/assign_tables', methods=['GET', 'POST'])
def assign_tables():
    conn = get_db_connection()
    guests = conn.execute('SELECT * FROM guests').fetchall()
    config = conn.execute('SELECT * FROM tables_config WHERE id=1').fetchone()
    conn.close()
    num_tables = config['num_tables']

    if request.method == 'POST':
        conn = get_db_connection()
        for g in guests:
            table_num_str = request.form.get(f'table_{g["id"]}', '')
            table_num = int(table_num_str) if table_num_str.isdigit() else None
            conn.execute('UPDATE guests SET table_assignment=? WHERE id=?', (table_num, g['id']))
        conn.commit()
        conn.close()
        return redirect(url_for('tables_view'))

    return render_template('assign_tables.html', guests=guests, num_tables=num_tables)

@app.route('/export_tables_pdf')
def export_tables_pdf():
    conn = get_db_connection()
    guests = conn.execute('SELECT * FROM guests').fetchall()
    config = conn.execute('SELECT * FROM tables_config WHERE id=1').fetchone()
    conn.close()

    num_tables = config['num_tables']
    seats_per_table = config['seats_per_table']
    tables = [[] for _ in range(num_tables)]
    guest_index = 0

    for g in guests:
        table_number = guest_index // seats_per_table
        if table_number < num_tables:
            tables[table_number].append(g['name'])
            guest_index += 1
        else:
            break

    rendered = render_template('tables_view_pdf.html', tables=tables, config=config)
    pdf = HTML(string=rendered).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=tables.pdf'
    return response

# -------------------------------
# Guest gift tracker
# -------------------------------
@app.route('/edit_gifts', methods=['GET', 'POST'])
def edit_gifts():
    conn = get_db_connection()
    guests = conn.execute('SELECT * FROM guests').fetchall()

    if request.method == 'POST':
        conn = get_db_connection()
        for g in guests:
            amount = request.form.get(f'gift_{g["id"]}')
            try:
                gift = float(amount) if amount else 0
            except ValueError:
                gift = 0
            conn.execute('UPDATE guests SET gift_amount=? WHERE id=?', (gift, g['id']))
        conn.commit()
        conn.close()
        return redirect(url_for('edit_gifts'))

    total_gifts = sum(g['gift_amount'] for g in guests)
    return render_template('edit_gifts.html', guests=guests, total_gifts=total_gifts)

# -------------------------------
# Run the app
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
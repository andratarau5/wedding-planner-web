from flask import Flask, render_template, request, redirect, url_for, flash
from weasyprint import HTML
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
GUEST_FILE = 'guest_list.json'
SERVICES_FILE = 'services.json'
EXPENSES_FILE = 'expenses.json'
TASKS_FILE = 'tasks.json'
TABLES_CONFIG_FILE = 'tables_config.json'
WEDDING_DATE = datetime(2026, 7, 11)

def load_guests():
    if os.path.exists(GUEST_FILE):
        with open(GUEST_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def load_services():
    if os.path.exists(SERVICES_FILE):
        with open(SERVICES_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def load_expenses():
    if os.path.exists(EXPENSES_FILE):
        with open(EXPENSES_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_guests(guests):
    with open(GUEST_FILE, 'w') as f:
        json.dump(guests, f, indent=4)

def save_services(services):
    with open(SERVICES_FILE, 'w') as f:
        json.dump(services, f, indent=4, default=str)

def save_expenses(expenses):
    with open(EXPENSES_FILE, 'w') as f:
        json.dump(expenses, f, indent=4)

@app.route('/')
def home():
    today = datetime.now()
    days_left = (WEDDING_DATE - today).days

    return render_template(
        'home.html',
        wedding_date=WEDDING_DATE,
        days_left=days_left
    )

@app.route('/guests')
def index():
    guests = load_guests()
    attending_count = sum(1 + guest.get('plus_ones', 0) for guest in guests if guest['rsvp'].lower() == 'yes')
    declined_count = sum(1 for guest in guests if guest['rsvp'].lower() == 'no')
    total_kids = sum(guest.get('kids', 0) for guest in guests)
    total_adults = len(guests) + sum(guest.get('plus_ones', 0) for guest in guests)
    grand_total = total_adults + total_kids
    return render_template('index.html', 
                           guests=guests, 
                           attending_count=attending_count, 
                           declined_count=declined_count,
                           total_kids=total_kids,
                           total_adults=total_adults,
                           grand_total=grand_total)

@app.route('/services')
def services():
    services = load_services()
    return render_template('service.html', services=services)

@app.route('/expenses')
def expenses():
    expenses = load_expenses()
    return render_template('expenses.html', expenses=expenses)

@app.route('/add', methods=['GET', 'POST'])
def add_guest():
    if request.method == 'POST':
        new_guest = {
            'name': request.form['name'],
            'rsvp': 'No Response',   # default state
            'dietary': '',           # default empty
            'plus_ones': 0
        }
        guests = load_guests()
        guests.append(new_guest)
        save_guests(guests)
        return redirect(url_for('index'))
    return render_template('add_guest.html')

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit_guest(index):
    guests = load_guests()
    if index < 0 or index >= len(guests):
        return "Guest not found", 404

    guest = guests[index]

    if request.method == 'POST':
        guest['rsvp'] = request.form['rsvp']
        guest['dietary'] = request.form['dietary']
        guest['plus_ones'] = int(request.form['plus_ones'])
        guest['hotel'] = request.form.get('hotel') == 'yes'
        guest['kids'] = int(request.form.get('kids', 0))
        guest['phone'] = request.form.get('phone', '')
        save_guests(guests)
        return redirect(url_for('index'))

    return render_template('edit_guest.html', guest=guest, index=index)


@app.route('/delete/<int:index>')
def delete_guest(index):
    guests = load_guests()
    if 0 <= index < len(guests):
        guests.pop(index)
        save_guests(guests)
    return redirect(url_for('index'))

@app.route('/services/add', methods=['GET', 'POST'])
def add_service():
    if request.method == 'POST':
        new_service = {
            'service': request.form['service'],
            'name': request.form['name'],
            'price': float(request.form['price']),
            'contact': request.form['contact'],
            'other_info': request.form.get('other_info', '')
        }
        services = load_services()
        services.append(new_service)
        save_services(services)
        return redirect(url_for('services'))
    return render_template('add_service.html')

@app.route('/services/edit/<int:index>', methods=['GET', 'POST'])
def edit_service(index):
    services = load_services()
    if request.method == 'POST':
        services[index] = {
            'service': request.form['service'],
            'name': request.form['name'],
            'price': float(request.form['price']),
            'contact': request.form['contact'],
            'other_info': request.form.get('other_info', '')
        }
        save_services(services)
        return redirect(url_for('services'))
    return render_template('edit_service.html', service=services[index])

@app.route('/services/delete/<int:index>')
def delete_service(index):
    services = load_services()
    services.pop(index)
    save_services(services)
    return redirect(url_for('services'))

@app.route('/expenses/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        new_expense = {
            'name': request.form['name'],
            'price': float(request.form['price']),
            'description': request.form['description']
        }
        expenses = load_expenses()
        expenses.append(new_expense)
        save_expenses(expenses)
        return redirect(url_for('expenses'))
    return render_template('add_expense.html')

@app.route('/expenses/edit/<int:index>', methods=['GET', 'POST'])
def edit_expense(index):
    expenses = load_expenses()
    if request.method == 'POST':
        expenses[index] = {
            'name': request.form['name'],
            'price': float(request.form['price']),
            'description': request.form['description']
        }
        save_expenses(expenses)
        return redirect(url_for('expenses'))
    return render_template('edit_expense.html', expense=expenses[index])

@app.route('/expenses/delete/<int:index>')
def delete_expense(index):
    expenses = load_expenses()
    if 0 <= index < len(expenses):
        expenses.pop(index)
        save_expenses(expenses)
    return redirect(url_for('expenses'))

@app.route('/search')
def search_guest():
    query = request.args.get('q', '').strip().lower()
    guests = load_guests()

    if query:
        filtered_guests = [
            guest for guest in guests
            if query in guest['name'].lower()
        ]
    else:
        filtered_guests = []

    return render_template('search_results.html', guests=filtered_guests, query=query)

@app.route('/budget')
def budget_overview():
    services = load_services()
    expenses = load_expenses()

    service_total = sum(float(s.get('total_price', 0)) for s in services if s.get('total_price'))
    other_total = sum(float(e.get('price', 0)) for e in expenses)

    grand_total = service_total + other_total

    return render_template('budget.html',
                           services=services,
                           expenses=expenses,
                           service_total=service_total,
                           other_total=other_total,
                           grand_total=grand_total)

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f)

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    tasks = load_tasks()
    if request.method == 'POST':
        new_task = request.form['title']
        tasks.append({'title': new_task, 'completed': False})
        save_tasks(tasks)
        return redirect(url_for('tasks'))

    total = len(tasks)
    completed = sum(1 for t in tasks if t['completed'])
    percent = int((completed / total) * 100) if total > 0 else 0

    return render_template('tasks.html', tasks=tasks, total=total, completed=completed, percent=percent)


@app.route('/tasks/toggle/<int:index>', methods=['POST'])
def toggle_task(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        tasks[index]['completed'] = not tasks[index]['completed']
        save_tasks(tasks)
    return redirect(url_for('tasks'))

@app.route('/tasks/delete/<int:index>', methods=['POST'])
def delete_task(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        tasks.pop(index)
        save_tasks(tasks)
    return redirect(url_for('tasks'))

def load_table_config():
    if os.path.exists(TABLES_CONFIG_FILE):
        with open(TABLES_CONFIG_FILE) as f:
            return json.load(f)
    return {"num_tables": 0, "seats_per_table": 0}

def save_table_config(config):
    with open(TABLES_CONFIG_FILE, 'w') as f:
        json.dump(config, f)

@app.route('/configure_tables', methods=['GET', 'POST'])
def configure_tables():
    config = load_table_config()
    if request.method == 'POST':
        config['num_tables'] = int(request.form['num_tables'])
        config['seats_per_table'] = int(request.form['seats_per_table'])
        save_table_config(config)
        return redirect(url_for('tables_view'))
    return render_template('tables_config.html', config=config)

@app.route('/tables_view')
def tables_view():
    config = load_table_config()
    guests = load_guests()
    num_tables = config.get("num_tables", 0)

    # Prepare tables as dict {table_num: [guest_names]}
    tables = {i: [] for i in range(1, num_tables + 1)}

    for guest in guests:
        table_num = guest.get('table')
        if table_num and table_num in tables:
            tables[table_num].append(guest['name'])

    return render_template('tables_view.html', tables=tables)


@app.route('/assign_tables', methods=['GET', 'POST'])
def assign_tables():
    guests = load_guests()
    config = load_table_config()
    num_tables = config.get('num_tables', 0)

    if request.method == 'POST':
        # Loop through guests and update table assignment from form data
        for i, guest in enumerate(guests):
            table_num_str = request.form.get(f'table_{i}', '')
            if table_num_str.isdigit():
                guest['table'] = int(table_num_str)
            else:
                guest['table'] = None  # Or 0 or null for no assignment

        save_guests(guests)
        return redirect(url_for('tables_view'))

    return render_template('assign_tables.html', guests=guests, num_tables=num_tables)

@app.route('/export_tables_pdf')
def export_tables_pdf():
    config = load_table_config()
    guests = load_guests()

    num_tables = config.get("num_tables", 0)
    seats_per_table = config.get("seats_per_table", 0)
    tables = [[] for _ in range(num_tables)]
    guest_index = 0

    for guest in guests:
        table_number = guest_index // seats_per_table
        if table_number < num_tables:
            tables[table_number].append(guest['name'])
            guest_index += 1
        else:
            break

    rendered = render_template('tables_view_pdf.html', tables=tables, config=config)
    pdf = HTML(string=rendered).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=tables.pdf'
    return response

@app.route('/edit_gifts', methods=['GET', 'POST'])
def edit_gifts():
    guests = load_guests()
    if request.method == 'POST':
        for i, guest in enumerate(guests):
            amount = request.form.get(f'gift_{i}')
            try:
                guest['gift_amount'] = float(amount) if amount else 0
            except ValueError:
                guest['gift_amount'] = 0
        save_guests(guests)
        return redirect(url_for('edit_gifts'))
    
    total_gifts = sum(g.get('gift_amount', 0) for g in guests)
    return render_template('edit_gifts.html', guests=guests, total_gifts=total_gifts)

@app.route('/budget_resolution')
def budget_resolution():
    guests = load_guests()
    services = load_services()
    expenses = load_expenses()

    # Gifts received from guests
    total_gifts = sum(g.get('gift_amount', 0) for g in guests)

    # Service and other expenses
    service_total = sum(float(s.get('total_price', 0)) for s in services if s.get('total_price'))
    other_total = sum(float(e.get('price', 0)) for e in expenses)
    total_spent = service_total + other_total

    remaining_balance = total_gifts - total_spent

    return render_template(
        'budget_resolution.html',
        total_gifts=total_gifts,
        service_total=service_total,
        other_total=other_total,
        total_spent=total_spent,
        remaining_balance=remaining_balance
    )

if __name__ == '__main__':
    app.run(debug=True)
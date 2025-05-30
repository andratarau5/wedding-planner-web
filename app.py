from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
GUEST_FILE = 'guest_list.json'
VENUES_FILE = 'venues.json'
EXPENSES_FILE = 'expenses.json'
WEDDING_DATE = 'wedding_date.json'


def load_guests():
    if os.path.exists(GUEST_FILE):
        with open(GUEST_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def load_venues():
    try:
        with open(VENUES_FILE, 'r') as f:
            venues = json.load(f)
            for v in venues:
                v['date'] = datetime.strptime(v['date'], '%Y-%m-%d')
            return venues
    except FileNotFoundError:
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

def save_venues(venues):
    venues_to_save = [
        {**v, 'date': v['date'].strftime('%Y-%m-%d')} for v in venues
    ]
    with open(VENUES_FILE, 'w') as f:
        json.dump(venues_to_save, f, indent=2)

def save_expenses(expenses):
    with open(EXPENSES_FILE, 'w') as f:
        json.dump(expenses, f, indent=4)

@app.route('/') 
def home():
    wedding_date_dict = load_wedding_date()
    wedding_date_str = wedding_date_dict.get('wedding_date')
    wedding_date_obj = None
    if wedding_date_str:
        wedding_date_obj = datetime.strptime(wedding_date_str, '%Y-%m-%d')
    return render_template('home.html', wedding_date=wedding_date_obj)

@app.route('/guests')
def index():
    guests = load_guests()
    attending_count = sum(1 + guest.get('plus_ones', 0) for guest in guests if guest['rsvp'].lower() == 'yes')
    declined_count = sum(1 for guest in guests if guest['rsvp'].lower() == 'no')
    return render_template('index.html', guests=guests, attending_count=attending_count, declined_count=declined_count)

@app.route('/venues')
def venue():
    venues = load_venues()
    return render_template('venue.html', venues=venues)

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

@app.route('/venues/add', methods=['GET', 'POST'])
def add_venue():
    if request.method == 'POST':
        new_venue = {
            'name': request.form['name'],
            'address': request.form['address'],
            'date': datetime.strptime(request.form['date'], '%Y-%m-%d'),
            'capacity': int(request.form['capacity']),
            'menu_price': float(request.form['menu_price']),
            'contact': request.form['contact']
        }
        venues = load_venues()
        venues.append(new_venue)
        save_venues(venues)
        return redirect(url_for('venue'))
    return render_template('add_venue.html')

@app.route('/venues/edit/<int:index>', methods=['GET', 'POST'])
def edit_venue(index):
    venues = load_venues()
    if request.method == 'POST':
        venues[index] = {
            'name': request.form['name'],
            'address': request.form['address'],
            'date': datetime.strptime(request.form['date'], '%Y-%m-%d'),
            'capacity': int(request.form['capacity']),
            'menu_price': float(request.form['menu_price']),
            'contact': request.form['contact']
        }
        save_venues(venues)
        return redirect(url_for('venue'))
    return render_template('edit_venue.html', venue=venues[index])

@app.route('/venues/delete/<int:index>')
def delete_venue(index):
    venues = load_venues()
    venues.pop(index)
    save_venues(venues)
    return redirect(url_for('venue'))

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
    venues = load_venues()
    expenses = load_expenses()

    venue_total = sum(float(v.get('menu_price', 0)) for v in venues if v.get('menu_price'))
    other_total = sum(float(e.get('amount', 0)) for e in expenses)

    grand_total = venue_total + other_total

    return render_template('budget.html',
                           venues=venues,
                           expenses=expenses,
                           venue_total=venue_total,
                           other_total=other_total,
                           grand_total=grand_total)


def load_wedding_date():
    if os.path.exists(WEDDING_DATE):
        with open(WEDDING_DATE, 'r') as f:
            return json.load(f)
    return {}


def save_wedding_date(wedding_date):
    with open(WEDDING_DATE, 'w') as f:
        json.dump(wedding_date, f)


@app.route('/edit_date', methods=['GET', 'POST'])
def edit_date():
    wedding_date_dict = load_wedding_date()
    current_date = wedding_date_dict.get('wedding_date', '')  # string or empty

    if request.method == 'POST':
        new_date = request.form.get('wedding_date')  # expects "YYYY-MM-DD"
        if new_date:
            wedding_date_dict['wedding_date'] = new_date
            save_wedding_date(wedding_date_dict)
        return redirect(url_for('home'))  # redirect to home or wherever you want

    return render_template('edit_date.html', wedding_date=current_date)


if __name__ == '__main__':
    app.run(debug=True)
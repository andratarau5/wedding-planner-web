from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
GUEST_FILE = 'guest_list.json'

def load_guests():
    if os.path.exists(GUEST_FILE):
        with open(GUEST_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_guests(guests):
    with open(GUEST_FILE, 'w') as f:
        json.dump(guests, f, indent=4)

@app.route('/')
def index():
    guests = load_guests()
    attending_count = sum(1 + guest.get('plus_ones', 0) for guest in guests if guest['rsvp'].lower() == 'yes')
    declined_count = sum(1 for guest in guests if guest['rsvp'].lower() == 'no')
    return render_template('index.html', guests=guests, attending_count=attending_count, declined_count=declined_count)

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

if __name__ == '__main__':
    app.run(debug=True)
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
    return render_template('index.html', guests=guests)

@app.route('/add', methods=['GET', 'POST'])
def add_guest():
    if request.method == 'POST':
        new_guest = {
            'name': request.form['name'],
            'rsvp': request.form['rsvp'],
            'dietary': request.form['dietary']
        }
        guests = load_guests()
        guests.append(new_guest)
        save_guests(guests)
        return redirect(url_for('index'))
    return render_template('add_guest.html')

@app.route('/delete/<int:index>')
def delete_guest(index):
    guests = load_guests()
    if 0 <= index < len(guests):
        guests.pop(index)
        save_guests(guests)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
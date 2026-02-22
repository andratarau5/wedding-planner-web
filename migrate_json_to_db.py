import sqlite3
import json
import os

DB = "wedding.db"

conn = sqlite3.connect(DB)
cursor = conn.cursor()


# -------------------------
# Helper function
# -------------------------
def load_json(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        return json.load(f)


# -------------------------
# MIGRATE GUESTS
# -------------------------
guests = load_json("guests.json")

for g in guests:
    cursor.execute("""
        INSERT INTO guests (name, group_name, table_number, gift_amount)
        VALUES (?, ?, ?, ?)
    """, (
        g.get("name"),
        g.get("group", ""),
        g.get("table", None),
        g.get("gift_amount", 0)
    ))


# -------------------------
# MIGRATE SERVICES
# -------------------------
services = load_json("services.json")

for s in services:
    cursor.execute("""
        INSERT INTO services (service_type, name, total_price, contact, other_info)
        VALUES (?, ?, ?, ?, ?)
    """, (
        s.get("service"),
        s.get("name"),
        s.get("total_price", 0),
        s.get("contact", ""),
        s.get("other_info", "")
    ))


# -------------------------
# MIGRATE EXPENSES
# -------------------------
expenses = load_json("expenses.json")

for e in expenses:
    cursor.execute("""
        INSERT INTO expenses (service, price, paid)
        VALUES (?, ?, ?)
    """, (
        e.get("service"),
        e.get("price", 0),
        e.get("paid", 0)
    ))


# -------------------------
# MIGRATE TASKS
# -------------------------
tasks = load_json("tasks.json")

for t in tasks:
    cursor.execute("""
        INSERT INTO tasks (task_name, completed)
        VALUES (?, ?)
    """, (
        t.get("task"),
        1 if t.get("completed") else 0
    ))


conn.commit()
conn.close()

print("🎉 Migration completed successfully!")
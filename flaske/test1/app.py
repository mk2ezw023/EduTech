from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
app.config['DEBUG'] = True

def create_table():
    conn = sqlite3.connect('study.db')
    conn.execute('CREATE TABLE IF NOT EXISTS study (id INTEGER PRIMARY KEY, date TEXT, study_time INTEGER, grade INTEGER)')
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('study.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM study')
    results = cur.fetchall()
    conn.close()
    return render_template('index.html', results=results)

@app.route('/add', methods=['POST'])
def add():
    date = request.form['date']
    study_time = request.form['study_time']
    grade = request.form['grade']
    conn = sqlite3.connect('study.db')
    cur = conn.cursor()
    cur.execute('INSERT INTO study (date, study_time, grade) VALUES (?, ?, ?)', (date, study_time, grade))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    create_table()
    app.run()

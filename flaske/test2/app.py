from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route('/')
def home():
    conn = sqlite3.connect('study.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM study')
    results = cur.fetchall()
    conn.close()
    return render_template('home.html', results=results, advice=generate_advice())

def get_study_records():
    conn = sqlite3.connect('study.db')
    cur = conn.cursor()
    cur.execute('SELECT study_time, grade FROM study')
    results = cur.fetchall()
    conn.close()
    return results


    
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

def generate_advice():
    records = get_study_records()
    if len(records) == 0:
        return 'No study records found.'
    total_time = sum(record[0] for record in records)
    avg_time = total_time / len(records)
    avg_grade = sum(record[1] for record in records) / len(records)
    if avg_time < 60 and avg_grade < 60:
        return 'You need to study more and improve your grades.'
    elif avg_time < 60:
        return 'You need to study more.'
    elif avg_grade < 60:
        return 'You need to improve your grades.'
    elif avg_time > 120 and avg_grade > 80:
        return 'Great job! Keep up the good work.'
    else:
        return 'Good job. Keep working on maintaining your study habits.'

if __name__ == '__main__':
    app.run()


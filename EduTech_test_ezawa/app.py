from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from flask_sqlalchemy import SQLAlchemy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
from base64 import b64encode
import datetime



app = Flask(__name__)

# SQLite3データベースのパス
DATABASE = 'db/study.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edu_data.db'
db = SQLAlchemy(app)


class StudyData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    study_hours = db.Column(db.Integer)
    score = db.Column(db.Integer)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/results', methods=['POST'])
def results():
    study_hours = int(request.form['study_hours'])
    score = int(request.form['score'])

    data = StudyData(study_hours=study_hours, score=score)
    db.session.add(data)
    db.session.commit()

    all_data = StudyData.query.all()
    hours = []
    scores = []
    for data in all_data:
        hours.append(data.study_hours)
        scores.append(data.score)

    corr_coef = round(np.corrcoef(hours, scores)[0, 1], 2)
    # ビジュアライズ
    plt.scatter(hours, scores)
    plt.title(f"Correlation Coefficient: {corr_coef}")
    plt.xlabel("Study Hours")
    plt.ylabel("Score")
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')

    return render_template('results.html', plot_data=plot_data)


# 残り日数の変更
@app.route('/exam', methods=['POST'])
def exam():
    exam_date = request.form['exam_date']
    exam_date = datetime.datetime.strptime(exam_date, '%Y-%m-%d')
    today = datetime.datetime.today()
    remaining_days = (exam_date - today).days
    return render_template('countdown.html', remaining_days=remaining_days)


# データベース関連の関数
def connect_db():
    return sqlite3.connect(DATABASE)


def init_database():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('DROP TABLE IF EXISTS subjects')
        c.execute('CREATE TABLE subjects (id INTEGER PRIMARY KEY, name TEXT, hours INTEGER, grade INTEGER)')
        subjects = [('英語', 0, 0), ('数学', 0, 0), ('国語', 0, 0), ('理科', 0, 0), ('社会', 0, 0)]
        c.executemany('INSERT INTO subjects (name, hours, grade) VALUES (?, ?, ?)', subjects)
        conn.commit()



@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # フォームから送信されたデータを取得
        subjects = request.form.getlist('subject')
        hours = request.form.getlist('hours')

        conn = connect_db()
        c = conn.cursor()
        # データベースのデータを更新
        for i in range(len(subjects)):
            c.execute('UPDATE subjects SET hours = ? WHERE name = ?', (hours[i], subjects[i]))
        conn.commit()
        conn.close()

        return render_template('result.html', subjects=subjects, hours=hours)

    else:
        conn = connect_db()
        c = conn.cursor()
        c.execute('SELECT name, hours FROM subjects')
        data = c.fetchall()
        conn.close()

        return render_template('index.html', data=data)


if __name__ == '__main__':
    # データベースの初期化
    init_database()
    app.run(debug=True)


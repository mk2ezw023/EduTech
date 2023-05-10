from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
from base64 import b64encode
import sqlite3
import datetime

app = Flask(__name__)

app.jinja_env.filters['b64encode'] = b64encode
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edu_data.db'
db = SQLAlchemy(app)


class StudyData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    study_hours = db.Column(db.Integer)
    score = db.Column(db.Integer)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    hours = db.Column(db.Integer)


with app.app_context():
    db.create_all()

    # データベースの初期化
    subjects = [('英語', 0), ('数学', 0), ('国語', 0), ('理科', 0), ('社会', 0)]
    for subject_name, hours in subjects:
        subject = Subject(name=subject_name, hours=hours)
        db.session.add(subject)
    db.session.commit()


@app.route('/')
def index():
    data = Subject.query.all()
    return render_template('index.html', data=data)


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

    plt.scatter(hours, scores)
    plt.title(f"Correlation Coefficient: {corr_coef}")
    plt.xlabel("Study Hours")
    plt.ylabel("Score")
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')

    return render_template('results.html', plot_data=plot_data)


@app.route('/exam', methods=['POST'])
def exam():
    exam_date = request.form['exam_date']
    exam_date = datetime.datetime.strptime(exam_date, '%Y-%m-%d')
    today = datetime.datetime.today()
    remaining_days = (exam_date - today).days
    return render_template('countdown.html', remaining_days=remaining_days)


if __name__ == '__main__':
    app.run(debug=True)

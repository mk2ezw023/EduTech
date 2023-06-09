from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import numpy as np
from io import BytesIO
import base64
from base64 import b64encode
# ここからFlaskアプリを作るよ
app = Flask(__name__)

# Jinja2のフィルターとしてb64encodeを定義
app.jinja_env.filters['b64encode'] = b64encode
# データベースのURIを設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edu_data.db'
# SQLAlchemyオブジェクトを作成
db = SQLAlchemy(app)
# データベースのモデルを定義
class StudyData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    study_hours = db.Column(db.Integer)
    score = db.Column(db.Integer)
# データベースがなければ作成する
with app.app_context():
    db.create_all()
# ホームページを表示するためのルート
@app.route('/')
def index():
    return render_template('index.html')
# フォームから送信されたデータを処理し、結果ページを表示するためのルート
@app.route('/results', methods=['POST'])
def results():
    study_hours = int(request.form['study_hours'])# フォームから送信されたデータを取得
    score = int(request.form['score'])

    # 取得したデータをデータベースに保存
    data = StudyData(study_hours=study_hours, score=score)
    db.session.add(data)
    db.session.commit()
# データベース内の全てのデータを取得
    all_data = StudyData.query.all()
    hours = []
    scores = []
    for data in all_data:
        hours.append(data.study_hours)
        scores.append(data.score)

    # データの相関係数を計算し、結果を表示するための準備をする
    corr_coef = round(np.corrcoef(hours, scores)[0, 1], 2)
#ビジュアライズ
    plt.scatter(hours, scores)
    plt.title(f"Correlation Coefficient: {corr_coef}")
    plt.xlabel("Study Hours")
    plt.ylabel("Score")
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')

    return render_template('results.html', plot_data=plot_data)






#残り日数の変更
import datetime




# 残り日数を計算し、カウントダウンページを表示するためのルート
@app.route('/exam', methods=['POST'])
def exam():
    # フォームから送信された試験日を取得し、計算に必要な形式に変換する
    exam_date = request.form['exam_date']
    exam_date = datetime.datetime.strptime(exam_date, '%Y-%m-%d')
    today = datetime.datetime.today()
    remaining_days = (exam_date - today).days
    return render_template('countdown.html', remaining_days=remaining_days)



if __name__ == '__main__':
    app.run(debug=True)
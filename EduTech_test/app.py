# app.py
from flask import Flask, render_template, request
import sqlite3
import datetime
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# データベースファイルのパス
DATABASE = 'db/study.db'

# 初期データの登録
def init_database():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        # テーブルが存在しない場合は作成
        c.execute('CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY, name TEXT, hours INTEGER, score INTEGER)')
        # 既存のデータを削除
        c.execute('DELETE FROM subjects')
        # 初期データの挿入
        subjects = [('英語', 0, 0), ('数学', 0, 0), ('国語', 0, 0), ('理科', 0, 0), ('社会', 0, 0)]
        c.executemany('INSERT INTO subjects (name, hours, score) VALUES (?, ?, ?)', subjects)
        conn.commit()

# 初期データの登録
init_database()

# ホームページのルートパス
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # フォームから送信されたデータを取得
        subjects = request.form.getlist('subject')
        hours = request.form.getlist('hours')

        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            # データベースのデータを更新
            for i in range(len(subjects)):
                c.execute('UPDATE subjects SET hours = ? WHERE name = ?', (hours[i], subjects[i]))
            conn.commit()

        return render_template('result.html', subjects=subjects, hours=hours)

    else:
        # データベースから科目と時間のデータを取得
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute('SELECT name, hours, score FROM subjects')
            data = c.fetchall()

        return render_template('index.html', data=data)

# 残り日数を計算し、カウントダウンページを表示するためのルート
@app.route('/exam', methods=['POST'])
def exam():
    # フォームから送信された試験日を取得し、計算に必要な形式に変換する
    exam_date = request.form['exam_date']
    exam_date = datetime.datetime.strptime(exam_date, '%Y-%m-%d')
    today = datetime.datetime.today()
    remaining_days = (exam_date - today).days
    return render_template('index.html', remaining_days=remaining_days)

# グラフの表示を行うルート
@app.route('/graph')
def graph():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('SELECT name, hours, score FROM subjects')
        data = c.fetchall()
    
    subjects = [subject[0] for subject in data]
    hours = [subject[1] for subject in data]
    scores = [subject[2] for subject in data]

    # 円グラフの作成
    plt.figure(figsize=(6, 6))
    plt.pie(hours, labels=subjects, autopct='%1.1f%%')
    plt.title('Study Hours by Subject')

    # グラフをバイナリデータとして保存
    graph_image = io.BytesIO()
    plt.savefig(graph_image, format='png')
    graph_image.seek(0)
    graph_url = base64.b64encode(graph_image.getvalue()).decode()

    # 散布図の作成
    plt.figure(figsize=(6, 6))
    plt.scatter(scores, hours)
    plt.xlabel('Scores')
    plt.ylabel('Study Hours')
    plt.title('Correlation between Scores and Study Hours')

    # グラフをバイナリデータとして保存
    scatter_image = io.BytesIO()
    plt.savefig(scatter_image, format='png')
    scatter_image.seek(0)
    scatter_url = base64.b64encode(scatter_image.getvalue()).decode()

    return render_template('graph.html', graph_url=graph_url, scatter_url=scatter_url)


if __name__ == '__main__':
    app.run(port=5010)  # 代わりのポート番号を指定

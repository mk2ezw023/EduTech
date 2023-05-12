# app.py
from flask import Flask, render_template, request
import sqlite3
import datetime
import random
import matplotlib.pyplot as plt
import spacy
from scipy.stats import pearsonr
nlp = spacy.load('en_core_web_sm')


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
# 学習時間とテストの点数の相関を計算する関数
def calculate_correlation(hours, scores):
    # 相関を計算
    correlation = np.corrcoef(hours, scores)[0, 1]
    return correlation


# ホームページのルートパス
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # フォームから送信されたデータを取得
        subjects = request.form.getlist('subject')
        hours = request.form.getlist('hours')
        scores = request.form.getlist('score')

        # 学習時間とテストの点数を整数に変換
        hours = list(map(int, hours))
        scores = list(map(int, scores))

        # 学習時間とテストの点数の相関を計算
        correlation, _ = pearsonr(hours, scores)

        # 相関をグラフ化
        plt.figure()
        plt.scatter(hours, scores)
        plt.xlabel('Study Hours')
        plt.ylabel('Test Scores')
        plt.title('Correlation between Study Hours and Test Scores')
        plt.grid(True)
        plt.savefig('static/correlation.png')

        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            # データベースのデータを更新
            for i in range(len(subjects)):
                c.execute('UPDATE subjects SET hours = ?, score = ? WHERE name = ?', (hours[i], scores[i], subjects[i]))
            conn.commit()

        return render_template('results.html', subjects=subjects, hours=hours)

    else:
        # データベースから科目と時間のデータを取得
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute('SELECT name, hours FROM subjects')
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


# ホームページを表示するためのルート
@app.route('/')
def home():
    return render_template('index.html')

# しりとりゲームのルート
@app.route('/word_chain', methods=['GET', 'POST'])
def word_chain():
    if request.method == 'POST':
        user_word = request.form['user_word'].lower()
        user_last_letter = user_word[-1]
        computer_word = get_random_word(user_last_letter)

        if computer_word:
            doc = nlp(computer_word)
            pos = doc[0].pos_
            return render_template('index.html', user_word=user_word, computer_word=computer_word, pos=pos)
        else:
            return render_template('index.html', user_word=user_word, computer_word=None, pos=None)
    else:
        return render_template('index.html', user_word=None, computer_word=None, pos=None)

def get_random_word(last_letter):
    word_list = [
        "apple", "banana", "cat", "dog", "elephant", "ant", "ball", "car", "dog", "elephant",
        "fish", "guitar", "hat", "ice cream", "jacket", "kangaroo", "lion", "mouse", "noodle",
        "orange", "penguin", "queen", "rabbit", "snake", "tiger", "umbrella", "violin", "watermelon",
        "xylophone", "yoga", "zebra", "apple", "banana", "cat", "dog", "elephant", "ant", "ball",
        "car", "dog", "elephant", "fish", "guitar", "hat", "ice cream", "jacket", "kangaroo", "lion",
        "mouse", "noodle", "orange", "penguin", "queen", "rabbit", "snake", "tiger", "umbrella",
        "violin", "watermelon", "xylophone", "yoga", "zebra", "apple", "banana", "cat", "dog",
        "elephant", "ant", "ball", "car", "dog", "elephant", "fish", "guitar", "hat", "ice cream",
        "jacket", "kangaroo", "lion", "mouse", "noodle", "orange", "penguin", "queen", "rabbit",
        "snake", "tiger", "umbrella", "violin", "watermelon", "xylophone", "yoga", "zebra"
    ]
    filtered_words = [word for word in word_list if word.startswith(last_letter)]
    if filtered_words:
        return random.choice(filtered_words)
    else:
        return None



if __name__ == '__main__':
    app.run(port=5010)  # 代わりのポート番号を指定


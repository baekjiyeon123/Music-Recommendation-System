from flask import Flask, jsonify, render_template, request
from sqlalchemy import create_engine, text
import pandas as pd

app = Flask(__name__)

# MySQL 연결
engine = create_engine('mysql+pymysql://root:qorwl20910!@localhost:3306/location_music')

# CSV 파일 경로
file_path = 'C:/Users/82108/.kaggle/music_data/top50.csv'

# CSV 파일 읽기
music_data = pd.read_csv(file_path, encoding='ISO-8859-1')

# 불필요한 컬럼 삭제
music_data = music_data.drop(columns=['Unnamed: 0'], errors='ignore')

# 컬럼 이름 변경
music_data.columns = ['Track_Name', 'Artist_Name', 'Genre', 'Beats_Per_Minute',
                       'Energy', 'Danceability', 'Loudness_dB', 'Liveness',
                       'Valence', 'Length', 'Acousticness', 'Speechiness', 'Popularity']

# 'mood'와 'time_of_day' 생성
def get_mood(valence):
    return 'Positive' if valence >= 70 else 'Negative'

def get_time_of_day(energy, danceability):
    if energy > 50 and danceability > 50:
        return 'Night'
    return 'Day'


# 새로운 컬럼 생성
music_data['mood'] = music_data['Valence'].apply(get_mood)
music_data['time_of_day'] = music_data.apply(lambda row: get_time_of_day(row['Energy'], row['Danceability']), axis=1)

# 필요한 컬럼만 추출
modified_data = music_data[['Track_Name', 'Artist_Name', 'Genre', 'mood', 'time_of_day']]

# 컬럼 이름 변경
modified_data.columns = ['title', 'artist', 'genre', 'mood', 'time_of_day']

# MySQL에 데이터 저장
try:
    modified_data.to_sql('songs', con=engine, if_exists='replace', index=False)
    print("Data inserted into MySQL!")
except Exception as e:
    print(f"Error: {e}")

@app.route('/', methods=['GET'])
def get_songs():
    # 쿼리 파라미터에서 mood, time_of_day, genre를 받아옵니다.
    mood = request.args.get('mood', default=None, type=str)
    time_of_day = request.args.get('time_of_day', default=None, type=str)
    genre = request.args.get('genre', default=None, type=str)

    # 기본 쿼리 작성
    query = "SELECT * FROM songs WHERE 1=1"
    params = {}

    if mood:
        query += " AND mood = :mood"
        params['mood'] = mood
    if time_of_day:
        query += " AND time_of_day = :time_of_day"
        params['time_of_day'] = time_of_day
    if genre:
        query += " AND genre = :genre"
        params['genre'] = genre

    # SQL 쿼리 실행
    with engine.connect() as connection:
        result = connection.execute(text(query), params)
        # 수정된 부분: Row 객체에서 key를 사용하여 dict 형태로 변환
        songs = [dict(zip(result.keys(), row)) for row in result.fetchall()]

    # HTML 템플릿으로 결과 전달
    return render_template('musicmusic.html', songs=songs)

if __name__ == '__main__':
    app.run(debug=True)

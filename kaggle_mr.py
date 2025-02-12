import pandas as pd
from sqlalchemy import create_engine

# 다운로드된 CSV 파일 경로
file_path = 'C:/Users/82108/.kaggle/music_data/top50.csv'  # 다운로드된 파일 경로에 맞춰 수정

# CSV 파일 읽기
music_data = pd.read_csv(file_path, encoding='ISO-8859-1')

# 불필요한 'Unnamed: 0' 컬럼 삭제
music_data = music_data.drop(columns=['Unnamed: 0'], errors='ignore')

# 컬럼 이름 변경
music_data.columns = ['Track_Name', 'Artist_Name', 'Genre', 'Beats_Per_Minute',
                        'Energy', 'Danceability', 'Loudness_dB', 'Liveness',
                        'Valence', 'Length', 'Acousticness', 'Speechiness', 'Popularity']

# 'mood'와 'time_of_day'를 생성하기 위한 간단한 조건을 설정

def get_mood(valence):
    if valence >= 0.5:
        return 'Positive'
    else:
        return 'Negative'

def get_time_of_day(energy, danceability):
    if energy > 0.7 and danceability > 0.7:
        return 'Night'  # 에너지와 댄스 가능성이 높은 곡은 밤에 어울린다
    else:
        return 'Day'  # 에너지가 낮거나 댄스하기 어려운 곡은 낮에 어울린다

# 새로운 컬럼 생성
music_data['mood'] = music_data['Valence'].apply(get_mood)
music_data['time_of_day'] = music_data.apply(lambda row: get_time_of_day(row['Energy'], row['Danceability']), axis=1)

# 필요한 컬럼만 추출
modified_data = music_data[['Track_Name', 'Artist_Name', 'Genre', 'mood', 'time_of_day']]

# 컬럼 이름 변경
modified_data.columns = ['title', 'artist', 'genre', 'mood', 'time_of_day']

# 수정된 데이터 확인
print(modified_data.head())

# MySQL 연결
engine = create_engine('mysql+pymysql://root:<비밀번호>@localhost:3306/location_music')

# 데이터프레임을 MySQL 테이블에 저장
try:
    modified_data.to_sql('songs', con=engine, if_exists='append', index=False)
    print("Data inserted into MySQL!")
except Exception as e:
    print(f"Error: {e}")

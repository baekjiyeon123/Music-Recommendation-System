import kaggle

# 데이터셋 다운로드
kaggle.api.dataset_download_files(
    'leonardopena/top50spotify2019',  # 데이터셋 이름
    path='./music_data',             # 데이터를 저장할 로컬 경로
    unzip=True                        # 압축 해제 옵션
)

print("다운로드 완료! ./music_data 디렉토리를 확인하세요.")

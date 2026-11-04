# pathlib.Path : 운영체제 독립적인 파일/폴더 경로 처리
from pathlib import Path
# os : 현재 작업 디렉터리 변경
import os
# cv2 : OpenCV 이미지 입출력 및 변환
import cv2
# numpy : 난수 생성 및 배열 연산
import numpy as np

# 제공 코드: 어느 작업 폴더에서 실행해도 현재 파일 옆의 입력을 읽습니다.
# OpenCV에는 영문 상대 경로를 전달합니다. 원본 파일은 덮어쓰지 않습니다.
# 현재 실행 중인 파이썬 파일이 위치한 폴더로 작업 디렉터리 변경
# - 실행 위치와 관계없이 스크립트가 있는 폴더를 기준으로 작업
# - 이후 사용하는 상대 경로("../data", "outputs")가 모두 스크립트 폴더를 기준으로 해석됨
os.chdir(Path(__file__).resolve().parent)

# csv : CSV 파일 읽기/쓰기
import csv
# json : 설정 또는 결과 JSON 처리용 (현재 코드에서는 미사용)
import json
# perf_counter : 성능 측정용 고해상도 타이머 (현재 코드에서는 미사용)
from time import perf_counter
# outputs 폴더 생성
# - 이미 존재하면 예외 발생하지 않음(exist_ok=True)
Path("outputs").mkdir(exist_ok=True)

# hashlib : SHA256 해시 계산
# - 원본 이미지 무결성 기록용
import hashlib

def augment(image,seed):
    # 시드를 고정한 난수 생성기 생성
    # - 같은 이미지와 같은 seed를 사용하면 동일한 증강 결과 생성 //난수 생성 순서와 OpenCV 처리 조건이 동일하다는 전제
    rng=np.random.default_rng(seed)
    # flip
    # - 50% 확률로 좌우 반전 수행 여부 결정
    # beta
    # - 밝기 변화량을 -20부터 +20까지 정수로 무작위 결정
    # - 음수: 어둡게 / 양수: 밝게 / 0: 변화 없음
    flip=bool(rng.random()<0.5); beta=int(rng.integers(-20,21))
    # if flip=True
    # - 좌우 반전 수행
    # else flip=False
    # - 원본 복사본 사용
    # - 좌우 반전하지 않는 경우에도 원본 배열을 직접 수정하지 않도록 복사
    result=cv2.flip(image,1) if flip else image.copy()
    # >>> TODO H06
    # beta를 적용하되 uint8의 순환을 막고 값 범위를 지키세요. 원본 image는 수정하지 않습니다.

    # 밝기(beta) 적용
    # - uint8은 0~255 범위의 정수만 표현
    # - 따라서 음수나 255 초과 값이 발생하지 않도록 int16으로 변환
    # - beta를 더해 밝기 조정
    # - np.clip()으로 0~255 범위로 제한
    # - astype(np.uint8)로 다시 이미지 자료형 변환
    result=np.clip(result.astype(np.int16)+beta,0,255).astype(np.uint8)
    # <<< TODO H06
    # 증강 이미지와 설정값 반환
    # - result : 증강 결과 이미지
    # - seed : 난수 생성에 사용한 시드
    # - flip : 좌우 반전 수행 여부(True/False)
    # - beta : 적용한 밝기 변화량
    return result,{"seed":seed,"flip":flip,"beta":beta}

# manifest.csv 로드
# - BOM 제거를 위해 utf-8-sig 사용
# - CSV의 첫 번째 행을 열 이름으로 사용
# - 각 데이터 행을 딕셔너리 형태로 읽음
# - 전체 데이터 행을 sources 리스트에 저장
with open("../data/manifest.csv",encoding="utf-8-sig",newline="") as f:
    sources=list(csv.DictReader(f))
# 결과 기록용 리스트
# - augmentation.csv 작성 시 사용
rows=[]
# sample_id 기준 정렬
# - 실행 시 항상 동일한 처리 순서 보장
for row in sorted(sources,key=lambda r:r["sample_id"]):
    # train 데이터만 증강
    # - valid/test 데이터는 모델 평가용이므로 증강하지 않음
    # - 평가 데이터가 학습 과정에 영향을 주지 않도록 분리 유지
    if row["split"]!="train":
        continue  # valid/test는 증강 대상이 아닙니다.
    # sample_id 끝 번호를 이용하여 시드 생성
    # - 기본 시드 42에 sample_id 마지막 번호를 더함
    # - 예: img_01 -> seed=43
    seed=42+int(row["sample_id"].split("_")[-1])
    # 원본 이미지 경로 생성
    # 이미지 로드
    # - OpenCV는 문자열 경로 사용
    src=Path("../data")/row["path"];image=cv2.imread(str(src))
    # 증강 수행
    # 출력 파일명 생성
    # - 예: sample_7_aug.png
    result,settings=augment(image,seed);dest=Path("outputs")/(row["sample_id"]+"_aug.png")
    # 증강 결과 저장
    # - 이미지 저장에 성공하면 True 반환
    # - 이미지 저장에 실패하면 False 반환
    # - 반환값을 saved 변수에 저장
    saved=cv2.imwrite(str(dest),result)
    # 처리 결과 기록
    # - sample_id : 샘플 ID
    # - split : 데이터 분할(train)
    # - dest : 출력 파일 경로
    # - seed : 사용 시드
    # - flip : 좌우 반전 여부
    # - beta : 밝기 변화값
    # - saved : 저장 성공 여부
    # - SHA256 : 원본 파일 해시값
    rows.append([row["sample_id"],row["split"],str(dest),seed,settings["flip"],settings["beta"],saved,hashlib.sha256(src.read_bytes()).hexdigest()])
# 증강 결과 메타데이터 저장
# - 각 이미지의 증강 설정 및 저장 결과 기록
with open("outputs/augmentation.csv","w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f);w.writerow(["id","split","output","seed","flip","beta","saved","source_sha256"]);w.writerows(rows)
# 실제 증강된 이미지 개수 출력
print("증강 이미지:",len(rows),"/ train만 처리")
# 각 이미지별 증강 설정 출력
# - r[0] : sample_id
# - r[3] : seed
# - r[4] : flip 여부
# - r[5] : beta 값
print("설정:",[(r[0],r[3],r[4],r[5]) for r in rows])

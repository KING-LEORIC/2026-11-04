from pathlib import Path
import os
import cv2
import numpy as np

# 제공 코드: 어느 작업 폴더에서 실행해도 현재 파일 옆의 입력을 읽습니다.
# OpenCV에는 영문 상대 경로를 전달합니다. 원본 파일은 덮어쓰지 않습니다.
os.chdir(Path(__file__).resolve().parent)

import csv
import json
from time import perf_counter
# 출력 결과를 저장할 outputs 디렉터리 생성
# - exist_ok=True : 이미 폴더가 있어도 오류를 발생시키지 않음
# - 필터 결과 이미지와 CSV 파일이 저장되는 위치
Path("outputs").mkdir(exist_ok=True)

from filters import apply_filter
from statistics import median

# 입력 영상 로드
# - "../data/noisy_gray.png" : 그레이스케일 잡음 영상
# - 0 : 흑백(Gray) 모드로 읽기
gray = cv2.imread("../data/noisy_gray.png",0)
# 필터별 측정 결과 저장 리스트
# - [필터명, 중앙값 처리시간(ms), 에지 픽셀 수] 형태로 저장
rows=[]
# 세 가지 필터 성능 비교 수행
# - gaussian : 가우시안 블러
# - sharpen : 샤프닝
# - bilateral : 양방향 필터
for name in ["gaussian","sharpen","bilateral"]:
    # 워밍업 실행
    # - 최초 실행 시 발생할 수 있는 초기화 비용 제외
    apply_filter(gray,name)  # 워밍업 제외
    # 실행 시간 측정값 저장 리스트
    # - 7회 반복 측정 후 중앙값 사용
    samples=[]
    # 필터 처리 시간 측정
    # - perf_counter() : 고해상도 시간 측정
    # - 처리 시간을 ms 단위로 저장
    for _ in range(7):
        start=perf_counter(); result=apply_filter(gray,name); samples.append((perf_counter()-start)*1000)
    # 에지 추출
    # - Canny Edge Detector 사용
    # - 임계값 : 80, 160
    edge=cv2.Canny(result,80,160)
    # 필터 결과 및 에지 결과 저장
    # - {필터명}.png
    # - {필터명}_edge.png
    cv2.imwrite(f"outputs/{name}.png",result);cv2.imwrite(f"outputs/{name}_edge.png",edge)
    # 결과 테이블에 기록
    # - name : 필터 이름
    # - median(samples) : 7회 측정 시간의 중앙값(ms)
    # - np.count_nonzero(edge) : 검출된 에지 픽셀 개수
    rows.append([name,median(samples),int(np.count_nonzero(edge))])
# 필터 비교 결과 CSV 저장
# - UTF-8 BOM 인코딩 사용
# - filter : 필터 이름
# - median_ms : 중앙 처리시간(ms)
# - edge_pixels : 에지 픽셀 수
with open("outputs/filter_comparison.csv","w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f);w.writerow(["filter","median_ms","edge_pixels"]);w.writerows(rows)
# 필터별 에지 픽셀 수 출력
# - 각 필터가 유지/생성한 에지 양 비교 가능
print("필터/Edge 픽셀:",[(r[0],r[2]) for r in rows])
# 시간 측정 기준 안내
# - 현재 실행 환경의 CPU 및 OpenCV 버전에 따라 값이 달라질 수 있음
# - 7회 측정값의 중앙값 사용
print("median_ms는 현재 CPU·OpenCV 환경의 7회 측정값입니다.")

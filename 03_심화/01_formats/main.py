from pathlib import Path
import os
import cv2
import numpy as np

# 제공 코드: 어느 작업 폴더에서 실행해도 현재 파일 옆의 입력을 읽습니다.
# OpenCV에는 영문 상대 경로를 전달합니다. 원본 파일은 덮어쓰지 않습니다.
# 현재 실행 중인 파이썬 파일의 위치로 작업 폴더 변경
# - Path(__file__).resolve().parent : 현재 파일이 있는 디렉터리
# - os.chdir(...) : 작업 디렉터리 이동
# - 어떤 위치에서 실행해도 동일한 상대경로 사용 가능
os.chdir(Path(__file__).resolve().parent)

import csv
import json
from time import perf_counter
# 결과 저장용 outputs 폴더 생성
# - exist_ok=True : 이미 폴더가 있어도 오류 발생 안 함
Path("outputs").mkdir(exist_ok=True)

# scene.png를 기본 컬러(BGR) 형식으로 읽기
# - image : 원본 컬러 영상
image = cv2.imread("../data/scene.png")
# >>> TODO H01
# IMREAD_GRAYSCALE로 scene.png를, IMREAD_UNCHANGED로 rgba.png를 읽으세요. 변수 이름은 gray, rgba입니다.
# 영상 파일 읽기
# - gray : scene.png를 흑백(1채널)로 읽은 영상
# - cv2.IMREAD_GRAYSCALE : 그레이스케일 모드
# - rgba : rgba.png를 원본 채널 그대로 읽은 영상
# - cv2.IMREAD_UNCHANGED : 알파 채널 포함 모든 채널 유지
gray = cv2.imread("../data/scene.png", cv2.IMREAD_GRAYSCALE)
rgba = cv2.imread("../data/rgba.png", cv2.IMREAD_UNCHANGED)
# <<< TODO H01
# PNG 형식으로 저장
# - 무손실 압축
# - 저장 후 픽셀값이 원본과 동일
cv2.imwrite("outputs/lossless.png", image)
# JPEG 형식으로 저장
# - 품질값 80
# - 손실 압축 적용
# - 원본과 픽셀값이 달라질 수 있음
cv2.imwrite("outputs/lossy.jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 80])
# 파일 비교 결과를 저장할 리스트
# - 파일명
# - 파일 크기
# - 평균 절대 오차(MAE)
# - 픽셀 완전 일치 여부
rows = []
# 저장된 두 파일의 품질 비교
# - lossless.png
# - lossy.jpg
for filename in ["lossless.png", "lossy.jpg"]:
    # 비교 대상 파일 경로 생성
    # - outputs 폴더 안의 파일 지정
    p = Path("outputs") / filename
    # 저장된 파일 다시 읽기
    # - readback : 복원 영상
    readback = cv2.imread(str(p))
    # 평균 절대 오차(MAE) 계산
    # - float32로 변환 후 차이 계산
    # - 값이 작을수록 원본과 유사
    mae = float(np.abs(image.astype(np.float32) - readback.astype(np.float32)).mean())
    # 비교 결과 저장
    # - filename : 파일명
    # - p.stat().st_size : 파일 크기(byte)
    # - round(mae, 5) : 평균 절대 오차
    # - np.array_equal(...) : 픽셀 단위 완전 일치 여부
    rows.append([filename, p.stat().st_size, round(mae, 5), np.array_equal(image, readback)])
# 비교 결과 CSV 저장
# - format_comparison.csv 생성
# - utf-8-sig : 엑셀 한글 깨짐 방지
with open("outputs/format_comparison.csv", "w", encoding="utf-8-sig", newline="") as f:
    # CSV 헤더 작성
    # - file : 파일명
    # - bytes : 파일 크기
    # - pixel_mae : 평균 절대 오차
    # - pixel_equal : 픽셀 완전 일치 여부
    # 비교 데이터 기록
    w = csv.writer(f); w.writerow(["file", "bytes", "pixel_mae", "pixel_equal"]); w.writerows(rows)
# 읽어들인 영상의 크기 출력
# - gray.shape : 그레이스케일 영상 크기
# - rgba.shape : RGBA 영상 크기
print("Gray/UNCHANGED shape:", gray.shape, rgba.shape)
# 알파 채널 범위 출력
# - rgba[:,:,3] : 알파 채널
# - min() : 최소 투명도
# - max() : 최대 투명도
print("Alpha range:", int(rgba[:,:,3].min()), int(rgba[:,:,3].max()))
# 파일 비교 결과 출력
# - PNG/JPEG 품질 및 크기 비교 결과
print(rows)

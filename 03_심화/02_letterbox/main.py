# pathlib.Path
# - 파일 및 디렉터리 경로를 객체 형태로 다루기 위한 모듈
# - 운영체제에 독립적인 경로 처리 지원
from pathlib import Path
# os
# - 현재 작업 디렉터리 변경 등 운영체제 기능 제공
import os
# OpenCV 라이브러리
# - 이미지 입출력 및 영상 처리 기능 제공
import cv2
# NumPy 라이브러리
# - 배열 연산과 영상 데이터 처리에 사용
import numpy as np

# 제공 코드: 어느 작업 폴더에서 실행해도 현재 파일 옆의 입력을 읽습니다.
# OpenCV에는 영문 상대 경로를 전달합니다. 원본 파일은 덮어쓰지 않습니다.
# 현재 파이썬 파일이 위치한 디렉터리로 작업 위치 변경
# - 상대 경로 기준을 고정하기 위함
os.chdir(Path(__file__).resolve().parent)

# csv 모듈
# - CSV 파일 입출력 기능 제공
# - 현재 코드에서는 사용되지 않음
import csv
# json 모듈
# - 파이썬 객체를 JSON 문자열로 저장/로드
import json
# perf_counter
# - 정밀한 실행 시간 측정 함수
# - 현재 코드에서는 사용되지 않음
from time import perf_counter
# 결과 저장용 outputs 디렉터리 생성
# - 이미 존재하면 오류 없이 통과
Path("outputs").mkdir(exist_ok=True)

def letterbox(image, size=(224, 224)):
    """비율을 유지해 채운 뒤 남는 가장자리에 검정을 추가합니다. size=(W,H)."""
    # 입력 이미지의 높이(height)와 너비(width) 추출
    height, width = image.shape[:2]
    # 비율을 유지하면서 목표 크기에 맞추기 위한 배율 계산
    # - 가로 기준 배율과 세로 기준 배율 중 작은 값 사용
    ratio = min(size[0]/width, size[1]/height)
    # 비율 유지 후 resize될 크기 계산
    new_w, new_h = round(width*ratio), round(height*ratio)
    # 좌측 패딩 크기와 상단 패딩 크기 계산
    # - 이미지를 중앙 정렬하기 위한 위치 정보
    left = (size[0]-new_w)//2; top = (size[1]-new_h)//2
    # >>> TODO H02
    # new_w·new_h로 Resize한 뒤 top/bottom/left/right 여백을 추가해 size와 같은 크기를 만드세요. result에 저장합니다.
    
    # 원본 이미지를 비율 유지 상태로 resize
    resized = cv2.resize(image, dsize=(new_w, new_h))
    # 우측 패딩 크기 계산
    # - 최종 가로 길이를 size[0]으로 맞춤
    right = size[0] - new_w - left
    # 하단 패딩 크기 계산
    # - 최종 세로 길이를 size[1]로 맞춤
    bottom = size[1] - new_h - top
    # 검은색 패딩 추가
    # - BORDER_CONSTANT : 지정 색상으로 채움
    # - value=(0,0,0) : 검은색(BGR)
    result = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    # <<< TODO H02
    # Letterbox 결과 이미지와 변환 설정 정보 반환
    return result, {"resized_wh":[new_w,new_h],"left":left,"top":top,"ratio":ratio}

# 이미지 파일 읽기
# - OpenCV는 이미지를 BGR 형식으로 로드
image = cv2.imread("../data/scene.png")
# BGR 색공간을 HSV 색공간으로 변환
# - 색상 범위 기반 객체 추출에 유리
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
# 녹색 계열 영역 검출을 위한 이진 마스크 생성
# - 범위 내 픽셀은 255
# - 범위 밖 픽셀은 0
mask = cv2.inRange(hsv, (35,80,60), (85,255,255))
# 마스크 영역만 원본 이미지에서 추출
# - 녹색 영역만 남김
masked = cv2.bitwise_and(image, image, mask=mask)
# Letterbox 변환 수행
# - 결과 이미지와 설정 정보 반환
result, settings = letterbox(image)
# 녹색 마스크 이미지 저장
# 녹색 영역만 추출한 이미지 저장
cv2.imwrite("outputs/green_mask.png", mask);cv2.imwrite("outputs/green_only.png", masked)
# Letterbox 결과 이미지 저장
cv2.imwrite("outputs/letterbox.png", result)
# 설정 정보를 JSON 형식으로 저장
# - resized_wh : resize 결과 크기
# - left, top : 패딩 시작 위치
# - ratio : 적용된 크기 비율
Path("outputs/resize.json").write_text(json.dumps(settings,indent=2),encoding="utf-8")
# 결과 이미지 크기와 설정 정보 출력
print("Letterbox:",result.shape,settings)
# 마스크에서 0이 아닌 픽셀 수 계산
# - 검출된 녹색 영역의 픽셀 개수
print("녹색 Mask 픽셀:",int(np.count_nonzero(mask)))

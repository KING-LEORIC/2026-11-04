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
# 출력 결과를 저장할 outputs 폴더 생성
# - exist_ok=True : 이미 폴더가 존재해도 오류를 발생시키지 않음
# - morphology 결과 이미지와 csv 파일이 이 폴더에 저장됨
Path("outputs").mkdir(exist_ok=True)


# 입력 영상 읽기
# - "../data/objects.png" : 원본 이미지 경로
# - 0 : 그레이스케일(단일 채널)로 읽기
gray=cv2.imread("../data/objects.png",0)
# 이진화 수행
# - 임계값(threshold) : 127
# - 127 이하 → 0
# - 127 초과 → 255
# - binary : 형태학 연산에 사용할 이진 이미지
_, binary=cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
# 실험 결과를 저장할 리스트
# - 각 설정별 foreground 픽셀 수와 연결 성분 개수를 저장
rows=[]
# 형태학 연산 설정 반복
# - rect : 사각형 구조 요소
# - ellipse : 타원형 구조 요소
for shape_name,shape in [("rect",cv2.MORPH_RECT),("ellipse",cv2.MORPH_ELLIPSE)]:
    # 구조 요소 크기 반복
    # - 3x3
    # - 5x5
    for size in [3,5]:
        # Opening 반복 횟수 반복
        # - 1회
        # - 2회
        for iterations in [1,2]:
            # 구조 요소(커널) 생성
            # - shape : 구조 요소 형태
            # - (size,size) : 구조 요소 크기
            kernel=cv2.getStructuringElement(shape,(size,size))
            # >>> TODO H04
            # 현재 kernel과 iterations를 사용하여 binary에 Opening을 적용하세요.

            # Opening 적용
            # - binary : 입력 이진 영상
            # - MORPH_OPEN : 침식(Erosion) 후 팽창(Dilation) 수행하는 열기 연산 //작은 노이즈는 사라지고 큰 객체만 남는 효과
            # -- 침식(Erosion): 흰색 객체를 깎아서 작게 만듦
            # -- 팽창(Dilation): 깎인 객체를 다시 키움
            # - kernel : 현재 실험에 사용할 구조 요소
            # - iterations : 연산 반복 횟수
            # - result : Opening 결과 영상
            result=cv2.morphologyEx(binary,cv2.MORPH_OPEN,kernel,iterations=iterations)
            # <<< TODO H04
            # 연결 성분 분석 수행
            # - connectivity=8 : 8방향 연결 기준
            # - count : 전체 라벨 수(배경 포함)
            # - labels : 픽셀별 라벨 맵
            # - stats : 각 성분의 통계 정보
            # - centroids : 각 성분의 중심 좌표
            count, labels, stats, centroids=cv2.connectedComponentsWithStats(result,connectivity=8)
            # 현재 실험 설정 이름 생성
            # 예) rect_3_1, ellipse_5_2
            name=f"{shape_name}_{size}_{iterations}"
            # Opening 결과 영상 저장
            # - outputs 폴더에 설정별 PNG 파일 생성
            cv2.imwrite(f"outputs/{name}.png",result)
            # 결과 기록
            # - name : 실험 설정 이름
            # - np.count_nonzero(result) : foreground(255) 픽셀 개수
            # - count-1 : 배경을 제외한 연결 성분 개수
            rows.append([name,int(np.count_nonzero(result)),count-1])
# CSV 파일 저장
# - utf-8-sig : Excel 한글 호환 인코딩
# - newline="" : 빈 줄 생성 방지
with open("outputs/morphology.csv","w",encoding="utf-8-sig",newline="") as f:
    # CSV 작성 객체 생성
    # 헤더 작성
    # 실험 결과 작성
    w=csv.writer(f);w.writerow(["setting","foreground_pixels","components_without_background"]);w.writerows(rows)
# 최종 결과 출력
# - 각 설정별 foreground 픽셀 수
# - 각 설정별 연결 성분 개수
print(rows)

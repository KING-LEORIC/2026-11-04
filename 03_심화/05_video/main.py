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
# 출력 폴더 생성
# - "outputs" : 처리 결과 저장 폴더
# - exist_ok=True : 폴더가 이미 존재해도 오류 없이 진행
Path("outputs").mkdir(exist_ok=True)

from video_ops import process_frame
# 입력 비디오 열기
# - "../data/sample.avi" : 입력 비디오 파일
# - cap : 비디오 캡처 객체
# - fps : 입력 비디오의 프레임 속도(FPS)
cap=cv2.VideoCapture("../data/sample.avi");fps=cap.get(cv2.CAP_PROP_FPS)
# 출력 비디오 생성
# - "outputs/edge.avi" : 저장할 비디오 파일
# - MJPG : 비디오 코덱
# - fps : 저장할 프레임 속도
# - (160,120) : 저장할 프레임 크기
writer=cv2.VideoWriter("outputs/edge.avi",cv2.VideoWriter_fourcc(*"MJPG"),fps,(160,120))
# 처리 통계 변수 초기화
# - count : 저장한 프레임 수
# - processing : 프레임별 처리 시간 저장 리스트
# - start_all : 전체 실행 시간 측정 시작 시각
count=0;processing=[];start_all=perf_counter()
# 비디오를 프레임 단위로 읽어 처리
# - cap.isOpened() : 입력 비디오 사용 가능 여부
# - writer.isOpened() : 출력 비디오 사용 가능 여부
while cap.isOpened() and writer.isOpened():
    # 프레임 읽기
    # - ok : 프레임 읽기 성공 여부
    # - frame : 읽어온 원본 프레임
    ok,frame=cap.read()
    # 더 이상 읽을 프레임이 없으면 종료
    if not ok: break
    # 프레임 처리 시간 측정
    # - process_frame(frame) : 프레임 영상 처리 함수
    # - result : 처리 완료된 프레임
    # - processing : 처리 시간 기록
    start=perf_counter();result=process_frame(frame);processing.append(perf_counter()-start)
    # 처리된 프레임 저장
    # - result : edge 처리된 프레임
    # 저장 프레임 수 증가
    writer.write(result);count+=1
# 입력/출력 비디오 객체 해제
# 전체 실행 시간 계산
# - wall : 읽기 + 처리 + 저장 전체 소요 시간
cap.release();writer.release();wall=perf_counter()-start_all
# 저장된 비디오를 다시 열어 정보 확인
# - check : 저장 결과 검사용 비디오 객체
check=cv2.VideoCapture("outputs/edge.avi")
# 결과 통계 생성
# - frames_written : 저장한 프레임 수
# - reopened_frames : 저장 후 다시 읽은 프레임 수
# - fps : 저장된 비디오 FPS
# - width : 저장된 비디오 가로 크기
# - height : 저장된 비디오 세로 크기
# - wall_s : 전체 실행 시간(초)
# - mean_process_ms : 프레임 처리 평균 시간(ms)
report={"frames_written":count,"reopened_frames":int(check.get(7)),"fps":check.get(5),"width":int(check.get(3)),"height":int(check.get(4)),"wall_s":wall,"mean_process_ms":float(np.mean(processing)*1000)}
# 검사용 비디오 객체 해제
check.release()
# 처리 결과를 JSON 파일로 저장
# - report : 처리 통계 정보
# - indent=2 : 보기 좋은 형식으로 저장
Path("outputs/video_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
# 저장된 비디오 정보 출력
# - reopened_frames : 프레임 수
# - fps : 프레임 속도
# - (width,height) : 비디오 크기
print("Frame/FPS/크기:",report["reopened_frames"],report["fps"],(report["width"],report["height"]))
# 시간 측정 기준 안내
# - wall : read + process + write 포함
# - mean_process : process_frame 수행 시간만 계산
print("wall은 read·처리·write 포함, mean_process는 Frame 처리만 포함합니다.")

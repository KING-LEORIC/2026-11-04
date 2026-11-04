# 파일 및 경로 처리를 위한 라이브러리
from pathlib import Path
# 운영체제 관련 기능
import os
# OpenCV 이미지 및 영상 처리 라이브러리
import cv2
# 배열 및 수치 연산 라이브러리
import numpy as np

# 제공 코드: 어느 작업 폴더에서 실행해도 현재 파일 옆의 입력을 읽습니다.
# OpenCV에는 영문 상대 경로를 전달합니다. 원본 파일은 덮어쓰지 않습니다.
os.chdir(Path(__file__).resolve().parent)

# CSV 파일 읽기
import csv
# JSON 파일 읽기 및 저장
import json
# 실행 시간 측정 함수
from time import perf_counter
# 결과 저장 폴더 생성
Path("outputs").mkdir(exist_ok=True)

# 파일 무결성 확인 라이브러리
import hashlib
# 이미지 처리 결과 CSV 파일 열기
# - encoding="utf-8-sig" : UTF-8 BOM을 포함한 CSV 읽기
# - newline="" : CSV 줄바꿈 처리
with open("outputs/result_summary.csv",encoding="utf-8-sig",newline="") as f:
    # CSV 데이터를 딕셔너리 형태로 읽기
    # - csv.DictReader() : 첫 번째 행을 열 이름으로 사용
    # - rows : 각 이미지 처리 결과를 담은 딕셔너리 목록
    rows=list(csv.DictReader(f))
# 이미지 검증 결과를 저장할 리스트
checks=[]
# CSV에 기록된 이미지 처리 결과를 한 행씩 검증
for row in rows:
    # 저장된 결과 이미지 다시 읽기
    # - row["output"] : CSV에 기록된 이미지 파일 경로
    # - cv2.IMREAD_UNCHANGED : 원본 채널과 자료형 유지
    # - image : 다시 읽어온 이미지 배열
    image=cv2.imread(row["output"],cv2.IMREAD_UNCHANGED)
    # >>> TODO H10
    # 읽은 image의 존재·(높이,너비)·dtype·채널을 CSV와 비교해 bool ok를 만드세요. 보고서의 의미 판단을 자동 채점하는 코드는 아닙니다.

    # 이미지가 정상적으로 읽혔는지 먼저 확인
    # - image is not None : 파일이 존재하고 OpenCV가 정상적으로 읽었는지 확인
    # - 이미지가 None이면 이후 shape 등에 접근하지 않음
    if image is not None:
        # 실제 이미지의 높이와 너비 확인
        # - image.shape[:2] : (높이, 너비)
        # - height : 실제 이미지 높이
        # - width : 실제 이미지 너비
        height,width=image.shape[:2]
        # 실제 이미지의 채널 수 확인
        # - image.ndim==2 : Grayscale 이미지이므로 1채널
        # - image.ndim==3 : 마지막 차원에서 채널 수 확인
        channels=1 if image.ndim==2 else image.shape[2]
        # CSV에 기록된 이미지 정보와 실제 이미지 정보 비교
        # - height : 실제 이미지 높이
        # - row["height"] : CSV에 기록된 이미지 높이
        # - width : 실제 이미지 너비
        # - row["width"] : CSV에 기록된 이미지 너비
        # - channels : 실제 이미지 채널 수
        # - row["channels"] : CSV에 기록된 채널 수
        # - str(image.dtype) : 실제 이미지 자료형
        # - row["dtype"] : CSV에 기록된 자료형
        # - row["roundtrip_equal"] : 저장 전후 이미지 데이터 일치 여부
        # - 모든 조건이 True이면 ok=True
        ok=(height==int(row["height"]) and width==int(row["width"]) and channels==int(row["channels"]) and str(image.dtype)==row["dtype"] and row["roundtrip_equal"]=="True")
    else:
        # 이미지 파일을 읽지 못했으면 검증 실패
        ok=False
    # <<< TODO H10
    # 현재 이미지의 검증 결과 추가
    # - checks : 각 이미지의 검증 결과 목록
    # - True : 검증 통과
    # - False : 검증 실패
    checks.append(ok)
# 원본 파일의 해시값이 저장된 JSON 파일 읽기
# - source_hashes.json : 원본 이미지와 영상의 해시값
original_hashes=json.loads(Path("outputs/source_hashes.json").read_text(encoding="utf-8"))
# 원본 파일이 변경되지 않았는지 확인
# - original_hashes.items() : 파일명과 원본 해시값 목록
# - Path("data")/name : 원본 파일 경로
# - hashlib.sha256() : 현재 파일의 SHA-256 해시 계산
# - digest : 실행 전에 기록했던 원본 해시값
# - all() : 모든 파일의 해시값이 일치하면 True
source_unchanged=all(hashlib.sha256((Path("data")/name).read_bytes()).hexdigest()==digest for name,digest in original_hashes.items())
# 처리된 영상 파일 열기
# - outputs/processed.avi : 처리 결과 영상
# 영상 Frame 개수 초기화
# 각 Frame의 크기를 기록할 리스트
video=cv2.VideoCapture("outputs/processed.avi");count=0;shapes=[]
# 영상이 열려 있는 동안 Frame 읽기
while video.isOpened():
    # 다음 Frame 읽기
    # - ok : 읽기 성공 여부
    # - frame : 읽은 Frame 이미지
    ok,frame=video.read()
    # Frame 읽기에 실패하면 반복 종료
    if not ok:break
    # 읽은 Frame 개수 증가
    # Frame의 크기 기록
    # - frame.shape : (높이, 너비, 채널)
    # - shapes : 모든 Frame의 크기를 저장하는 리스트
    count+=1;shapes.append(frame.shape)
# 처리된 영상의 FPS 확인
# - cv2.CAP_PROP_FPS : 초당 Frame 수
# 영상 객체 해제
fps=video.get(cv2.CAP_PROP_FPS);video.release()
# 최종 검증 보고서 생성
# - image_rows : CSV에 기록된 이미지 처리 결과 행 수
# - images_ok : 21개 이미지가 모두 존재하고 검증에 통과했는지 확인
# - source_unchanged : 원본 파일이 변경되지 않았는지 확인
# - video_ok : 영상의 Frame 수, FPS, 크기가 정상인지 확인
report={"image_rows":len(rows),"images_ok":len(rows)==21 and all(checks),"source_unchanged":source_unchanged,"video_ok":count==48 and fps==12 and all(s==(120,160,3) for s in shapes)}
# 최종 검증 결과를 JSON 파일로 저장
# - validation.json : 전체 검증 결과
# - indent=2 : JSON 들여쓰기 2칸
Path("outputs/validation.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
# 최종 검증 결과 출력
print(report)

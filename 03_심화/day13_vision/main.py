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

# CSV 파일 생성 및 저장 라이브러리
import csv
# JSON 파일 생성 및 저장 라이브러리
import json
# 실행 시간 측정 함수
from time import perf_counter
# 결과 저장 폴더 생성
# - outputs : 결과 이미지, 영상, 보고서를 저장할 폴더
# - exist_ok=True : 폴더가 이미 존재해도 오류 발생 방지
Path("outputs").mkdir(exist_ok=True)

# 파일 무결성 확인을 위한 해시 라이브러리
import hashlib
# 이미지 처리 함수와 영상 처리 함수 가져오기
from image_ops import prepare_image,augment_image
from video_ops import process_video

# 이미지 처리 결과를 저장할 리스트
# - rows : 이미지별 처리 결과와 이미지 정보를 저장
# - source_hashes : 원본 파일의 SHA-256 해시값을 저장
rows=[];source_hashes={}
# 처리할 이미지 파일 목록
# - scene.png : 일반 이미지
# - noisy.png : 노이즈가 포함된 이미지
# - objects.png : 여러 객체가 포함된 이미지
for filename in ["scene.png","noisy.png","objects.png"]:
    # 원본 이미지 파일 경로 설정
    # - Path("data") : 원본 이미지가 저장된 폴더
    # - filename : 현재 처리할 파일명
    # 원본 파일의 SHA-256 해시값 계산
    # - read_bytes() : 파일을 바이너리 데이터로 읽음
    # - hashlib.sha256() : SHA-256 해시 계산
    # - hexdigest() : 해시값을 16진수 문자열로 반환
    # - source_hashes : 파일명과 해시값을 저장하는 딕셔너리
    src=Path("data")/filename;source_hashes[filename]=hashlib.sha256(src.read_bytes()).hexdigest()
    # 원본 이미지 읽기
    # - cv2.imread() : 이미지 파일 읽기
    # - str(src) : Path 객체를 문자열 경로로 변환
    # - image : 원본 BGR 이미지
    # 이미지 전처리 실행 시간 측정 시작
    # Grayscale, Resize, Blur, Threshold, Morphology, Edge 처리
    # - prepare_image() : 이미지 전처리 함수
    # - results : 각 처리 단계의 결과를 담은 딕셔너리
    # 이미지 전처리 실행 시간 측정 종료
    # - perf_counter() : 고해상도 시간 측정
    # - seconds : 이미지 전처리에 걸린 시간(초)
    image=cv2.imread(str(src));start=perf_counter();results=prepare_image(image);seconds=perf_counter()-start
    # 데이터 증강(Augmentation) 실행
    # - cv2.resize(image,(160,120)) : 원본 이미지를 160x120으로 축소
    # - interpolation=cv2.INTER_AREA : 이미지 축소에 적합한 보간법
    # - augment_image() : 좌우 반전 및 밝기 증가
    # - results["aug"] : 증강 이미지 저장
    results["aug"]=augment_image(cv2.resize(image,(160,120),interpolation=cv2.INTER_AREA))
    # >>> TODO H09
    # results의 각 stage/result를 PNG로 저장하고 재읽기 비교와 크기·채널을 rows에 기록하세요. CSV 열은 코드의 예시 구조를 참고합니다.
    
    # 저장할 이미지 처리 단계 목록
    # - results.items() : 딕셔너리의 키와 값을 순서대로 가져옴
    # - stage : 처리 단계 이름(gray, small, blur, binary, opened, edge, aug)
    # - stage_image : 해당 처리 단계의 이미지 배열
    for stage,stage_image in results.items():
        # 처리 단계별 출력 파일명 생성
        # - src.stem : 확장자를 제외한 원본 파일명
        # - stage : 이미지 처리 단계 이름
        # - .png : 저장할 이미지 파일 형식
        # - output_path : 결과 이미지 저장 경로
        output_path=Path("outputs")/f"{src.stem}_{stage}.png"
        # 처리 결과를 PNG 이미지로 저장
        # - cv2.imwrite() : 이미지 파일 저장
        # - output_path : 저장할 파일 경로
        # - stage_image : 저장할 이미지 배열
        cv2.imwrite(str(output_path),stage_image)
        # 저장된 PNG 이미지를 다시 읽기
        # - cv2.IMREAD_UNCHANGED : 원본 채널 및 자료형을 유지하여 읽기
        # - saved_image : 다시 읽어온 이미지 배열
        saved_image=cv2.imread(str(output_path),cv2.IMREAD_UNCHANGED)
        # 저장 전후 이미지 데이터가 동일한지 비교
        # - np.array_equal() : 두 배열의 모양과 모든 원소가 동일한지 검사
        # - stage_image : 저장 전 이미지
        # - saved_image : 저장 후 다시 읽은 이미지
        # - roundtrip_equal : 저장 및 재읽기 결과가 동일하면 True
        roundtrip_equal=saved_image is not None and np.array_equal(stage_image,saved_image)
        # 다시 읽은 이미지의 크기와 채널 정보 확인
        # - saved_image.shape : 이미지 배열의 형태
        # - shape[0] : 이미지 높이(height)
        # - shape[1] : 이미지 너비(width)
        # - ndim : 배열의 차원 수
        # - 2차원 이미지 : Grayscale, 채널 수 1
        # - 3차원 이미지 : 컬러 이미지, 마지막 차원이 채널 수
        height,width=saved_image.shape[:2]
        channels=1 if saved_image.ndim==2 else saved_image.shape[2]
        # 이미지 처리 결과를 CSV 기록용 딕셔너리로 구성
        # - source : 원본 이미지 파일명
        # - stage : 이미지 처리 단계
        # - output : 저장된 결과 이미지 경로
        # - height : 이미지 높이
        # - width : 이미지 너비
        # - channels : 이미지 채널 수
        # - dtype : 이미지 배열의 자료형
        # - roundtrip_equal : 저장 전후 이미지 데이터 일치 여부
        row={"source":filename, "stage":stage, "output":str(output_path), "height":height, "width":width, "channels":channels, "dtype":str(saved_image.dtype), "roundtrip_equal":roundtrip_equal}
        # 현재 이미지 처리 결과를 전체 결과 목록에 추가
        # - rows : 모든 원본 이미지의 처리 결과를 저장하는 리스트
        # - append() : 리스트 마지막에 새로운 결과 추가
        rows.append(row)

    # <<< TODO H09
    # 비교용 이미지 생성
    # - cv2.resize(image,(160,120)) : 원본 이미지를 160x120으로 축소
    # - cv2.cvtColor(results["small"],cv2.COLOR_GRAY2BGR) : 흑백 이미지를 3채널로 변환
    # - cv2.cvtColor(results["edge"],cv2.COLOR_GRAY2BGR) : Edge 이미지를 3채널로 변환
    # - cv2.hconcat() : 이미지를 가로 방향으로 연결
    # - preview : 원본, 축소 이미지, Edge 이미지 비교 결과
    preview=cv2.hconcat([cv2.resize(image,(160,120)),cv2.cvtColor(results["small"],cv2.COLOR_GRAY2BGR),cv2.cvtColor(results["edge"],cv2.COLOR_GRAY2BGR)])
    # 비교용 이미지 저장
    # - src.stem : 원본 파일명
    # - _compare.png : 비교 이미지 파일명
    cv2.imwrite(f"outputs/{src.stem}_compare.png",preview)
# 원본 영상 파일의 SHA-256 해시값 계산
# - data/sample.avi : 입력 영상 파일
# - read_bytes() : 영상 파일을 바이너리 데이터로 읽음
# - source_hashes : 원본 파일 해시값 저장 딕셔너리
source_hashes["sample.avi"]=hashlib.sha256(Path("data/sample.avi").read_bytes()).hexdigest()
# 영상 처리 함수 실행
# - data/sample.avi : 원본 영상
# - outputs/processed.avi : 처리된 영상 저장 경로
# - process_video() : Frame 단위 영상 처리
# - video : 영상 처리 결과 보고서
video=process_video("data/sample.avi","outputs/processed.avi")
# 이미지 처리 결과 CSV 파일 생성
# - result_summary.csv : 이미지 처리 결과 파일
# - encoding="utf-8-sig" : Excel에서 한글이 깨지는 현상 방지
# - newline="" : CSV 파일의 불필요한 빈 줄 방지
with open("outputs/result_summary.csv","w",encoding="utf-8-sig",newline="") as f:
    # CSV 작성 객체 생성
    # - csv.DictWriter() : 딕셔너리 데이터를 CSV로 기록
    # - fieldnames=list(rows[0]) : 첫 번째 결과 딕셔너리의 키를 CSV 열 이름으로 사용
    # CSV 첫 번째 행에 열 이름 기록
    # 모든 이미지 처리 결과 기록
    # - rows : 이미지 21개 처리 결과
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# 원본 파일 해시값을 JSON 파일로 저장
# - indent=2 : JSON 들여쓰기 2칸
# - encoding="utf-8" : UTF-8 인코딩
Path("outputs/source_hashes.json").write_text(json.dumps(source_hashes,indent=2),encoding="utf-8")
# 영상 처리 결과 보고서를 JSON 파일로 저장
Path("outputs/video_report.json").write_text(json.dumps(video,indent=2),encoding="utf-8")
# 이미지 처리 결과 행 개수 출력
print("이미지 처리표:",len(rows),"행")
# 영상 처리 Frame 개수와 FPS 출력
print("영상 Frame/FPS:",video["decoded"],video["fps"])
# 다음 실행할 검증 프로그램 안내
print("다음: python validate.py")

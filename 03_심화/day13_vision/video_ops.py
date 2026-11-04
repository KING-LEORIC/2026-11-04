# OpenCV 영상 처리 라이브러리
import cv2
# 실행 시간 측정 함수
from time import perf_counter
# 이미지 전처리 함수 가져오기
from image_ops import prepare_image

# 영상 처리 함수 정의
# - source : 입력 영상 경로
# - destination : 처리된 영상 저장 경로
# - 반환값 : 영상 처리 결과 보고서
def process_video(source,destination):
    """한 번 열고 Frame을 순서대로 처리합니다. 코덱 성공 여부도 반환합니다."""
    # 입력 영상 열기
    # - cv2.VideoCapture() : 영상 파일 읽기 객체 생성
    # - source : 입력 영상 파일 경로
    # - cap : 영상의 Frame을 읽는 객체
    # 원본 영상의 FPS 확인
    # - cv2.CAP_PROP_FPS : 초당 Frame 수
    # - fps : 원본 영상의 FPS
    cap=cv2.VideoCapture(str(source));fps=cap.get(cv2.CAP_PROP_FPS)
    # 출력 영상 저장 객체 생성
    # - cv2.VideoWriter() : 영상 파일 저장 객체
    # - destination : 출력 영상 경로
    # - cv2.VideoWriter_fourcc(*"MJPG") : MJPG 코덱 지정
    # - fps : 초당 저장할 Frame 수
    # - (160,120) : 출력 영상 크기(너비, 높이)
    writer=cv2.VideoWriter(str(destination),cv2.VideoWriter_fourcc(*"MJPG"),fps,(160,120))
    # 입력 영상과 출력 영상 객체가 정상적으로 열렸는지 확인
    # - cap.isOpened() : 입력 영상 열기 성공 여부
    # - writer.isOpened() : 출력 영상 저장 객체 생성 성공 여부
    # - opened : 두 조건이 모두 True이면 영상 처리 진행
    # 처리한 Frame 개수 초기화
    # 영상 처리 시작 시간 기록
    opened=cap.isOpened() and writer.isOpened();count=0;start=perf_counter()
     # 영상 객체가 정상적으로 열렸다면 Frame 처리 반복
    while opened:
        # 다음 Frame 읽기
        # - cap.read() : 영상에서 다음 Frame을 읽음
        # - ok : Frame 읽기 성공 여부
        # - frame : 읽어온 이미지 배열
        ok,frame=cap.read()
        # Frame 읽기에 실패하면 반복 종료
        # - ok=False : 더 이상 읽을 Frame이 없거나 읽기 실패
        if not ok:break
        # >>> TODO H08
        # prepare_image(frame)의 edge 결과를 3채널로 바꾸고 writer에 전달하세요.
        
        # 현재 Frame의 이미지 전처리 실행
        # - prepare_image(frame) : Grayscale, Resize, Blur, Threshold, Morphology, Edge 처리
        # - processed : 처리 결과를 담은 딕셔너리
        processed=prepare_image(frame)
        # Edge 이미지 추출
        # - processed["edge"] : Canny Edge Detection 결과
        # - edge : 160x120 크기의 1채널 흑백 이미지
        edge=processed["edge"]
        # Edge 이미지를 3채널 BGR 이미지로 변환
        # - cv2.COLOR_GRAY2BGR : 1채널 Grayscale을 3채널 BGR로 변환
        # - edge : 입력 Edge 이미지
        # - edge_bgr : 3채널로 변환된 Edge 이미지
        # - VideoWriter는 지정된 영상 크기와 채널 형식에 맞는 Frame을 필요로 함
        edge_bgr=cv2.cvtColor(edge,cv2.COLOR_GRAY2BGR)
        # Edge 처리 결과를 출력 영상에 기록
        # - writer.write() : 현재 Frame을 영상 파일에 기록
        # - edge_bgr : 저장할 3채널 Edge 이미지
        writer.write(edge_bgr)
        # <<< TODO H08
        # 정상적으로 처리한 Frame 개수 증가
        count+=1
    # 입력 영상 객체 해제
    # 출력 영상 객체 해제 및 파일 저장 마무리
    cap.release();writer.release()
    # 저장된 결과 영상을 다시 열기
    # - check : 저장된 영상의 정보를 확인하는 객체
    check=cv2.VideoCapture(str(destination))
    # 영상 처리 결과 보고서 작성
    # - opened : 입력 및 출력 영상 객체 열기 성공 여부
    # - written : 실제 처리하여 기록한 Frame 수
    # - decoded : 저장된 영상에서 확인되는 전체 Frame 수
    # - fps : 저장된 영상의 FPS
    # - width : 저장된 영상의 너비
    # - height : 저장된 영상의 높이
    # - wall_s : 전체 영상 처리 소요 시간
    report={"opened":opened,"written":count,"decoded":int(check.get(7)),"fps":check.get(5),"width":int(check.get(3)),"height":int(check.get(4)),"wall_s":perf_counter()-start}
    # 결과 영상 확인 객체 해제
    # 영상 처리 보고서 반환
    check.release();return report

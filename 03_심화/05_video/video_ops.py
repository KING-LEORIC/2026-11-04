import cv2

def process_frame(frame):
    """컬러 Frame을 고정 크기의 Edge 컬러 Frame으로 바꿉니다."""
    # >>> TODO H05
    # Resize160×120→Gray→Gaussian3×3→Canny80/160 순서로 edge를 만드세요. 파일 열기·종료는 main이 담당합니다.
    
    # 입력 프레임 전처리 및 에지 검출
    # - frame : 원본 BGR 컬러 영상
    # - Resize(160×120) → Gray → GaussianBlur(3×3) → Canny(80,160)
    # - 생성된 edge는 단일 채널(흑백) 에지 영상
    # 프레임 크기 조정
    # - frame : 원본 프레임
    # - (160,120) : 출력 해상도
    # - INTER_AREA : 축소(Downsampling) 시 품질 손실을 줄이기 위한 보간법
    small=cv2.resize(frame,(160,120), interpolation=cv2.INTER_AREA)
    # 컬러(BGR) 영상을 그레이스케일 영상으로 변환
    # - Canny 연산 전에 단일 채널 영상 생성
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    # 가우시안 블러 적용
    # - 커널 크기 : 3×3
    # - 노이즈를 줄여 에지 검출 안정화
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    # Canny 에지 검출 수행
    # - 하위 임계값 : 80
    # - 상위 임계값 : 160
    edge = cv2.Canny(blur, 80, 160)
    # <<< TODO H05
    # 단일 채널 에지 영상을 BGR 3채널로 변환 후 반환
    # - VideoWriter가 컬러 프레임을 저장할 수 있도록 변환
    return cv2.cvtColor(edge,cv2.COLOR_GRAY2BGR)

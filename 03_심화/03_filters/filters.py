import cv2
import numpy as np

def apply_filter(gray, name):
    """한 장의 Gray에 선택 필터를 적용합니다. 파일 입출력은 하지 않습니다."""
    # 가우시안 블러 적용
    # - (5,5) 커널 사용
    # - sigma=0 : OpenCV가 자동 계산
    if name == "gaussian":
        return cv2.GaussianBlur(gray,(5,5),0)
    # 샤프닝 필터 적용
    # - 중심 픽셀을 강조하여 경계와 디테일 강화
    # - filter2D로 컨볼루션 수행
    if name == "sharpen":
        kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]],dtype=np.float32)
        return cv2.filter2D(gray,-1,kernel)
    # >>> TODO H03
    # 마지막 후보 bilateral을 d=7, sigmaColor=50, sigmaSpace=50으로 처리해 반환하세요. name은 정상 후보만 전달됩니다.
    # 양방향(Bilateral) 필터 적용
    # - d=7 : 주변 화소 탐색 크기
    # - sigmaColor=50 : 색상 유사도 범위
    # - sigmaSpace=50 : 공간 거리 영향 범위
    # - 에지는 유지하면서 노이즈를 제거
    return cv2.bilateralFilter(gray, 7, 50, 50)
    # <<< TODO H03

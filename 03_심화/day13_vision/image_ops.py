import cv2
import numpy as np

# 이미지 전처리 함수 정의
# - image : OpenCV로 읽은 원본 이미지(BGR 형식)
# - size : 축소할 이미지 크기(너비, 높이)
# - 반환값 : 각 이미지 처리 단계의 결과를 담은 딕셔너리
def prepare_image(image,size=(160,120)):
    """색공간·Resize·필터·형태학 처리의 중간 결과를 딕셔너리로 반환합니다."""
    # >>> TODO H07
    # Gray와 size=(너비,높이)로 축소한 small을 만드세요. 원본 image를 직접 수정하지 않습니다.

    # 원본 컬러 이미지를 Grayscale(흑백) 이미지로 변환
    # - cv2.COLOR_BGR2GRAY : BGR 3채널을 Grayscale 1채널로 변환
    # - image : 원본 이미지
    # - gray : 원본 크기를 유지한 흑백 이미지
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    # 흑백 이미지를 지정한 크기로 축소
    # - size=(160,120) : 너비 160픽셀, 높이 120픽셀
    # - cv2.resize() : 이미지 크기 변경
    # - small : 축소된 흑백 이미지
    small=cv2.resize(gray,size)
    # <<< TODO H07
    # Gaussian Blur를 이용한 이미지 노이즈 감소
    # - small : 축소된 흑백 이미지
    # - (3,3) : 3x3 크기의 Gaussian Kernel
    # - 0 : 표준편차를 자동 계산
    # - blur : 부드럽게 처리된 이미지
    blur=cv2.GaussianBlur(small,(3,3),0)
    # Threshold를 이용한 이진화 처리
    # - blur : Blur 처리된 이미지
    # - 127 : 임계값
    # - 255 : 임계값을 초과하는 픽셀에 적용할 값
    # - cv2.THRESH_BINARY : 임계값보다 크면 255, 작거나 같으면 0
    # - _ : 임계값 반환값은 사용하지 않음
    # - binary : 흑백 두 가지 값으로 구성된 이진 이미지
    _,binary=cv2.threshold(blur,127,255,cv2.THRESH_BINARY)
    # 형태학적 연산에 사용할 Kernel 생성
    # - cv2.MORPH_RECT : 사각형 형태의 Kernel
    # - (3,3) : Kernel 크기 3x3
    # - kernel : 형태학적 연산에 사용할 구조 요소
    kernel=cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    # Morphological Opening 처리
    # - binary : 입력 이진 이미지
    # - cv2.MORPH_OPEN : 침식(Erosion) 후 팽창(Dilation)
    # - kernel : 형태학적 연산에 사용할 구조 요소
    # - opened : 작은 흰색 노이즈가 제거된 이미지
    opened=cv2.morphologyEx(binary,cv2.MORPH_OPEN,kernel)
    # Canny Edge Detection을 이용한 윤곽선 검출
    # - blur : Blur 처리된 흑백 이미지
    # - 80 : 낮은 임계값
    # - 160 : 높은 임계값
    # - edge : 윤곽선이 흰색으로 표시된 1채널 이미지
    edge=cv2.Canny(blur,80,160)
    # 모든 처리 결과를 딕셔너리로 반환
    # - gray : 원본 크기의 흑백 이미지
    # - small : 축소 이미지
    # - blur : Gaussian Blur 이미지
    # - binary : 이진화 이미지
    # - opened : Opening 처리 이미지
    # - edge : Edge 검출 이미지
    return {"gray":gray,"small":small,"blur":blur,"binary":binary,"opened":opened,"edge":edge}

# 이미지 데이터 증강(Augmentation) 함수
# - image : 입력 이미지
# - 반환값 : 좌우 반전 및 밝기 증가가 적용된 이미지
def augment_image(image):
    """종합 실습에서는 설정을 고정해 재실행 비교를 쉽게 합니다."""
    # 이미지 좌우 반전
    # - cv2.flip(image,1) : 수평 방향으로 뒤집기
    # - flipped : 좌우 반전된 이미지
    flipped=cv2.flip(image,1)
    # 이미지 밝기 증가 및 픽셀 범위 제한
    # - astype(np.float32) : 계산을 위해 실수형으로 변환
    # - +15 : 각 픽셀의 밝기를 15만큼 증가
    # - np.clip(...,0,255) : 픽셀값을 0~255 범위로 제한
    # - astype(np.uint8) : 이미지 저장에 적합한 8비트 정수형으로 변환
    # - 반환값 : 좌우 반전 및 밝기 증가가 적용된 이미지
    return np.clip(flipped.astype(np.float32)+15,0,255).astype(np.uint8)

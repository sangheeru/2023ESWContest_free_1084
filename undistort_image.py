import cv2
import numpy as np

#켈리브레이션을 이용한 카메라 고유 파라미터
DIM=(1280, 960)
K=np.array([[366.4377565676265, 0.0, 629.2165918787352], [0.0, 366.01595951903425, 473.03276232842603], [0.0, 0.0, 1.0]])
D=np.array([[0.008919967682168696], [-0.021890199878023698], [0.012773718191265238], [-0.003032995995254996]])

balance=0
map1=None
map2=None

#렌즈로 인한 왜곡 보정
def undistorts(img):
    global map1, map2
    balance=1.0
    dim1 = img.shape[:2][::-1]  #dim1 is the dimension of input image to un-distort
    assert dim1[0]/dim1[1] == DIM[0]/DIM[1], "Image to undistort needs to have same aspect ratio as the ones used in calibration"
    scaled_K = K * dim1[0] / DIM[0]  # The values of K is to scale with image dimension.
    scaled_K[2][2] = 1.0  # Except that K[2][2] is always 1.0
    if map1 is None or map2 is None:
        new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K, D, dim1, np.eye(3), balance=balance)
        map1, map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K, D, np.eye(3), new_K, dim1, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img
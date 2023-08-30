import cv2
rear_cam = cv2.VideoCapture(0)
rear_cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # 가로
rear_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) # 세로
rear_cam.set(cv2.CAP_PROP_AUTO_EXPOSURE,3) # 자동노출
while True:
    front_ret, front_cap = rear_cam.read()
    cv2.imshow("s",front_cap)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        cv2.destroyAllWindows()
        break
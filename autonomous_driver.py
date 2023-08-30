import cv2
import numpy as np
import mediapipe as mp
import traceback
import threading
import speed_controller
from serial_arduino_connector import ArdComm
import running_info_display
import detectpose
import undistort_image

def weighted_img(img, initial_img, α=1, β=1., λ=0.): # 두 이미지 operlap 하기
    return cv2.addWeighted(initial_img, α, img, β, λ)

def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap): # 허프 변환
    lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)
    return lines

def map_value(value, in_min, in_max, out_min, out_max): # 입력 범위에서 출력 범위로의 선형 변환 수식을 적용
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def activate_trainer_robot():

    mp_pose = mp.solutions.pose
    # 비디오에 대한 포즈 기능 설정
    pose = mp_pose.Pose(model_complexity=1)
    angle_limit = [70,110]

    #카메라 불러오기
    front_cam = cv2.VideoCapture(0)
    front_cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # 가로
    front_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 960) # 세로
    front_cam.set(cv2.CAP_PROP_AUTO_EXPOSURE,3) # 자동노출
    
    rear_cam = cv2.VideoCapture(2)
    rear_cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # 가로
    rear_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) # 세로
    rear_cam.set(cv2.CAP_PROP_AUTO_EXPOSURE,3) # 자동노출
    
    ard_comm = ArdComm()
    ard_comm.joy_data = [512, 512, 0]
    while True:
        try:
            front_ret, front_cap = front_cam.read()
            rear_ret, rear_cap = rear_cam.read()

            runner_pose, landmarks = detectpose.get_landmarks(rear_cap, pose, display=False)
            if landmarks:
                detectpose.classify_pose(runner_pose,landmarks,display=False)

            info_display = running_info_display.update_info_display()


            #차선 검출을 위한 영상처리 흑백 -> 보정 -> 버드아이시점 변경 -> 블러 -> 테두리 검출 -> 선추출
            gray = cv2.cvtColor(front_cap, cv2.COLOR_BGR2GRAY)
            gray = undistort_image.undistorts(gray)
            pts1 = np.float32([[592, 400], [529, 487], [676, 400], [739, 487]]) # 좌표점은 좌상->좌하->우상->우하
            pts2 = np.float32([[0,0],[0,600],[300,0],[300,600]])
            M = cv2.getPerspectiveTransform(pts1, pts2)
            bird_eye_image = cv2.warpPerspective(gray, M, (300,600))
            blur = cv2.GaussianBlur(bird_eye_image, (5, 5), 0)
            canny = cv2.Canny(blur, 50, 100)
            lines = cv2.HoughLines(canny, 1, np.pi/180, 110)
            
            # Append the new lines to the new list
            # Convert the new lines to a NumPy array
            if lines is not None:
                new_lines = []  # Create a new list to store the new lines
                for line in lines:
                    rho, theta = line[0]
                    cos_theta = np.cos(theta)
                    sin_theta = np.sin(theta)
                    x0 = rho * cos_theta
                    y0 = rho * sin_theta
                    dx = 900 * -sin_theta
                    dy = 900 * cos_theta
                    x1 = int(x0 + dx)
                    y1 = int(y0 + dy)
                    x2 = int(x0 - dx)
                    y2 = int(y0 - dy)
                    new_lines.append([[x1, y1, x2, y2]])  
                lines = np.array(new_lines, dtype=np.int32)  
            bird_eye_image = cv2.cvtColor(bird_eye_image, cv2.COLOR_GRAY2BGR)

            x_intercept = []
            lines_slope =[]
            my_lines = []

            #과도하게 기울어진 직선 버리기

            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x1 == x2:
                    m = 0
                    angle = 90
                else:
                    m = (y2 - y1) / (x2 - x1)
                    angle = np.rad2deg(np.arctan(m))

                    if angle < 0:
                        angle += 180
                    cv2.line(bird_eye_image, (x1, y1), (x2, y2), (0,0,255), 2)
                if (angle_limit[0] <= angle <= angle_limit[1]):
                    cv2.line(bird_eye_image, (x1, y1), (x2, y2), (50,200,50), 2)
                    b = y1 -m * x1
                    if m == 0:
                        x_intercept.append(x1)
                    else:
                        x_intercept.append(int((300 - b)/m))
                    lines_slope.append(angle)
                    my_lines.append(line[0])

            #직선 절편을 이용하여 직선 식별

            sorted_x_intercept = sorted(x_intercept,reverse=True)
            rightmost_intercept = sorted_x_intercept[0]
            lane_intercept = []
            lane_intercept.append(rightmost_intercept)

            #직선간 일정거리이상만 차선으로 간주
            for i in sorted_x_intercept:
                if rightmost_intercept - i >10:
                    lane_intercept.append(i)
                rightmost_intercept = i

            #기존 차선의 기울기를 이용해 기울기 필터링값 결정

            closest_numbers = [0,0]
            for idx, x in enumerate(lane_intercept):
                if x <163:
                    closest_numbers[0] = x
                    closest_numbers[1] = lane_intercept[idx-1]
                    break
    
            m1 = lines_slope[x_intercept.index(closest_numbers[0])]
            m2 = lines_slope[x_intercept.index(closest_numbers[1])]
            prev_avg_slope = (m1+m2)//2

            angle_limit[0] = prev_avg_slope - 10
            angle_limit[1] = prev_avg_slope + 10
            target = (closest_numbers[0] + closest_numbers[1])//2

            # 입력 범위와 출력 범위 설정
            input_min = 63
            input_max = 263
            output_min = 1023
            output_max = 0

            BLEND_RATIO = 0.5  # 이전 값과 현재 값의 비율 설정 (0.0부터 1.0 사이)

            if 'prev_target' not in locals():
                prev_target = target

            # 현재 값과 이전 값의 비율로 타켓값을 산출
            blended_target = int(BLEND_RATIO * prev_target + (1 - BLEND_RATIO) * target)

            prev_target = blended_target

            # 입력값을 출력 범위로 변환
            steering_value = map_value(blended_target, input_min, input_max, output_min, output_max)

            #아두이노에게 줄 조향및 속도값 변경
            ard_comm.joy_data = [steering_value, speed_controller.robot_speed, 0]

            left_x1, left_y1, left_x2, left_y2 = my_lines[x_intercept.index(closest_numbers[0])]
            cv2.line(bird_eye_image, (left_x1, left_y1), (left_x2, left_y2), (0, 0, 255), thickness=3)

            right_x1, right_y1, right_x2, right_y2 = my_lines[x_intercept.index(closest_numbers[1])]
            cv2.line(bird_eye_image, (right_x1, right_y1), (right_x2, right_y2), (255, 0, 0), thickness=3)
            
            cv2.circle(bird_eye_image,(blended_target,300), 5, (255, 25, 255), -1)
            
            cv2.imshow("running_info_display", info_display)
            cv2.imshow("s",rear_cap)
            # cv2.imshow('undistort',gray)
            # # cv2.imshow('canny_img',canny)
            # cv2.imshow('bird_eye_image',bird_eye_image)
            # # cv2.imshow('undistort',gray)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                cv2.destroyAllWindows()
                break
        except Exception as e:
            print(traceback.format_exc())         
    # front_cam.release()
    rear_cam.release()
    

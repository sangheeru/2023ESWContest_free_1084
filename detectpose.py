import mediapipe as mp
import math
import user_settings
mp_pose = mp.solutions.pose

height, width = [0, 0]
speed = 0.0

# 랜드마크 각도 계산 함수
def calculateAngle(landmark1, landmark2, landmark3):
    # 세 점을 이용해 두 개의 선 사이 각도 계산 좌표가 튜플 형태로 전달
    x1, y1, _ = landmark1
    x2, y2, _ = landmark2
    x3, y3, _ = landmark3

    # 세 랜드마크 사이의 각도 계산식
    # (두 번째 랜드마크와 세 번째 랜드마크 사이의 각도)-(첫 번째 랜드마크외 두 번째 랜드마크 사이의 각도)
    # 두 각도의 차이 계산 및 360도 내에 들어오도록 보정 후 라디안을 도 단위로 변환
    angle = math.degrees((math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))%(2*math.pi))
    
    return angle

# 랜드마크 저장 및 그리기
def get_landmarks(image, pose, display=False):
    global height, width
    runner_pose = pose.process(image)   # 이미지에서 자세 추출 실행
    height, width, _ = image.shape      # 이미지의 크기 정보 저장
    landmarks = []                      # 랜드마크 좌표를 저장할 리스트 초기화

    # landmark가 감지 되었는지 확인
    if runner_pose.pose_landmarks:
        # landmark 그리기
        mp.solutions.drawing_utils.draw_landmarks(
            image, runner_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    
    # 각 랜드마크의 좌표와 깊이 정보를 리스트에 저장
    for landmark in runner_pose.pose_landmarks.landmark:
        landmarks.append((int(landmark.x * width), int(landmark.y * height), (landmark.z * width)))
    
    if not display:
        return runner_pose, landmarks

# 포즈 분류 함수
def classify_pose(runner_pose, landmarks, display=False):
    global estimated_distance
    global posture_command
    global incorrect_running_pose

    posture_command = ""
    incorrect_running_pose = ""
    focal_langth = 1099
    person_height = 0.9

    # 포즈 분류에 필요한 랜드마크 좌표 추출
    right_shoulder_x = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x 
    right_shoulder_y = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
    right_knee_x = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE].x
    right_knee_y = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE].y
    left_shoulder_x = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x 
    left_shoulder_y = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y 
    left_knee_x = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].x 
    left_knee_y = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].y 
    right_hand_x = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].x
    right_hand_y = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y 
    left_hand_x = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].x
    left_hand_y = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].y
    right_ankle_y = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE].y
    left_ankle_y = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].y
    left_hip_x = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].x
    left_hip_y = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y
    right_hip_x = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].x
    right_hip_y = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].y
    right_mouth_y = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.MOUTH_RIGHT].y
    right_foot_x = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HEEL].x
    left_foot_x = runner_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HEEL].x

    #----------------------------------------------------------------------------------------------------------------
    # 포즈 판단을 위한 변수 계산
    left_shoulder_knee_distance = abs((left_shoulder_x * height - left_knee_x* width)+ (left_shoulder_y* height - left_knee_y* height))    # 어깨 좌표에서 무릎 빼기 (픽셀 단위로!)
    right_shoulder_knee_distance = abs((right_shoulder_x * width - right_knee_x* width) + (right_shoulder_y * height- right_knee_y* height))
    shoulder_knee_distance = (left_shoulder_knee_distance + right_shoulder_knee_distance) / 2
    foot_avg_y = ( left_ankle_y + right_ankle_y)/2
    shoulder_avg_x = (left_shoulder_x+right_shoulder_x)/2
    left_hand = shoulder_avg_x - left_hand_x
    right_hand = shoulder_avg_x - right_hand_x

    #----------------------------------------------------------------------------------------------------------------
    # 로봇과 사용자와의 거리 계산
    person_height = int(user_settings.user_height)*0.00517  #어깨부터 무릎 비율로 뽑아내기  0.00517 
    estimated_distance = (focal_langth / shoulder_knee_distance)*person_height

    #----------------------------------------------------------------------------------------------------------------
    #각도 계산
    #왼쪽 어깨-팔꿈치-손목 landmark angle 값 계산 - left elbow 
    left_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                      landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
                                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value])
    #오른쪽 어깨-팔꿈치_손목 landmark angle 값 계산 - right elbow
    right_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                       landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
                                       landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value])   
    #왼쪽 팔꿈치-어깨-골반 landmark angle 값 계산 - left shoulder
    left_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
                                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value])
    #오른쪽 팔꿈치-어깨-골반 landmark angle 값 계산 - right shoulder
    right_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
                                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                          landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value])      
    
    
    # 정지(양팔)
    # 왼쪽/오른쪽 elbow각도 90~195 사이에 위치하는지 확인
    if left_elbow_angle > 130 and left_elbow_angle < 195 and right_elbow_angle > 130 and right_elbow_angle < 195:
        #
        if left_shoulder_angle > 190 and left_shoulder_angle < 300 and right_shoulder_angle > 120 and right_shoulder_angle < 180:
            posture_command = "STOP"
  
    # 시작(양팔 T포즈) 
    # 왼쪽/오른쪽 elbow 각도가 165~195(기준 180) 사이에 위치하는지 확인
    if left_elbow_angle > 165 and left_elbow_angle < 195 and right_elbow_angle > 165 and right_elbow_angle < 195:
        # 왼쪽 shoulder 각도가 260~300(기준 270) 사이, 오른쪽 shoulder 각도가 80~110(기준 90) 사이에 위치하는지 확인
        if left_shoulder_angle > 260 and left_shoulder_angle < 300 and right_shoulder_angle > 80 and right_shoulder_angle < 110:
            posture_command = "START"

    # 속도 down(오른팔)
    # 오른쪽 elbow 각도가 255~320(기준 270) 사이, 오른쪽 shoulder의 각도가 70~110(기준 90) 사이, 왼쪽 shoulder 각도가 300 이상
    if right_elbow_angle > 255 and right_elbow_angle < 320 and right_shoulder_angle > 70 and right_shoulder_angle < 110 and left_shoulder_angle > 300 :
        posture_command = "Decelerate"
        # speed_controller.speed_up()

    # 속도 up(왼팔)
    # 왼쪽 elbow 각도가 60~110(기준 90) 사이, 왼쪽 shoulder의 각도가 270~330(기준 270) 사이, 오른쪽 shoulder 각도가 60 이하
    if left_elbow_angle > 60 and left_elbow_angle < 110 and left_shoulder_angle > 270 and left_shoulder_angle < 330 and right_shoulder_angle <60 :
        posture_command = "Accelerate"

    # 손목 상하 교정
    # 왼/오 손목의 y 픽셀 값이 왼/오 어깨의 y픽셀 값보다 작고, 왼/오 손목과 왼/오 어깨의 x픽셀 값 차의 절댓값이 40이하이고, 오른쪽 입과 왼/오 손목의 y픽셀 값 차의 절댓값이 100이하
    if (right_hand_y * height < right_shoulder_y * height) and (abs(right_hand_x * width - right_shoulder_x * width) < 40) and (abs(right_mouth_y * height-right_hand_y * height) < 100):
        incorrect_running_pose = "Hands Down"
    if (left_hand_y * height < left_shoulder_y * height) and (abs(left_hand_x * width-left_shoulder_x * width) < 40) and (abs(right_mouth_y * height-left_hand_y * height) < 100):
        incorrect_running_pose = "Hands Down"
    # 넘어짐 교정
    # 오른쪽 입과 왼/오 무릎의 y픽셀 값 차의 절댓값이 220이하
    if abs(right_mouth_y * height - left_knee_y * height) < 180 or abs(right_mouth_y * height - right_knee_y * height) < 180:
        incorrect_running_pose = "Fall"
    # 무릎 교정
    # 왼/오 어깨와 왼/오 무릎의 y픽셀 값 차의 절댓값이 60이하
    if (abs(left_shoulder_x * width - left_knee_x * width) > 60) or (abs(right_shoulder_x * width - right_knee_x * width)>60):
        incorrect_running_pose = "Close Knees"
    # 팔 좌우 교정 (좌표)
    # 양 발의 평균과 왼/오 손목의 y좌표 값의 차가 0.01이상
    if (foot_avg_y - left_hand_y >= 0.01 and foot_avg_y - right_hand_y >= 0.01) and left_hand * right_hand > 0:
        incorrect_running_pose = "Align Hands"
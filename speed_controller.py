import time
import threading

robot_speed = 512
speed_lock = threading.Lock()

# 시작 속도 증가
def start():
    global robot_speed 
    time.sleep(3)               # 3초 대기
    while robot_speed < 800:    # 로봇 속도가 800보다 작은 동안 게속 실행
        with speed_lock:
            robot_speed += 10   # 로봇 속도를 10씩 증가
            time.sleep(0.03)    # 0.03초 동안 대기

# 속도 감소 후 정지
def stop():
    global robot_speed
    while robot_speed > 512:       # 로봇 속도가 512보다 큰 동안 계속 실행
        with speed_lock:
            robot_speed -= 10      # 로봇 속도 10씩 감소
            if robot_speed < 512:  # 로봇 속도가 512보다 작아졌을 경우, 최소 속도인 512로 설정
                robot_speed = 512
            time.sleep(0.03)       # 0.03초 동안 대기

# 가속
def accelerate():
    global robot_speed
    for i in range(100):            # 0부터 99까지의 범위를 반복
        with speed_lock:
            if robot_speed < 1023:  # 로봇 속도가 1023보다 작을 경우에만 실행
                robot_speed += 1    # 로봇 속도를 1씩 증가시킴
                time.sleep(0.03)    # 0.03초 동안 대기

# 감속
def decelerate():
    global robot_speed
    for i in range(100):            # 0부터 99까지의 범위를 반복
        with speed_lock:
            if robot_speed > 512:   # 로봇 속도가 512보다 클 경우에만 실행
                robot_speed -= 1    # 로봇 속도를 1씩 감소시킴
                time.sleep(0.03)    # 0.03초 동안 대기

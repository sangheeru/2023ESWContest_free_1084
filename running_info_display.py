import cv2
import time
import numpy as np
import detectpose
import speed_controller
import threading
import coach_audio_player


command_start_time = time.time()
pose_start_time = time.time()
timer_start_time = time.time()

seconds = 0

voice  = ""

width = 1200
height = 750

#사용자 로봇간의 안정거리 설정

stable_range_start = 1.0
stable_range_end = 3.0

timer_running = False

prev_command = ""
prev_pose = ""
speed_increasing = False


def start_timer():
    global timer_start_time
    global timer_running
    timer_start_time = time.time()
    timer_running = True

def stop_timer():
    global timer_running
    timer_running = False

def update_info_display():
    global command_start_time
    global pose_start_time

    global timer_start_time
    global seconds
    global timer_running

    global prev_command
    global prev_pose
    global increase_speed_thread

    global voice
    voice  = ""
    if timer_running and timer_start_time + 1 < time.time():
        seconds += 1
        timer_start_time = time.time()

    distance = detectpose.estimated_distance
    command = detectpose.posture_command
    pose = detectpose.incorrect_running_pose
    info_display = np.zeros((height, width, 3), dtype=np.uint8)

    #사용자 포즈 추정으로 부터 얻은 특정 동작에 따른 기능수행

    if command == "STOP":
        increase_speed_thread = threading.Thread(target=speed_controller.stop)
        increase_speed_thread.start()
        stop_timer()
        prev_command = command
        voice = "STOP"

    #일정시간동안 특정 동작을 유지 또는 해제하야여 디스플레이에 표현

    if (command != "" and command_start_time + 3 < time.time()):
        if command == "Accelerate":
            speed_thread = threading.Thread(target=speed_controller.accelerate)
            speed_thread.start()
            voice =  "Accelerate"


        elif command == "Decelerate":
            speed_thread = threading.Thread(target=speed_controller.decelerate)
            speed_thread.start()
            voice =  "Decelerate"


        elif command == "START":
            speed_thread = threading.Thread(target=speed_controller.start)
            speed_thread.start()
            voice =  "START"
            start_timer()

        prev_command = command
        command_start_time = time.time()
    
    if (command == "" and command_start_time + 5 < time.time()):
        prev_command = ""
        command_start_time = time.time()
    
    if (pose != "" and pose_start_time + 2 < time.time()):
        prev_pose = pose
        pose_start_time = time.time()
    
    if (pose == "" and pose_start_time + 3 < time.time()):
        prev_pose = ""
        pose_start_time = time.time()

    if prev_pose == "Fall":
        speed_thread = threading.Thread(target=speed_controller.stop)
        speed_thread.start()
        voice = "Fall"

    if prev_command != "":
        if prev_command == "Accelerate" or prev_command == "Decelerate":
            cv2.putText(info_display, prev_command, (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 8)
        else:
            cv2.putText(info_display, prev_command, (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 255), 15)
    else:
        cv2.putText(info_display, prev_pose, (60, 150), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 8)
        voice = prev_pose
    #속도와 거리 출력
    mapped_speed = (speed_controller.robot_speed - 512) * 15 / 511
    cv2.putText(info_display, f"{mapped_speed:.1f}", (125, 650), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 255, 255), 15)
    cv2.putText(info_display, f"{distance:.1f}", (680, 650), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 255, 255), 15)
    
    # 분과 초 계산
    minutes, remaining_seconds = divmod(seconds, 60)
    
    # 분:초 형식으로 표시
    timer_text = f"{minutes:02d}:{remaining_seconds:02d}"

    cv2.putText(info_display, timer_text, (230, 450), cv2.FONT_HERSHEY_SIMPLEX, 8, (255, 255, 255), 30)
    #사용자와의 거리에 따른 출력값
    if distance < stable_range_start :
        cv2.putText(info_display, "Close", (700, 150), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 15)
        voice = "Close"
    elif distance > stable_range_end :
        cv2.putText(info_display, "Far", (700, 150), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 15)
        speed_controller.stop()
        voice = "Far"
    else :
        cv2.putText(info_display, "Stable", (700, 150), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 15)
    
    #코칭 음성재생
    play_sound = threading.Thread(target=coach_audio_player.play_sound)
    play_sound.start()

    cv2.putText(info_display, "m", (1000, 650), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    cv2.putText(info_display, "km/h", (400, 650), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    
    return info_display
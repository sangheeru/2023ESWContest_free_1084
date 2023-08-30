import threading
import pygame
import running_info_display

sound_lock = threading.Lock()
def play_sound():
    global sound_lock
    if running_info_display.voice != "":
        if sound_lock.acquire(blocking=False):  # Lock 획득 시도 (non-blocking)
            try:
                pygame.init()
                mp3_file = "CoachVoice/" + running_info_display.voice + ".mp3"  # 실제 파일 경로로 변경해야 합니다.
                print(running_info_display.voice)
                # mp3 파일 재생
                pygame.mixer.music.load(mp3_file)
                pygame.mixer.music.play()

                # 재생이 끝날 때까지 대기
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            finally:
                pygame.quit()
                sound_lock.release()  # Lock 해제

import serial
import struct
import threading

# 아두이노에게 시리얼 통신을 통해 조향 및 속도값 전송을 수행하는 클래스
class ArdComm:
    joy_data = [512, 512, 0]  # 서보모터 및 DC모터 제어변수 초기화
    def __init__(self):
        self.ard_port = '/dev/ttyACM0'  # 아두이노 시리얼 포트 경로
        self.baud = 57600  # 통신 속도 (보드레이트)
        self.rcv_period = 0.02  # 수신 주기
        self.rcv_struct_format = '3si'  # 수신할 데이터의 패킹 형식
        self.rcv_struct_size = struct.calcsize(self.rcv_struct_format)  # 수신할 데이터의 패킹 크기
        self.btn = 0  # 버튼 상태

        self.snd_period = 0.02  # 송신 주기
        self.snd_struct_format = '3s3i'  # 송신할 데이터의 패킹 형식
        self.snd_struct_size = struct.calcsize(self.snd_struct_format)  # 송신할 데이터의 패킹 크기
        self.ser = serial.Serial(self.ard_port, self.baud, timeout=1)  # 시리얼 통신 인스턴스 생성

        self.snd_header = b'JOY'  # 송신 데이터 헤더
        
        self.send_joy()  # 서보모터 및 DC모터 데이터 송신 함수 호출
        self.rcv_ard()  # 아두이노 데이터 수신 함수 호출

    # 서보모터 및 DC모터 데이터를 아두이노로 송신하는 함수
    def send_joy(self):
        if self.btn != 1:
            send_data = struct.pack(self.snd_struct_format, self.snd_header, *self.joy_data)
            self.ser.write(send_data)
        threading.Timer(self.snd_period, self.send_joy).start()

    # 아두이노에서 데이터를 수신하는 함수
    def rcv_ard(self):        
        if self.ser.readable():
            buffer = self.ser.read_all()
            len_buffer = len(buffer)
            if len_buffer >= self.rcv_struct_size:
                strt_idx = -1
                for idx in range(len_buffer - self.rcv_struct_size + 1):
                    if buffer[idx] == ord('A') and buffer[idx+1] == ord('R') and buffer[idx+2] == ord('D'):
                        strt_idx = idx
                        break
                if strt_idx == -1:
                    print('Fail detecting Arduino msg {}'.format(buffer[idx]))
                else:
                    rcv_struct = buffer[strt_idx:strt_idx + self.rcv_struct_size]
                    try:
                        rcv_data = struct.unpack(self.rcv_struct_format, rcv_struct)
                        self.btn = rcv_data[-1]
                        # print('Btn {}'.format(self.btn))
                    except:
                        print('Corrupted!')
            
        threading.Timer(self.rcv_period, self.rcv_ard).start()

# 메인 함수
def main(args=None):
    ardComm = ArdComm()  # 아두이노 통신 클래스 인스턴스 생성
    while True:
        pass  # 계속해서 프로그램 실행

# 스크립트 진입점
if __name__ == '__main__':
    main()  # 메인 함수 호출

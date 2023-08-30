// Pin connection
// Pin 0 of Arduino nano 33 iot <-> DOUT of Zigbee socket
// Pin 1 of Arduino nano 33 iot <-> DIN of Zigbee socket

// 시리얼 통신 속도 (보드레이트)
const long baud = 57600;

// Servo 라이브러리를 사용하여 DC 모터와 서보 모터를 제어하는 객체 생성
#include <Servo.h>
Servo DC;
Servo SV;
// 모터의 핀 번호
int dc = 9;
int sv = 10;
int st = 1500;  // 서보 모터 각도
int sp = 1500;  // DC 모터 속도
int prev_x = 0;
int prev_y = 0;
int cnt = 0;
int mode = 0;   // 로봇 제어 모드
int led_pin[2] = {4, 13};  // LED 핀 번호
// 조이스틱 데이터의 유니온 (다양한 데이터 형식을 함께 사용)
union JoyUnion {
  struct {
    char header[3];  // 헤더
    int axis[2];      // 조이스틱 좌표
    int btn;          // 버튼 상태
  } joy_data;
  char buffer[sizeof(joy_data)];  // 버퍼
};

// 아두이노 데이터 구조체
struct ArdData {
  char header[3];  // 헤더
  int btn;         // 버튼 상태
} ard_data;
unsigned int ard_data_size = sizeof(ArdData);  // 아두이노 데이터 크기

// 조이스틱 데이터의 유니온 배열
union JoyUnion joy_union[3];  // 0: zigbee, 1: xavier, 2: selected
unsigned int joy_struct_size_m1 = sizeof(JoyUnion) - 1;  // 조이스틱 데이터 크기 - 1

bool toggle_led[2] = {true, true};  // LED 상태 토글 배열
bool rcv_strt[2] = {false, false};   // 데이터 수신 시작 여부 배열
bool rcv_success[2] = {false, false};  // 데이터 수신 성공 여부 배열
int data_cnt[2] = {0 ,0};  // 데이터 카운터 배열
int mode_id = 1;  // 0: zigbee, 1: xavier (로봇 제어 모드)
int joyon = 0;
unsigned long start_time = 0;
int Tms = 20;  // 주기적인 통신 주기

void setup() {
  Serial1.begin(baud);  // 시리얼 통신 시작
  Serial.begin(baud);
  for (int i = 0; i < 2; i++) {
    pinMode(led_pin[i], OUTPUT);  // LED 핀을 출력으로 설정
    digitalWrite(led_pin[i], toggle_led[i]);  // LED 초기 상태 설정
  }
  DC.attach(dc);  // DC 모터 서보 객체에 연결
  SV.attach(sv);  // 서보 모터 서보 객체에 연결
  pinMode(5, OUTPUT);
  digitalWrite(5, HIGH);

  // 아두이노 데이터 초기화
  ard_data.header[0] = 'A';
  ard_data.header[1] = 'R';
  ard_data.header[2] = 'D';
  ard_data.btn = 0;
}

void loop() {
  zigXavComm();  // zigbee와 xavier 간의 통신 함수 호출
  digitalWrite(5, mode_id);  // 디지털 핀의 출력 설정

  // 주기적으로 아두이노 데이터 전송
  if (millis() - start_time > Tms) {
    if (ard_data.btn != 0) {
      Serial.write((byte*)&ard_data, ard_data_size);
    }
    start_time = millis();
  }

  // 조이스틱 값을 읽어 모터 제어
  if (joy_union[mode_id].joy_data.axis[1] == prev_x &&  joy_union[mode_id].joy_data.axis[0] == prev_y) {
    cnt++;
  } else {
    cnt = 0;
  }

  // 로봇 제어 모드에 따라 속도 및 각도 값 설정
  if (mode == 3) {
    sp = map(joy_union[mode_id].joy_data.axis[1], 0, 1023, 1300, 1700);
    if (sp <= 1400) {
      sp = 1400 - (1400 - sp) * 5;
    }
  } else if (mode == 0) {
    sp = map(joy_union[mode_id].joy_data.axis[1], 0, 1023, 1450, 1550);
  } else if (mode == 1) {
    sp = map(joy_union[mode_id].joy_data.axis[1], 0, 1023, 1425, 1575);
  } else if (mode == 2) {
    sp = map(joy_union[mode_id].joy_data.axis[1], 0, 1023, 1400, 1600);
  }
  st = map(joy_union[mode_id].joy_data.axis[0], 0, 1023, 1200, 1800);
  DC.writeMicroseconds(sp);
  SV.writeMicroseconds(st);
}
// zigbee와 xavier 간의 통신을 처리하는 함수
void zigXavComm() {
  for (int i = 0; i < 2; i++) {
    char c = '\0';  // 수신된 문자
    bool rcv_c = false;  // 문자를 수신했는지 여부
    if (i == 0 && Serial1.available()) {
      c = Serial1.read();  // Zigbee 모듈로부터 문자 수신
      rcv_c = true;
    } else if (i == 1 && Serial.available()) {
      c = Serial.read();  // Xavier로부터 문자 수신
      rcv_c = true;
    }
    if (!rcv_c) {
      continue;  // 문자를 수신하지 않은 경우 다음 반복으로 이동
    }    
    // 데이터 수신을 시작하는 지점 식별 ('J', 'O', 'Y' 순서로 수신됨)
    if (c == 'J' && rcv_strt[i] == false) {
      rcv_strt[i] = true;
      joy_union[i].buffer[data_cnt[i]] = c;
      data_cnt[i] = 1;    
    } else if (c == 'O' && data_cnt[i] == 1) {
      joy_union[i].buffer[data_cnt[i]] = c;
      data_cnt[i]++;      
    } else if (c == 'Y' && data_cnt[i] == 2) {
      joy_union[i].buffer[data_cnt[i]] = c;
      data_cnt[i]++;      
    } else {
      // 데이터 수신 중
      if (rcv_strt[i] && data_cnt[i] > 2) {
        joy_union[i].buffer[data_cnt[i]] = c;
        data_cnt[i]++;
        // 조이스틱 데이터 수신 완료
        if (data_cnt[i] == joy_struct_size_m1) {
          toggle_led[i] = !toggle_led[i];
          // 수신된 데이터를 joy_union[i].joy_data에 복사
          memcpy(&joy_union[i].joy_data, joy_union[i].buffer, sizeof(joy_union[i].joy_data));
          rcv_strt[i] = false;        
          data_cnt[i] = 0;
          
          // 아두이노 데이터 업데이트 및 로봇 제어 모드 설정
          if (i == 0) {
            ard_data.btn = joy_union[i].joy_data.btn;
            if (joy_union[i].joy_data.btn == 1) {
              // 수동 모드 선택 시
              mode_id = 0;
              break;
            } else if (joy_union[i].joy_data.btn == 2) {
              mode = 0;  // 모드 0
            } else if (joy_union[i].joy_data.btn == 3) {
              mode = 1;  // 모드 1
            } else if (joy_union[i].joy_data.btn == 4) {
              mode = 2;  // 모드 2
            } else if (joy_union[i].joy_data.btn == 5) {
              mode = 3;  // 모드 3
            } else if (joy_union[i].joy_data.btn == 8) {
              mode_id = 1;  // Xavier 제어 모드
            }
          }
        }
      } else {
        rcv_strt[i] = false;        
        data_cnt[i] = 0;        
      }      
    }
    digitalWrite(led_pin[i], toggle_led[i]);
    joy_union[2] = joy_union[mode_id];
  }  
}

from tkinter import*

user_height=170
user_weight=70
# 사용자의 height 변경 및 저장
def set_height(value):
    global user_height
    # value 값에 따라 사용자의 키를 증가 또는 감소시킴
    if value==1:
        user_height-=1
    elif value==2:
        user_height+=1
    
    # 변경된 사용자의 키를 문자열로 만들어 라벨에 표시
    height_string = f"{user_height}cm"
    set_height_label.config(text=height_string)

    # 변경된 사용자의 키 값을 반환
    return user_height
    
# 사용자의 weight 변경 및 저장
def set_weight(value):
    global user_weight
    # value 값에 따라 사용자의 몸무게를 증가 또는 감소시킴
    if value==1:
        user_weight-=1
    elif value==2:
        user_weight+=1
        
    # 변경된 사용자의 몸무게를 문자열로 만들어 라벨에 표시
    weight_string = f"{user_weight}kg"
    set_weight_label.config(text=weight_string)
    
    # 변경된 사용자의 몸무게 값을 반환
    return user_weight

# 사용자 정보 변경 메인 함수
def set_user_data():
    global user_data
    global user_height
    global user_weight
    global set_height_label
    global set_weight_label
    user_data=Toplevel()
    user_data.title("사용자 정보 설정")
    user_data.geometry("1200x750")
    user_data.configure(bg="black")
    
    main_label=Label(user_data,text="\nUser Settings",font=("맑은 고딕",30,"bold"),bg="black",fg="white")
    main_label.pack()
    
    height_label=Label(user_data,text="Height",font=("맑은 고딕",90,"bold"),bg="black",fg="white")
    height_label.place(x=30,y=180)
    set_height_label=Label(user_data,text=f"{user_height}cm",font=("맑은 고딕",90,"bold"),bg="black",fg="white")
    set_height_label.place(x=650,y=180)
    set_height_btn_m=Button(user_data,text="<",font=("맑은 고딕",30,"bold"),bg="white",fg="black",width=4,height=2,command=lambda:set_height(1))
    set_height_btn_m.place(x=510,y=200)
    set_height_btn_p=Button(user_data,text=">",font=("맑은 고딕",30,"bold"),bg="white",fg="black",width=4,height=2,command=lambda:set_height(2))
    set_height_btn_p.place(x=1050,y=200)
    
    weight_label=Label(user_data,text="Weight",font=("맑은 고딕",90,"bold"),bg="black",fg="white")
    weight_label.place(x=30,y=480)
    set_weight_label=Label(user_data,text=f"{user_weight}kg",font=("맑은 고딕",90,"bold"),bg="black",fg="white")
    set_weight_label.place(x=650,y=480)
    set_weight_btn_m=Button(user_data,text="<",font=("맑은 고딕",30,"bold"),bg="white",fg="black",width=4,height=2,command=lambda:set_weight(1))
    set_weight_btn_m.place(x=510,y=500)
    set_weight_btn_p=Button(user_data,text=">",font=("맑은 고딕",30,"bold"),bg="white",fg="black",width=4,height=2,command=lambda:set_weight(2))
    set_weight_btn_p.place(x=1050,y=500)
    
    # 사용자 정보 변경 종료
    def exit():
        user_data.destroy()
    
    exit_btn=Button(user_data,text="Exit",font=("맑은 고딕",20,"bold"),width=10,height=4,bg="pink",fg="black",command=exit)
    exit_btn.place(x=1025,y=0)
    
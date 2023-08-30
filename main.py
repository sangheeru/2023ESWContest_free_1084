from tkinter import*
import autonomous_driver
import user_settings

root=Tk()
root.title("트레이닝봇")
root.geometry('1200x750')
root.configure(bg="black")

#------------------------------------------------------------   
def close():                #전체종료
        root.destroy()
label_text = Label(root, text="\nRunner Training Robot", font=("맑은 고딕",40,"bold"),bg="black",fg="white")
label_text.pack(side="top")

Running_mode = Button(root,width=20,height=7, text="Start Run",font=("맑은 고딕",20,"bold"),bg="white",fg="black",overrelief="groove")
Running_mode.place(x=200,y=250)
Running_mode.config(command = autonomous_driver.activate_trainer_robot)

User_mode = Button(root,width=20,height=7, text="User Settings",font=("맑은 고딕",20,"bold"),bg="white",fg="black",overrelief="groove")
User_mode.place(x=650,y=250)
User_mode.config(command = user_settings.set_user_data)

btn_close=Button(overrelief="solid",text = "Close", font=("맑은 고딕",20,"bold"), width=10,height=4,bg="pink",fg="black")    #종료 버튼
btn_close.config(command = close)
btn_close.place(x = 1025,y = 0)
#-------------------------------------------------------------
if __name__ == '__main__':
        root.mainloop()
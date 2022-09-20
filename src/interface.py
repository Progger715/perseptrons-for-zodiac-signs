from tkinter import *
from PIL import Image, EpsImagePlugin
from tkinter.ttk import Combobox
from tkinter import scrolledtext



canvas_width = 256
canvas_height = 256
brush_size = 3
color = "black"

def paint(event):
    global brush_size
    global color
    x1 = event.x - brush_size
    x2 = event.x + brush_size
    y1 = event.y - brush_size
    y2 = event.y + brush_size
    w.create_oval(x1, y1, x2, y2, fill=color, outline=color)


def delete():
    w.delete("all")
    res.delete(1.0, END)

def save():
    #x = root.winfo_rootx() + w.winfo_x()
    # y = root.winfo_rooty() + w.winfo_y()
    # x1 = x + w.winfo_width()
    # y1 = y + w.winfo_height()
    # ImageGrab.grab().crop((x,y,x1,y1)).save("Image.png")
    w.postscript(file="Image.ps", colormode="color")
    # надо изменить путь
    EpsImagePlugin.gs_windows_binary = r'C:\Program Files\gs\gs9.56.1\bin\gswin64c'
    img = Image.open("Image.ps")
    img.save("tmp.png", "png")
    img = img.resize((32, 32), Image.Resampling.LANCZOS)
    img.save("Image.png", "png")




def get_result():
    save()
    res.delete(1.0, END)
    res.insert(INSERT, "Здесь будет ответ")


def select():
    new_window = Toplevel()
    new_window.geometry("310x150")
    new_window.resizable(False, False)
    Label(new_window, text="Выберите, какой знак зодиака был Вами нарисован: \n").pack()
    combo = Combobox(new_window)
    combo['values'] = ("Овен", "Телец", "Близнецы","Рак","Лев","Дева","Весы","Скорпион","Стрелец","Козерог","Водолей","Рыбы", )
    combo.current(1)
    combo.pack(pady=20)
    def get_combobox():
        print(str(combo.get()))
        new_window.destroy()
    Button(new_window, text="Выбрать", command=get_combobox).pack()
    save()



root = Tk()
root.title("Лаба1")
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
width = width // 2
height = height // 2
width = width - 200
height = height - 200
root.geometry('400x500+{}+{}'.format(width, height))
root.resizable(False, False)

w = Canvas(width=canvas_width, height=canvas_height, bg="white")
w.bind("<B1-Motion>", paint)
w.pack()


delete_btn = Button(text="Очистить", width=10, command=delete)
delete_btn.pack(side=BOTTOM, pady=10)

learning_btn = Button(root, text="Выбрать и обучить", width=30, command=select)
learning_btn.pack(side=BOTTOM, pady=10)

save_btn = Button(text="Распознать", width=10, command=get_result)
save_btn.pack(side=BOTTOM, pady=10)

res = scrolledtext.ScrolledText(root, width=30, height=2)
res.pack(side=BOTTOM, pady=10)


root.mainloop()
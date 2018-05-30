import tkinter

top = tkinter.Tk()
top.title("Web Monitor and Warning Sender")

frame1 = tkinter.Frame(top)
label_u = tkinter.Label(frame1, text="URL = ", width='20')
label_u.pack(side=tkinter.LEFT)
entry_url = tkinter.Entry(frame1, width='40')
entry_url.pack(side=tkinter.RIGHT)

frame2 = tkinter.Frame(top)
label_m = tkinter.Label(frame2, text="Keyword = ", width='20')
label_m.pack(side=tkinter.LEFT)
entry_key = tkinter.Entry(frame2, width='40')
entry_key.pack(side=tkinter.RIGHT)

frame3 = tkinter.Frame(top)
label_d = tkinter.Label(frame3, text="Depth = ", width='20')
label_d.pack(side=tkinter.LEFT)
entry_dep = tkinter.Entry(frame3, width='40')
entry_dep.pack(side=tkinter.RIGHT)

frame4 = tkinter.Frame(top)
label_e = tkinter.Label(frame4, text="Email = ", width='20')
label_e.pack(side=tkinter.LEFT)
entry_eml = tkinter.Entry(frame4, width='40')
entry_eml.pack(side=tkinter.RIGHT)

label_top = tkinter.Label(top)
label_sep = tkinter.Label(top)
label_bot = tkinter.Label(top)

def main():
    print("start.....")

frame5 = tkinter.Frame(top)
btn = tkinter.Button(frame5, text="Start Monitor", command=main)
btn.pack(side=tkinter.BOTTOM)

label_top.pack()
frame1.pack()
frame2.pack()
frame3.pack()
frame4.pack()
label_sep.pack()
frame5.pack()
label_bot.pack()
top.mainloop()

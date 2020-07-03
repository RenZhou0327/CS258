import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from HuffmanKernel import MyHuffman
from LzssKernel import MyLzss
import os

top = tk.Tk()
top.minsize(500, 100)
top.title("Naive的数据压缩")
top.iconbitmap('Frog.ico')


def choose_file():
    file_path = filedialog.askopenfilename()
    path.set(file_path)


def encode():
    file_path = entry.get()
    if os.path.isfile(file_path):
        print(True)
    else:
        print(False)
        messagebox.showinfo(title='错误', message="当前文件不存在，请选择正确的文件")
        return

    var = select.get()
    result_path = ""
    result = True
    if var == 1:
        print("哈夫曼压缩")
        try:
            myhuffman = MyHuffman(file_path)
            result_path = myhuffman.do_encoding()
        except Exception as e:
            result = False
            messagebox.showinfo(title='压缩错误', message=e)
    else:
        print("lzss压缩")
        try:
            mylzss = MyLzss(file_path)
            result_path = mylzss.do_encoding()
        except Exception as e:
            result = False
            messagebox.showinfo(title='压缩错误', message=e)
    if result:
        messagebox.showinfo(title='提示', message='压缩成功！\n新文件路径为' + result_path)


def decode():
    file_path = entry.get()
    if os.path.isfile(file_path):
        print(True)
    else:
        print(False)
        messagebox.showinfo(title='错误', message="当前文件不存在，请选择正确的文件")
        return

    file_path = file_path.replace("\\", "/")
    suffix = file_path.rsplit(".", 1)[1]
    print(suffix)
    var = select.get()
    result_path = ""
    result = True
    if var == 1:
        if suffix == "huffman":
            print("huffman解压")
            try:
                myhuffman = MyHuffman(file_path)
                result_path = myhuffman.do_decoding()
            except Exception as e:
                result = False
                messagebox.showinfo(title='压缩错误', message=e)
        else:
            messagebox.showinfo(title='错误', message="输入的文件格式不正确，请输入正确的压缩文件格式(xxx.huffman)")
            return
    else:
        if suffix == "lzss":
            print("lzss解压")
            try:
                mylzss = MyLzss(file_path)
                result_path = mylzss.do_decoding()
            except Exception as e:
                result = False
                messagebox.showinfo(title='压缩错误', message=e)
        else:
            messagebox.showinfo(title='错误', message="输入的文件格式不正确，请输入正确的压缩文件格式(xxx.lzss)")
            return
    if result:
        messagebox.showinfo(title='提示', message='解压成功！\n新文件路径为' + result_path)


path = tk.StringVar()
select = tk.IntVar()
btn1 = tk.Button(top, text='添加文件', font=('楷体', 14), command=choose_file)
btn1.place(x=350, y=20)

btn2 = tk.Button(top, text='压缩文件', font=('楷体', 14), command=encode)
btn2.place(x=350, y=70)

btn3 = tk.Button(top, text='解压文件', font=('楷体', 14), command=decode)
btn3.place(x=350, y=120)

entry = tk.Entry(top, textvariable=path)
entry.place(x=20, y=50, width=300, height=30)

select.set(1)
radio1 = tk.Radiobutton(top, variable=select, text="Huffman", value=1)
radio1.place(x=100, y=100)
radio2 = tk.Radiobutton(top, variable=select, text="Lzss", value=2)
radio2.place(x=200, y=100)
top.mainloop()

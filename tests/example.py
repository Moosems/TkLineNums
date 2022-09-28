from tkinter import Text, Tk
from tkinter.font import Font
from tkinter.ttk import Style

from tklinenums import TkLineNumbers

root = Tk()

style = Style()
style.configure("TLineNumbers", background="#ffffff", foreground="#2197db")

text = Text(root, wrap="char")
text.pack(side="right")

for i in range(50):
    text.insert("end", f"Line {i+1}\n")

font = Font(family="Courier New bold", size=15, name="TkLineNumsFont")

linenums = TkLineNumbers(root, text, font)
linenums.pack(fill="y", side="left", expand=True)
linenums.reload(font)

text.bind("<Key>", lambda event: root.after_idle(linenums.redraw))
text["yscrollcommand"] = linenums.redraw

root.mainloop()

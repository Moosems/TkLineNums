from tkinter import Text, Tk
from tkinter.font import Font
from tkinter.ttk import Style
from platform import system

if system() == "Darwin":
    contmand = "Command"
else:
    contmand = "Control"

from tklinenums import TkLineNumbers

root = Tk()

style = Style()
style.configure("TLineNumbers", background="#ffffff", foreground="#2197db")

font = Font(family="Courier New bold", size=15, name="TkLineNumsFont")

text = Text(root, wrap="char", font=font)
text.pack(side="right")

for i in range(50):
    text.insert("end", f"Line {i+1}\n")

linenums = TkLineNumbers(root, text, font, justify="left")
linenums.pack(fill="y", side="left", expand=True)
linenums.reload(font)

text.bind("<Key>", lambda event: root.after_idle(linenums.redraw), add=True)
text.bind(f"<BackSpace>", lambda event: root.after_idle(linenums.redraw), add=True)
text.bind(f"<{contmand}-v>", lambda event: root.after_idle(linenums.redraw), add=True)
text["yscrollcommand"] = linenums.redraw

root.mainloop()

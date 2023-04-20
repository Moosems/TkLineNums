from platform import system
from tkinter import Text, Tk
from tkinter.ttk import Style

if system() == "Darwin":
    contmand: str = "Command"
else:
    contmand: str = "Control"

from tklinenums import TkLineNumbers

root = Tk()

style = Style()
style.configure("TLineNumbers", background="#ffffff", foreground="#2197db")

text = Text(root, wrap="char", font=("Courier New bold", 15))
text.pack(side="right")

for i in range(50):
    text.insert("end", f"Line {i+1}\n")

linenums = TkLineNumbers(root, text)
linenums.pack(fill="y", side="left", expand=True)

text.bind("<Key>", lambda event: root.after_idle(linenums.redraw), add=True)
text.bind("<BackSpace>", lambda event: root.after_idle(linenums.redraw), add=True)
text.bind(f"<{contmand}-v>", lambda event: root.after_idle(linenums.redraw), add=True)
text["yscrollcommand"] = linenums.redraw

root.mainloop()

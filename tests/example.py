from tkinter import Text, Tk
from tkinter.ttk import Style

from tklinenums import TkLineNumbers

root = Tk()

style = Style()
style.theme_create(
    "myScheme",
    parent="clam",
    settings={
        "TLineNumbers": {
            "configure": {"background": "#ffffff", "foreground": "#2197db"}
        }
    },
)
style.theme_use("myScheme")

text = Text(root)
text.pack(side="right")

linenums = TkLineNumbers(root, text, ("Courier New bold", 15))
linenums.pack(fill="y", side="left", expand=True)
linenums.reload(("Courier New bold", 15))

text.bind("<Key>", lambda event: root.after_idle(linenums.redraw))
text["yscrollcommand"] = linenums.redraw

root.mainloop()

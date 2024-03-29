from tkinter import Text, Tk
from tkinter.ttk import Style

from tklinenums import TkLineNumbers

# Create the root window
root = Tk()

# Set the ttk style (tkinter's way of styling) for the line numbers
style = Style()
style.configure("TkLineNumbers", foreground="#2197db", background="#ffffff")


# Create a style_provider function that returns the ttk style for the line numbers
def ttk_style_provider():
    fg: str = style.lookup("TkLineNumbers", "foreground", default="black")
    bg: str = style.lookup("TkLineNumbers", "background", default="white")
    return (fg, bg)


# Create the Text widget and pack it to the right
text = Text(root)
text.pack(side="right")

# Insert 50 lines of text into the Text widget
for i in range(50):
    text.insert("end", f"Line {i+1}\n")

# Create the TkLineNumbers widget and pack it to the left
linenums = TkLineNumbers(root, text, justify="center", colors=ttk_style_provider)
linenums.pack(fill="y", side="left")

# Redraw the line numbers when the text widget contents are modified
text.bind("<<Modified>>", lambda _: root.after_idle(linenums.redraw), add=True)

# Start the mainloop for the root window
root.mainloop()

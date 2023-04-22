<h1 align="center">TkLineNums</h1>

> **Note**
> If Python was installed via Homebrew, installed on Mac by default, or installed on Linux, tkinter will likely not work properly and may need to be installed via `brew install python-tk` or with the distro package manager on Linux as documented [here](https://tecadmin.net/how-to-install-python-tkinter-on-linux/).

## Description
`TkLineNums` is a simple line numbering widget for Python's `tkinter` GUI library. It is directly connects to a `Text` widget and even supports ttk themes through the set_to_ttk_style method.

![img](https://github.com/Moosems/TkLineNums/raw/main/images/TkLineNumsPhoto.png)

## Features of the `TkLineNums` widget:

- Clicking on line numbers will set the insert to the beginning of the line.
- Shift clicking will select all text from the end of the line clicked by cursor and the insert position.
- Scrolling the linebar will scroll the text widget (and vice versa).
- Supports ttk themes (by usage of the `.set_to_ttk_style()` method)
- Supports left, right, and center alignment with the `-justify` option
- Clicking and then dragging the mouse will scroll the text widget (see [#8](https://github.com/Moosems/TkLineNums/pull/8))

# Installation
`pip install tklinenums`

## Documentation
### `TkLineNums` Widget
|Options|Description|Type|
|---|---|---|
|master|The parent widget|Tkinter widget (defaults to `tkinter.Misc`)|
|editor|The `Text` widget the line numbers will connect to|Tkinter `Text` widget (or child class)|
|justify|The alignment of the line numbers|A string as either `"left"`, `"right"`, or `"center"`|
|*args|Arguments for the `Canvas` widget|Any arguments used for the `Canvas` widget|
|**kwargs|Keyword arguments for the `Canvas` widget|Any keyword arguments used for the `Canvas` widget|

### Basic Usage:
```python
from platform import system
from tkinter import Text, Tk
from tkinter.ttk import Style

from tklinenums import TkLineNumbers

# This is to make the example work on both Windows and Mac
if system() == "Darwin":
    contmand: str = "Command"
else:
    contmand: str = "Control"

# Create the root window
root = Tk()

# Set the ttk style (tkinter's way of styling) for the line numbers
style = Style()
style.configure("TLineNumbers", background="#ffffff", foreground="#2197db")

# Create the Text widget and pack it to the right
text = Text(root)
text.pack(side="right")

# Insert 50 lines of text into the Text widget
for i in range(50):
    text.insert("end", f"Line {i+1}\n")

# Create the TkLineNumbers widget and pack it to the left
linenums = TkLineNumbers(root, text)
linenums.pack(fill="y", side="left")

# Create binds to redraw the line numbers for most common events that change the text in the Text widget
text.bind("<Key>", lambda event: root.after_idle(linenums.redraw), add=True)
text.bind("<BackSpace>", lambda event: root.after_idle(linenums.redraw), add=True)
text.bind(f"<{contmand}-v>", lambda event: root.after_idle(linenums.redraw), add=True)

# Start the mainloop for the root window
root.mainloop()
```
For a more complete example, see the [example.py](./tests/example.py) file.

## How to run and contribute

### Running

To run the example, run `python3 tests/example.py` in the root directory. The project uses only standard library modules, so there are no dependencies. It will create a window with a `Text` widget and a `TkLineNumbers` widget and 50 lines of text to mess around with.

To test newer features or test code in a Pull Review, run `python3 tklinenums/tklinenums.py` in the root directory. Since the package is relatively small it doesn't have any relative imports, so you can run it directly.

### Contributing

To contribute, fork the repository, make your changes, and then make a pull request. If you want to add a feature, please open an issue first so we can discuss it.


## License

This project is licensed under the MIT License - see the [LICENSE](./LISCENSE).

<h1 align="center">TkLineNums</h1>

> **Note**
> If Python was installed via Homebrew, installed on Mac by default, or installed on Linux, tkinter will likely not work properly and may need to be installed via `brew install python-tk` or with the distro package manager on Linux as documented [here](https://tecadmin.net/how-to-install-python-tkinter-on-linux/).

## Description
`TkLineNums` is a simple line numbering widget for Python's `tkinter` GUI library. It is directly connects to a `Text` widget and even supports ttk themes through the set_to_ttk_style method.

![img](misc/TkLineNumsPhoto.png)

## Features of the `TkLineNums` widget:

- Clicking on line numbers will set the insert to the beginning of the line.
- Shift clicking will select all text from the end of the line clicked by cursor and the insert position.
- Scrolling the linebar will scroll the text widget (and vice versa).
- Can handle elided lines (elided lines are lines that are not visible in the text widget).
- Supports ttk themes and allows easy color customization.
- Supports left, right, and center alignment with the `-justify` option.
- Clicking and then dragging the mouse will scroll the text widget.
- Supports click dragging for selection.

# Installation

In the Command Line, paste the following: `pip install tklinenums`.

## Documentation
### `TkLineNums` Widget
|Options|Description|Type|
|---|---|---|
|master|The parent widget|Tkinter widget (defaults to `tkinter.Misc`)|
|textwidget|The `Text` widget the line numbers will connect to|Tkinter `Text` widget (or child class)|
|justify|The alignment of the line numbers|A string as either `"left"`, `"right"`, or `"center"`|
|colors|A way to provide coloring to the line numbers|A function, `(foreground, background)` tuple, or None. None (default) makes it use the `Text` widget's coloring. The function should return a `(foreground, background)` tuple: it will be called whenever the colors are needed, and it is useful when the colors can change.|
|*args|Arguments for the `Canvas` widget|Any arguments used for the `Canvas` widget|
|**kwargs|Keyword arguments for the `Canvas` widget|Any keyword arguments used for the `Canvas` widget|

### Basic Usage:
```python
from tkinter import Text, Tk
from tkinter.ttk import Style

from tklinenums import TkLineNumbers

# Create the root window
root = Tk()

# Create the Text widget and pack it to the right
text = Text(root)
text.pack(side="right")

# Insert 50 lines of text into the Text widget
for i in range(50):
    text.insert("end", f"Line {i+1}\n")

# Create the TkLineNumbers widget and pack it to the left
linenums = TkLineNumbers(root, text, justify="center", colors=("#2197db", "#ffffff"))
linenums.pack(fill="y", side="left")

# Redraw the line numbers when the text widget contents are modified
text.bind("<<Modified>>", lambda event: root.after_idle(linenums.redraw), add=True)

# Start the mainloop for the root window
root.mainloop()
```
For a more complete example, see [misc/example.py](./misc/example.py).

## How to run and contribute

### Running

To run the example, run `python3 misc/example.py` in the root directory. The project uses only standard library modules, so there are no dependencies. It will create a window with a `Text` widget and a `TkLineNumbers` widget and 50 lines of text to mess around with.

To test newer features or test code in a Pull Review, run `python3 tklinenums/tklinenums.py` in the root directory. Since the package is relatively small it doesn't have any relative imports, so you can run it directly.

### Contributing

To contribute, fork the repository, make your changes, and then make a pull request. If you want to add a feature, please open an issue first so we can discuss it.


## License

This project is licensed under the MIT License - see the [LICENSE](./LISCENSE).

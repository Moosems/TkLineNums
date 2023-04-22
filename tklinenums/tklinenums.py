"""TkLineNumbers - A line number widget for tkinter Text widgets"""
from __future__ import annotations

from platform import system
from tkinter import Canvas, Event, Misc, Text, getboolean
from tkinter.font import Font
from typing import Callable


def scroll_inversion(delta: int) -> int:
    """Corrects scrolling numbers across platforms"""

    # The scroll events passed by MacOS are different from Windows and Linux
    # so it must to be rectified to work properly when dealing with the events.
    # Originally found here: https://stackoverflow.com/a/17457843/17053202
    return -delta if system() == "Darwin" else delta / 120


class TkLineNumError(Exception):
    ...


class TkLineNumbers(Canvas):
    """
    Creates a line number widget for a text widget. Options are the same as a tkinter Canvas widget and add the following:
        * -textwidget (Text): The text widget to attach the line numbers to. (Required) (Second argument after master)
        * -justify (str): The justification of the line numbers. Can be "left", "right", or "center". Default is "left".

    Methods to be used outside externally:
        * .redraw(): Redraws the widget (to be used when the text widget is modified)
    """

    def __init__(
        self: TkLineNumbers,
        master: Misc,
        textwidget: Text,
        justify: str = "left",
        # None means take colors from text widget (default).
        # Otherwise it is a function that takes no arguments and returns (fg, bg) tuple.
        colors: Callable[[], tuple[str, str]] | tuple[str, str] | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Initializes the widget -- Internal use only"""

        # Initialize the Canvas widget
        Canvas.__init__(
            self,
            master,
            width=kwargs.pop("width", 40),
            highlightthickness=kwargs.pop("highlightthickness", 0),
            borderwidth=kwargs.pop("borderwidth", 2),
            relief=kwargs.pop("relief", "ridge"),
            *args,
            **kwargs,
        )

        # Set variables
        self.textwidget = textwidget
        self.master = master
        self.justify = justify
        self.click_pos: None = None
        self.colors = colors

        # Set style and its binding
        self.set_colors()
        self.bind("<<ThemeChanged>>", self.set_colors, add=True)

        # Mouse scroll binding
        self.bind("<MouseWheel>", self.mouse_scroll, add=True)
        self.bind("<Button-4>", self.mouse_scroll, add=True)
        self.bind("<Button-5>", self.mouse_scroll, add=True)

        # Click bindings
        self.bind("<Button-1>", self.click_see, add=True)
        self.bind("<ButtonRelease-1>", self.unclick, add=True)
        self.bind("<Double-Button-1>", self.double_click, add=True)

        # Drag bindings
        self.bind("<Button1-Motion>", self.drag, add=True)
        self.bind("<Button1-Leave>", self.auto_scroll, add=True)
        self.bind("<Button1-Enter>", self.stop_auto_scroll, add=True)

        # Set the yscrollcommand of the text widget to redraw the widget
        textwidget["yscrollcommand"] = self.redraw

        # Redraw the widget
        self.redraw()

    def redraw(self, *args) -> None:
        """Redraws the widget"""

        # Resize the widget based on the number of lines in the textwidget and set colors
        del args
        self.resize()
        self.set_colors()

        # Delete all the old line numbers
        self.delete("all")

        # Get the first and last line numbers for the textwidget (all other lines are in between)
        first_line, last_line = int(self.textwidget.index("@0,0").split(".")[0]), int(
            self.textwidget.index(f"@0,{self.textwidget.winfo_height()}").split(".")[0]
        )

        # Draw the line numbers looping through the lines
        for lineno in range(first_line, last_line + 1):
            # Check if line is elided
            tags: list = self.textwidget.tag_names(f"{lineno}.0")
            elide_values: tuple = (
                self.textwidget.tag_cget(tag, "elide") for tag in tags
            )
            # elide values can be empty
            line_elided: bool = any(getboolean(v or "false") for v in elide_values)

            # If the line is not visible, skip it
            if (
                dlineinfo := self.textwidget.dlineinfo(f"{lineno}.0")
            ) is None or line_elided:
                continue

            # Create the line number
            self.create_text(
                0
                if self.justify == "left"
                else int(self["width"])
                if self.justify == "right"
                else int(self["width"]) / 2,
                dlineinfo[1],
                text=f" {lineno} " if self.justify != "center" else f"{lineno}",
                anchor={"left": "nw", "right": "ne", "center": "n"}[self.justify],
                font=self.textwidget.cget("font"),
                fill=self.foreground_color,
            )

    def mouse_scroll(self, event: Event) -> None:
        """Scrolls the text widget when the mouse wheel is scrolled -- Internal use only"""

        # Scroll the text widget and then redraw the widget
        self.textwidget.yview_scroll(int(scroll_inversion(event.delta)), "units")
        self.redraw()

    def click_see(self, event: Event) -> None:
        """When clicking on a line number it scrolls to that line if not shifting -- Internal use only"""

        # If the shift key is down, redirect to self.shift_click()
        if event.state == 1:
            self.shift_click(event)
            return

        # Remove the selection tag from the text widget
        self.textwidget.tag_remove("sel", "1.0", "end")

        # Set the insert position to the line number clicked
        self.textwidget.mark_set(
            "insert",
            f"{self.textwidget.index(f'@{event.x},{event.y}').split('.')[0]}.0",
        )

        # Scroll to the location of the insert position
        self.textwidget.see("insert")

        # If the line clicked is at the edge of the screen, scroll by one line to bring it into view
        first_visible_line, last_visible_line = int(
            self.textwidget.index("@0,0").split(".")[0]
        ), int(
            self.textwidget.index(f"@0,{self.textwidget.winfo_height()}").split(".")[0]
        )
        insert = int(self.textwidget.index("insert").split(".")[0])
        if insert == first_visible_line:
            self.textwidget.yview_scroll(scroll_inversion(-1), "units")
        elif insert == last_visible_line:
            self.textwidget.yview_scroll(scroll_inversion(1), "units")
        self.click_pos: str = self.textwidget.index("insert")
        self.redraw()

    def unclick(self, event: Event) -> None:
        """When the mouse button is released it removes the selection -- Internal use only"""

        del event
        self.click_pos = None

    def double_click(self, event: Event) -> None:
        """Selects the line when double clicked -- Internal use only"""

        # Remove the selection tag from the text widget and select the line
        del event
        self.textwidget.tag_remove("sel", "1.0", "end")
        self.textwidget.tag_add("sel", "insert", "insert + 1 line")
        self.redraw()

    def auto_scroll(self, event: Event) -> None:
        """Automatically scrolls the text widget when the mouse is near the top or bottom,
        similar to the drag function -- Internal use only"""

        if self.click_pos is None:
            return

        # Taken from the Text source: https://github.com/tcltk/tk/blob/main/library/text.tcl#L676
        # Scrolls the widget if the cursor is off of the screen
        if event.y >= self.winfo_height():
            self.textwidget.yview_scroll(1, "units")
        elif event.y < 0:
            self.textwidget.yview_scroll(-1, "units")
        else:
            return

        # Select the text
        self.select_text(event=event)

        # After 50ms, call this function again
        self.cancellable_after = self.after(50, self.auto_scroll, event)
        self.redraw()

    def stop_auto_scroll(self, event: Event) -> None:
        """Stops the auto scroll when the cursor re-enters the line numbers -- Internal use only"""

        # If the after has not been cancelled, cancel it
        if self.cancellable_after is not None:
            self.after_cancel(self.cancellable_after)
            self.cancellable_after: None = None

    def drag(self, event: Event) -> None:
        """When click dragging it selects the text -- Internal use only"""

        # If the click position is None, return
        if self.click_pos is None or event.y < 0 or event.y >= self.winfo_height():
            return

        # Select the text
        start: str = self.textwidget.index("insert")
        self.select_text(start, event=event)

    def select_text(
        self, start: str | None = None, end: str | None = None, event: Event = Event
    ) -> None:
        """Selects the text between the start and end positions -- Internal use only"""

        # If the start and end positions are None, set them to the click position and the cursor position
        if start is None:
            start: str = self.textwidget.index(f"@{event.x},{event.y}")
        if end is None:
            end: str = self.click_pos

        # If the click position is greater than the cursor position, swap them
        if self.textwidget.compare("insert", ">", self.click_pos):
            start, end = end, str(float(start) + 2)
        else:
            end = str(float(end) + 1)

        # Select the text and move the insert position to the start of the
        # line corresponding to the event position
        self.textwidget.tag_remove("sel", "1.0", "end")
        self.textwidget.tag_add("sel", start, end)
        self.textwidget.mark_set("insert", f"@{event.x},{event.y} linestart")
        self.redraw()

    def shift_click(self, event: Event) -> None:
        """When shift clicking it selects the text between the click and the cursor -- Internal use only"""

        # Add the selection tag to the text between the click and the cursor
        start_pos: str = self.textwidget.index("insert")
        end_pos: str = self.textwidget.index(f"@0,{event.y}")
        self.textwidget.tag_remove("sel", "1.0", "end")
        if self.textwidget.compare(start_pos, ">", end_pos):
            start_pos, end_pos = end_pos, start_pos
        self.textwidget.tag_add("sel", start_pos, end_pos)
        self.redraw()

    def resize(self) -> None:
        """Resizes the widget to fit the text widget -- Internal use only"""

        # Get amount of lines in the text widget
        end = self.textwidget.index("end").split(".")[0]

        # Set the width of the widget to the required width to display the biggest line number
        temp_font = self.textwidget.cget("font")
        self.config(width=Font(font=temp_font).measure(" 1234 ")) if int(
            end
        ) <= 1000 else self.config(width=temp_font.measure(f" {end} "))

    def set_colors(self, event: Event | None = None) -> None:
        """Sets the colors of the widget according to self.colors - Internal use only"""

        # The event is irrelevant so it is deleted
        del event

        # If the color provider is None, set the foreground color to the Text widget's foreground color
        if self.colors is None:
            self.foreground_color = self.textwidget["fg"]
            self["bg"] = self.textwidget["bg"]
        elif isinstance(self.colors, tuple):
            self.foreground_color, self["bg"] = self.colors
        else:
            self.foreground_color, self["bg"] = self.colors()


if __name__ == "__main__":
    from tkinter import Tk
    from tkinter.ttk import Style

    root = Tk()

    style = Style()
    style.configure("TkLineNumbers", foreground="#2197db", background="#ffffff")

    text = Text(root)
    text.pack(side="right")

    for i in range(50):
        text.insert("end", f"Line {i+1}\n")

    def ttk_theme_colors() -> tuple[str, str]:
        fg: str = style.lookup("TkLineNumbers", "foreground")
        bg: str = style.lookup("TkLineNumbers", "background")
        return (fg, bg)

    linenums = TkLineNumbers(root, text, colors=ttk_theme_colors)
    linenums.pack(fill="y", side="left", expand=True)

    text.bind("<<Modified>>", lambda event: linenums.redraw())
    text.config(font=("Courier New bold", 15))

    root.mainloop()

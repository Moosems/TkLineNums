"""TkLineNumbers - A line number widget for tkinter Text widgets"""
from __future__ import annotations

import platform
from tkinter import Canvas, Event, Misc, Text
from tkinter.font import Font
from typing import Callable

system: str = str(platform.system())
if system in ("Darwin" or "Windows"):
    scroll_inversion: Callable[[int], int] = lambda delta: -delta
else:
    scroll_inversion: Callable[[int], int] = lambda delta: int(delta / 120)


class TkLineNumError(Exception):
    ...


class TkLineNumbers(Canvas):
    """
    Creates a line number widget for a text widget. Options are the same as a tkinter Canvas widget and add the following:
        * -justify (str): The justification of the line numbers. Can be "left", "right", or "center". Default is "left".
        * -font (tuple | Font | str | None): The font of the line numbers. Default is the text widget's font.
        * -editor (Text): The text widget to attach the line numbers to. (Required) (Second argument after master)

    Methods to be used outside externally:
        * .redraw(): Redraws the widget
        * .resize(): Calculates the required width of the widget and resizes it according to the text widget's font and the number of lines
        * .set_to_ttk_style(): Sets the foreground and background colors to the ttk style of the text widget
        * .reload_font(): Reloads the font of the widget (Requires font as argument)
    """

    def __init__(
        self: TkLineNumbers,
        master: Misc,
        editor: Text,
        justify: str = "left",
        *args,
        **kwargs,
    ) -> None:
        """Initializes the widget -- Internal use only"""
        self.textwidget: Misc = editor
        self.master: Misc = master
        self.justify: str = justify
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
        self.set_to_ttk_style()

        self.bind("<MouseWheel>", self.mouse_scroll, add=True)
        # If I'm mouse scrolling and I am clicking on line numbers, it should select the lines from where I clicked to where I am scrolling
        # TODO: Make it so that it selects the lines from where I clicked to where I am scrolling
        self.bind("<Button-1>", self.click_see, add=True)
        self.bind("<ButtonRelease-1>", self.unclick, add=True)
        self.bind("<Double-Button-1>", self.double_click, add=True)
        self.bind("<Button1-Motion>", self.drag, add=True)
        self.bind("<Button1-Leave>", self.auto_scroll, add=True)
        self.bind("<Button1-Enter>", self.stop_auto_scroll, add=True)

        self.click_pos: None | str = None
        self.cancellable_after: Callable | None = None

        self.reload()

    def redraw(self, *args) -> None:
        """Redraws the widget"""
        self.resize()
        self.delete("all")

        first_line: int = int(self.textwidget.index("@0,0").split(".")[0])
        last_line: int = int(self.textwidget.index(f"@0,{self.textwidget.winfo_height()}").split(".")[0]) + 1
        for lineno in range(first_line, last_line):
            dlineinfo: tuple | None = self.textwidget.dlineinfo(f"{lineno}.0")
            if dlineinfo is None:
                continue
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
                fill=self.foreground,
            )

    def mouse_scroll(self, event: Event) -> None:
        """Scrolls the text widget when the mouse wheel is scrolled -- Internal use only"""
        if system == "Darwin":
            self.textwidget.yview_scroll(scroll_inversion(event.delta), "units")
        else:
            self.textwidget.yview_scroll(int(scroll_inversion(event.delta)), "units")
        self.redraw()

    def click_see(self, event: Event) -> None:
        """When clicking on a line number it scrolls to that line if not shifting -- Internal use only"""
        if event.state == 1:
            self.shift_click(event)
            return
        self.textwidget.tag_remove("sel", "1.0", "end")
        self.textwidget.mark_set(
            "insert",
            f"{self.textwidget.index(f'@{event.x},{event.y}').split('.')[0]}.0",
        )
        self.textwidget.see("insert")
        first_visible_line: int = int(self.textwidget.index("@0,0").split(".")[0])
        last_visible_line: int = int(
            self.textwidget.index(f"@0,{self.textwidget.winfo_height()}").split(".")[0]
        )
        insert: int = int(self.textwidget.index("insert").split(".")[0])
        if insert == first_visible_line:
            self.textwidget.yview_scroll(scroll_inversion(-1), "units")
        elif insert == last_visible_line:
            self.textwidget.yview_scroll(scroll_inversion(1), "units")
        self.click_pos: str = self.textwidget.index("insert")

    def unclick(self, event: Event) -> None:
        """When the mouse button is released it removes the selection -- Internal use only"""
        del event
        self.click_pos: None = None

    def double_click(self, event: Event) -> None:
        """Selects the line when double clicked -- Internal use only"""
        del event
        self.textwidget.tag_remove("sel", "1.0", "end")
        self.textwidget.tag_add("sel", "insert", "insert + 1 line")

    def auto_scroll(self, event: Event) -> None:
        """Automatically scrolls the text widget when the mouse is near the top or bottom, similar to the drag function -- Internal use only"""
        if self.click_pos is None:
            return
        # scroll_inversion is not used here as this is a direct translation from the Text widget's auto_scroll function
        if event.y >= self.winfo_height():
            self.textwidget.yview_scroll(1, "units")
        elif event.y < 0:
            self.textwidget.yview_scroll(-1, "units")
        elif event.x >= self.winfo_width():
            self.textwidget.xview_scroll(2, "units")
        elif event.x < 0:
            self.textwidget.xview_scroll(-2, "units")
        else:
            return
        start: str = self.textwidget.index("insert")
        end: str = self.click_pos
        if self.textwidget.compare("insert", ">", self.click_pos):
            start, end = end, str(float(start) + 1)
        else:
            end = str(float(end) + 1)
        self.textwidget.tag_remove("sel", "1.0", "end")
        self.textwidget.tag_add("sel", start, end)
        self.textwidget.mark_set("insert", f"@{event.x},{event.y}")
        self.cancellable_after = self.after(50, self.auto_scroll, event)

    def stop_auto_scroll(self, event: Event) -> None:
        """Stops the auto scroll -- Internal use only"""
        if self.cancellable_after is not None:
            self.after_cancel(self.cancellable_after)
            self.cancellable_after: None = None

    def drag(self, event: Event) -> None:
        """When click dragging it selects the text -- Internal use only"""
        if (
            self.click_pos is None
            or event.x < 0
            or event.x >= self.winfo_width()
            or event.y < 0
            or event.y >= self.winfo_height()
        ):
            return
        start: str = self.textwidget.index("insert")
        end: str = self.click_pos
        if self.textwidget.compare("insert", ">", self.click_pos):
            start, end = end, str(float(start) + 1)
        else:
            end = str(float(end) + 1)

        self.textwidget.tag_remove("sel", "1.0", "end")
        self.textwidget.tag_add("sel", start.split(".")[0] + ".0", end.split(".")[0] + ".0")
        self.textwidget.mark_set("insert", self.textwidget.index(f"@{event.x},{event.y} linestart + 1 line"))
        self.redraw()

        """
        Issues:
         - Erratic behavior causes it to pause and requires reentering the text widget
         - If I click and start dragging, drag into the text, and then back into the linenumbers it has a weird behavior
         - If I drag into the text widget and keep dragging, sel is not added
        """  # TODO: Fix issues

    def shift_click(self, event: Event) -> None:
        """When shift clicking it selects the text between the click and the cursor -- Internal use only"""
        start_pos: str = self.textwidget.index("insert")
        end_pos: str = self.textwidget.index(f"@0,{event.y}")
        self.textwidget.tag_remove("sel", "1.0", "end")
        if self.textwidget.compare(start_pos, ">", end_pos):
            start_pos, end_pos = end_pos, start_pos
        self.textwidget.tag_add("sel", start_pos, end_pos)

    def resize(self) -> None:
        """Resizes the widget to fit the text widget"""
        end: str = self.textwidget.index("end").split(".")[0]
        self.config(width=Font(font=(temp_font := self.textwidget.cget("font"))).measure(" 1234 ")) if int(
            end
        ) <= 1000 else self.config(width=temp_font.measure(f" {end} "))

    def set_to_ttk_style(self) -> None:
        """Sets the widget to the ttk style"""
        self["bg"]: str = self.tk.eval("ttk::style lookup TLineNumbers -background")
        self.foreground: str = self.tk.eval("ttk::style lookup TLineNumbers -foreground")

    def reload(self) -> None:
        """Reloads the widget"""
        self.set_to_ttk_style()
        self.redraw()


if __name__ == "__main__":
    from platform import system
    from tkinter import Text, Tk
    from tkinter.font import Font
    from tkinter.ttk import Style

    if system() == "Darwin":
        contmand: str = "Command"
    else:
        contmand: str = "Control"

    from tklinenums import TkLineNumbers

    root: Tk = Tk()

    style: Style = Style()
    style.configure("TLineNumbers", background="#ffffff", foreground="#2197db")

    text: Text = Text(root, wrap="char", font=("Courier New bold", 15))
    text.pack(side="right")

    for i in range(50):
        text.insert("end", f"Line {i+1}\n")

    linenums: TkLineNumbers = TkLineNumbers(root, text)
    linenums.pack(fill="y", side="left", expand=True)

    text.bind("<Key>", lambda event: root.after_idle(linenums.redraw), add=True)
    text.bind(f"<BackSpace>", lambda event: root.after_idle(linenums.redraw), add=True)
    text.bind(f"<{contmand}-v>", lambda event: root.after_idle(linenums.redraw), add=True)
    text["yscrollcommand"] = linenums.redraw

    root.mainloop()

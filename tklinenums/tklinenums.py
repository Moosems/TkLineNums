"""TkLineNumbers - A line number widget for tkinter Text widgets"""
from __future__ import annotations

from platform import system
from tkinter import Canvas, Event, Misc, Text
from tkinter.font import Font
from typing import Callable


def scroll_inversion(delta: int) -> int:
    """Corrects scrolling numbers across platforms"""
    return -(delta if system() == "Darwin" else delta / 120)

class TkLineNumError(Exception):
    ...


class TkLineNumbers(Canvas):
    """
    Creates a line number widget for a text widget. Options are the same as a tkinter Canvas widget and add the following:
        * -editor (Text): The text widget to attach the line numbers to. (Required) (Second argument after master)
        * -justify (str): The justification of the line numbers. Can be "left", "right", or "center". Default is "left".

    Methods to be used outside externally:
        * .redraw(): Redraws the widget
        * .resize(): Calculates the required width of the widget and resizes it 
        according to the text widget's font and the number of lines (run in redraw())
        * .set_to_ttk_style(): Sets the foreground and background colors to the ttk style of the text widget
        * .reload(): Sets the widget to the ttk style, and redraws the widget
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
        self.editor: Misc = editor
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

        #Mouse scroll binding
        self.bind("<MouseWheel>", self.mouse_scroll, add=True)
        self.bind("<Button-4>", self.mouse_scroll, add=True)
        self.bind("<Button-5>", self.mouse_scroll, add=True)

        #Click bindings
        self.bind("<Button-1>", self.click_see, add=True)
        self.bind("<ButtonRelease-1>", self.unclick, add=True)
        self.bind("<Double-Button-1>", self.double_click, add=True)

        #Drag bindings
        self.bind("<Button1-Motion>", self.drag, add=True)
        self.bind("<Button1-Leave>", self.auto_scroll, add=True)
        self.bind("<Button1-Enter>", self.stop_auto_scroll, add=True)

        self.click_pos: str | None = None
        self.cancellable_after: Callable | None = None

        self.reload()

    def redraw(self, *args) -> None:
        """Redraws the widget"""
        del args
        self.resize()
        self.delete("all")

        first_line: int = int(self.editor.index("@0,0").split(".")[0])
        last_line: int = (
            int(self.editor.index(f"@0,{self.editor.winfo_height()}").split(".")[0]) + 1
        )
        for lineno in range(first_line, last_line):
            dlineinfo: tuple | None = self.editor.dlineinfo(f"{lineno}.0")
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
                font=self.editor.cget("font"),
                fill=self.foreground,
            )

    def mouse_scroll(self, event: Event) -> None:
        """Scrolls the text widget when the mouse wheel is scrolled -- Internal use only"""
        self.editor.yview_scroll(int(scroll_inversion(event.delta)), "units")
        self.redraw()

    def click_see(self, event: Event) -> None:
        """When clicking on a line number it scrolls to that line if not shifting -- Internal use only"""
        if event.state == 1:
            self.shift_click(event)
            return
        self.editor.tag_remove("sel", "1.0", "end")
        self.editor.mark_set(
            "insert",
            f"{self.editor.index(f'@{event.x},{event.y}').split('.')[0]}.0",
        )
        self.editor.see("insert")
        first_visible_line = int(self.editor.index("@0,0").split(".")[0])
        last_visible_line = int(
            self.editor.index(f"@0,{self.editor.winfo_height()}").split(".")[0]
        )
        insert = int(self.editor.index("insert").split(".")[0])
        if insert == first_visible_line:
            self.editor.yview_scroll(scroll_inversion(-1), "units")
        elif insert == last_visible_line:
            self.editor.yview_scroll(scroll_inversion(1), "units")
        self.click_pos: str = self.editor.index("insert")

    def unclick(self, event: Event) -> None:
        """When the mouse button is released it removes the selection -- Internal use only"""
        del event
        self.click_pos = None

    def double_click(self, event: Event) -> None:
        """Selects the line when double clicked -- Internal use only"""
        del event
        self.editor.tag_remove("sel", "1.0", "end")
        self.editor.tag_add("sel", "insert", "insert + 1 line")

    def auto_scroll(self, event: Event) -> None:
        """Automatically scrolls the text widget when the mouse is near the top or bottom, 
        similar to the drag function -- Internal use only"""
        if self.click_pos is None:
            return
        if event.y >= self.winfo_height():
            self.editor.yview_scroll(1, "units")
        elif event.y < 0:
            self.editor.yview_scroll(-1, "units")
        else:
            return
        self.select_text(event=event)
        self.cancellable_after = self.after(50, self.auto_scroll, event)

    def stop_auto_scroll(self, event: Event) -> None:
        """Stops the auto scroll -- Internal use only"""
        if self.cancellable_after is not None:
            self.after_cancel(self.cancellable_after)
            self.cancellable_after: None = None

    def drag(self, event: Event) -> None:
        """When click dragging it selects the text -- Internal use only"""
        if self.click_pos is None or event.y < 0 or event.y >= self.winfo_height():
            return
        start: str = self.editor.index("insert")
        self.select_text(start, event=event)

    def select_text(
        self, start: str | None = None, end: str | None = None, event: Event = Event
    ) -> None:
        """Selects the text between the start and end positions -- Internal use only"""
        if start is None:
            start: str = self.editor.index(f"@{event.x},{event.y}")
        if end is None:
            end: str = self.click_pos
        if self.editor.compare("insert", ">", self.click_pos):
            start, end = end, str(float(start) + 2)
        else:
            end = str(float(end) + 1)
        self.editor.tag_remove("sel", "1.0", "end")
        self.editor.tag_add("sel", start, end)
        self.editor.mark_set("insert", f"@{event.x},{event.y} linestart")

    def shift_click(self, event: Event) -> None:
        """When shift clicking it selects the text between the click and the cursor -- Internal use only"""
        start_pos: str = self.editor.index("insert")
        end_pos: str = self.editor.index(f"@0,{event.y}")
        self.editor.tag_remove("sel", "1.0", "end")
        if self.editor.compare(start_pos, ">", end_pos):
            start_pos, end_pos = end_pos, start_pos
        self.editor.tag_add("sel", start_pos, end_pos)
        self.redraw()

    def resize(self) -> None:
        """Resizes the widget to fit the text widget"""
        end: str = self.editor.index("end").split(".")[0]
        self.config(
            width=Font(font=(temp_font := self.editor.cget("font"))).measure(" 1234 ")
        ) if int(end) <= 1000 else self.config(width=temp_font.measure(f" {end} "))

    def set_to_ttk_style(self) -> None:
        """Sets the widget to the ttk style"""
        self["bg"]: str = self.tk.eval("ttk::style lookup TLineNumbers -background")
        self.foreground: str = self.tk.eval(
            "ttk::style lookup TLineNumbers -foreground"
        )

    def reload(self) -> None:
        """Reloads the widget"""
        self.set_to_ttk_style()
        self.redraw()


if __name__ == "__main__":
    from tkinter import Tk
    from tkinter.ttk import Style

    if system() == "Darwin":
        contmand: str = "Command"
    else:
        contmand: str = "Control"

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
    text.bind(
        f"<{contmand}-v>", lambda event: root.after_idle(linenums.redraw), add=True
    )
    text["yscrollcommand"] = linenums.redraw

    root.mainloop()

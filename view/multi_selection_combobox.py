import tkinter as tk
from typing import Sequence

from view.constants import Colors as c
from view.constants import Fonts as f

class MultiSelectionComboBox(tk.Frame):
    def __init__(self, parent, on_selection_changed, **kwargs):
        super().__init__(parent,bg=c.WINDOW_BACKGROUND, **kwargs)

        self.menubutton = tk.Menubutton(self, text="Select tables",
                                        indicatoron=True, borderwidth=1, relief="raised")
        self.menu = tk.Menu(self.menubutton, tearoff=False)
        self.on_selection_changed = on_selection_changed
        self.menubutton.configure(menu=self.menu)
        self.menubutton.pack(padx=10, pady=10)

        self.choices = {}

    def set_state(self, new_state):
        self.menubutton['state'] = new_state

    def set_options(self, options: Sequence[str]):
        self.choices.clear()
        self.menu.delete(0, tk.END)
        self.menubutton['text'] = 'Select tables'
        for choice in options:
            self.choices[choice] = tk.IntVar(value=0)
            self.menu.add_checkbutton(label=choice, variable=self.choices[choice],
                                      onvalue=1, offvalue=0,font=f.LABELS_FONT,
                                      command=self.selection_changed)

    def selection_changed(self):
        selected = list()
        for name, var in self.choices.items():
            if var.get() == 1:
                selected.append(name)
        self.menubutton['text'] = ', '.join(selected) if len(selected) > 0 else 'Select tables'
        self.on_selection_changed(self.get_selection_indices())

    def get_selection_indices(self) -> Sequence[int]:
        return [index for index, value in enumerate(self.choices.values()) if value.get() == 1]

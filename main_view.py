import tkinter as tk
from tkinter import ttk
from typing import Sequence

import db
import view.constants as consts
from view.constants import Colors as c
from view.constants import Fonts as f
from view.multi_selection_combobox import MultiSelectionComboBox
from view.constants import WindowVariables as wv

class MainView(tk.Frame):
    def __init__(self):
        tk.Frame.__init__(self)
        consts.Fonts.initialize_fonts()
        # declare constants & Variables:
        self.message_variable: tk.StringVar
        self.window: tk.Tk
        self.table: ttk.Treeview
        self.current_table: str
        self.cols_data: Sequence[db.ColumnData]
        self.home_frame: tk.Frame
        self.table_names: Sequence[str]
        self.table_box: ttk.Combobox
        self.home_frame: tk.Frame
        self.filter_columns_combobox: ttk.Combobox
        self.add_filter_bn: tk.Button
        self.text_box: tk.Entry
        self.listbox: tk.Listbox
        self.joinable_table_selected_box: MultiSelectionComboBox
        # self.operators_cb: ttk.Combobox
        self.handler: db.SqlLiteHandler = db.SqlLiteHandler.get_instance()
        self.list_id: int = 0
        self.filters_applying = list()
        self.last_sort_col = ''
        self.init_main_frame_view()
        self.init_table_selector_view()
        self.init_main_table_view()
        self.init_join_tables_menu_view()
        self.init_filter_pane()

        # ___ Set initial values ___
        # ___ Set initial values ___
        self.table_box.set(self.table_names[0])
        self.view_table(self.table_names[0])

    def init_join_tables_menu_view(self) -> None:
        """
        Initialize all tables' join related views
        """
        button_frame = tk.Frame(self.home_frame)
        button_frame.grid(row=4, column=0, sticky=tk.W)
        button_frame.config(bg=c.WINDOW_BACKGROUND)

        # Create tables names Combobox
        # self.joinable_tables = self.handler.get_related_tables(self.current_table)

        self.joinable_table_selected_box = MultiSelectionComboBox(button_frame, self.callback_joined_table_selected,
                                                                  width=20)
        self.joinable_table_selected_box.grid(column=2, row=0, padx=5, pady=5)

        message_label = tk.Label(button_frame, text="Join with", font=f.H2_FONT, bg=c.WINDOW_BACKGROUND)
        message_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=15)

    def init_filter_pane(self) -> None:
        """
        Initialize all filter related views 
        """
        query_frame = tk.LabelFrame(self.window, bg=c.WINDOW_BACKGROUND, text="Filters", width=250, height=80)
        query_frame.grid(row=1, column=0, sticky=tk.NSEW)

        # Set columns names
        tk.Label(query_frame, text="column names", font=f.H2_FONT, bg=c.WINDOW_BACKGROUND).grid(column=0,
                                                                                                row=0,
                                                                                                padx=5,
                                                                                                pady=5)
        # Create column names Combobox
        self.filter_columns_combobox = ttk.Combobox(query_frame, width=20, font=f.LABELS_FONT)
        self.filter_columns_combobox['state'] = 'readonly'
        self.filter_columns_combobox.grid(column=0, row=1, padx=10, pady=5, sticky=tk.W)

        # Set label Operator
        tk.Label(query_frame, text="operator", font=f.H2_FONT, bg=c.WINDOW_BACKGROUND).grid(column=1, row=0,
                                                                                            padx=5, pady=5)
        self.filter_columns_combobox.bind("<<ComboboxSelected>>", self.callback_columns_combobox)
        # Create Operator names Combobox
        self.operator_combobox = ttk.Combobox(query_frame, width=20, font=f.LABELS_FONT, state=tk.DISABLED)
        self.operator_combobox.grid(column=1, row=1, padx=5, pady=5)
        self.operator_combobox.bind("<<ComboboxSelected>>", self.callback_operators_combobox)

        # Set Exception Label
        self.exception_str = tk.StringVar()
        tk.Label(query_frame, textvar=self.exception_str, font=f.LABELS_FONT, fg=c.EXCEPTION_FOREGROUND,
                 bg=c.WINDOW_BACKGROUND).grid(column=0, row=2, padx=5,
                                              pady=5)

        # Set label
        tk.Label(query_frame, text="value", font=f.H2_FONT, bg=c.WINDOW_BACKGROUND).grid(column=2, row=0, padx=5,
                                                                                         pady=5)

        self.text_box = tk.Entry(query_frame, width=20, font=f.LABELS_FONT)
        self.text_box.grid(column=2, row=1, padx=5, pady=5)
        self.is_case_sensitive = tk.BooleanVar(value=True)
        case_sensitive_cb = tk.Checkbutton(query_frame, text="Case sensitive", variable=self.is_case_sensitive,
                                           width=12, bg=c.WINDOW_BACKGROUND, activebackground=c.WINDOW_BACKGROUND,
                                           font=f.H2_FONT)
        case_sensitive_cb.grid(column=2, row=5)

        # +
        self.add_filter_bn = tk.Button(query_frame, text="+", font=f.BUTTONS_FONT, bg=c.BUTTON_BACKGROUND,
                                       command=self.on_click_add_filter, state=tk.DISABLED)
        self.add_filter_bn.grid(column=3, row=1, padx=5, pady=5)

        self.remove_filter_btn = tk.Button(query_frame, text="-", font=f.BUTTONS_FONT, state=tk.DISABLED,
                                           bg=c.BUTTON_BACKGROUND, command=self.on_click_remove_filter)
        self.remove_filter_btn.grid(column=4, row=1, padx=5, pady=5)

        # Filter Frame
        filter_frame = tk.Frame(query_frame, bg=c.WINDOW_BACKGROUND)
        filter_frame.grid(column=0, row=3, sticky=tk.NSEW, columnspan=3)
        self.listbox = tk.Listbox(filter_frame, width=80, height=5, selectmode="extended ")
        self.listbox.grid(column=0, row=0, padx=5, pady=10)
        self.listbox.bind('<<ListboxSelect>>', self.callback_listbox_selection)

        # Submit BTN
        self.submit_btn = tk.Button(query_frame, text="Submit", font=f.BUTTONS_FONT, state=tk.DISABLED,
                                    bg=c.BUTTON_BACKGROUND, command=self.on_click_submit_filter)
        self.submit_btn.grid(column=1, row=5, padx=5, pady=5, columnspan=2)

    def init_main_frame_view(self) -> None:
        """
        Initialize all main frame's related views
        """
        self.window = self.master
        # Set the name & geometry of main window
        self.window.eval('tk::PlaceWindow . center')
        self.window.title(wv.WINDOW_TITLE)
        self.window.geometry("{}x{}+{}+{}".format(wv.WINDOW_SIZE_W, wv.WINDOW_SIZE_H, wv.WINDOW_LEFT_CORNER_X, wv.WINDOW_LEFT_CORNER_Y))
        #self.window.geometry(consts.WindowVariables.WINDOW_SIZE)
        # Disable resizing in x and y directions
        self.window.resizable(True, True)
        self.window.attributes('-topmost', 1)
        self.window['bg'] = c.WINDOW_BACKGROUND

        # setup main view's grid (home_frame)
        self.home_frame = tk.LabelFrame(self.window, bg=c.WINDOW_BACKGROUND, text="Data", font=f.LABELS_FONT, width=250,
                                        height=80)
        self.home_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        self.home_frame.rowconfigure(0, weight=1)
        self.home_frame.columnconfigure(0, weight=1)

    def init_table_selector_view(self) -> None:
        """
        Initialize all tables' selector related views
        """
        # Set label for selecting table
        # tk.Label(self.home_frame, text="Select The Table:",
        #  font=f.H1_FONT, bg=c.WINDOW_BACKGROUND) \
        #  .grid(column=0, row=0, padx=5, pady=5)
        # Create tables names Combobox
        self.table_names = self.handler.table_names
        self.table_box = ttk.Combobox(self.home_frame,
                                      values=self.table_names,
                                      width=27,
                                      font=f.LABELS_FONT)
        self.table_box['state'] = 'readonly'
        self.table_box.bind("<<ComboboxSelected>>", self.callback_select_main_table)
        self.table_box.grid(column=0, row=1, padx=5, pady=5)

    def init_join_ables_menu_view(self) -> None:
        """
        Initialize all table joining related views
        """
        button_frame = tk.Frame(self.home_frame)
        button_frame.grid(row=4, column=0, sticky=tk.W)
        button_frame.config(bg=c.WINDOW_BACKGROUND)

        # Create tables names Combobox
        # self.joinable_tables = self.handler.get_related_tables(self.current_table)

        self.joinable_table_selected_box = MultiSelectionComboBox(button_frame, self.callback_joined_table_selected,
                                                                  width=20)
        self.joinable_table_selected_box.grid(column=2, row=0, padx=5, pady=5)

        message_label = tk.Label(button_frame, text="Join with", font=f.H2_FONT, bg=c.WINDOW_BACKGROUND)
        message_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=15)

    def init_main_table_view(self) -> None:
        """
        Initialize all main table's related views
        """
        # init TreeView Object and locate it in frame
        self.table = ttk.Treeview(self.home_frame, show="headings", height=8, selectmode=tk.BROWSE)
        self.table.grid(column=0, row=2, sticky=tk.NSEW)
        # Setup scrollbars
        vertical_scrollbar = ttk.Scrollbar(self.home_frame, orient=tk.VERTICAL, command=self.table.yview)
        vertical_scrollbar.grid(column=1, row=2, sticky=tk.NS)
        self.table.configure(yscrollcommand=vertical_scrollbar.set)

        horizontal_scrollbar = ttk.Scrollbar(self.home_frame, orient=tk.HORIZONTAL, command=self.table.xview)
        horizontal_scrollbar.grid(column=0, row=3, sticky=tk.EW)
        self.table.configure(xscrollcommand=horizontal_scrollbar.set)

        #  table fonts & style
        style = ttk.Style()
        style.configure("Treeview.Heading", font=consts.Fonts.H2_FONT, text="B")
        style.configure('.', font=f.LABELS_FONT)

    def on_click_remove_filter(self) -> None:
        """
        removes filter from filter list
        """
        selection = self.listbox.curselection()  # value
        for index in reversed(selection):
            self.listbox.delete(index)
            self.filters_applying.pop(index)
        self.remove_filter_btn['state'] = tk.DISABLED
        if len(self.filters_applying) == 0:
            self.submit_btn['state'] = tk.DISABLED
            self.on_click_submit_filter()

    def on_click_submit_filter(self) -> None:
        """
        fetch all the data from db (including joins) and apply the filters specified.
        """
        all_data = self.handler.filter_last_executed_query(self.filters_applying, self.is_case_sensitive.get())
        self.display_new_data_in_table(self.cols_names, all_data)

    def on_click_add_filter(self) -> None:
        """
        Adding another filter (won't execute filter until clicking submit_filter)
        """
        col_idx = self.filter_columns_combobox.current()  # name of col
        operator = self.operator_combobox.current()  # operator
        value = self.text_box.get()  # value
        if col_idx == -1 or operator == -1:
            self.exception_str.set('Must select a column and an operator!!!')
            return

        flter = db.get_filter(self.cols_data[col_idx])
        flter.operator = flter.operators[operator]
        try:
            self.exception_str.set('')
            flter.value = value
            self.filters_applying.append(flter)

            self.list_id += 1
            self.listbox.insert(self.list_id, str(flter))
            self.text_box.delete(0, tk.END)
            self.operator_combobox.set('')
            self.text_box['state'] = tk.DISABLED
            self.add_filter_bn['state'] = tk.DISABLED
            self.submit_btn['state'] = tk.NORMAL
        except ValueError as e:
            self.exception_str.set(e)

    def callback_listbox_selection(self, event) -> None:
        """
        Marks selected filter (currently only used for removing filters)
        """
        self.remove_filter_btn['state'] = tk.NORMAL if len(event.widget.curselection()) > 0 else tk.DISABLED

    def callback_columns_combobox(self, event) -> None:
        """
        Args:
            event: holds the data of the click event that triggered the callback
        Harteteishen litigation
        """
        index = event.widget.current()
        flter = db.get_filter(self.cols_data[index])
        self.operator_combobox['values'] = flter.operators
        self.operator_combobox['state'] = 'readonly'

    def callback_operators_combobox(self, _) -> None:
        """
        Args:
            _: holds the data of the click event that triggered the callback
        We love you Itzik
        """
        self.text_box['state'] = tk.NORMAL
        self.add_filter_bn['state'] = tk.NORMAL

    def callback_select_main_table(self, event) -> None:
        """
        Args:
            event: holds the data of the click event that triggered the callback
        Harteteishen litigation
        """
        selected_table = event.widget.get()
        self.view_table(selected_table)
        if len(self.handler.get_related_tables(selected_table)) > 0:
            self.joinable_table_selected_box.set_state(tk.NORMAL)
        else:
            self.joinable_table_selected_box.set_state(tk.DISABLED)
        self.filters_applying.clear()
        self.listbox.delete(0, tk.END)

    def callback_joined_table_selected(self, indices: Sequence[int]) -> None:
        """
        Args:
            indices: incices of the tables we are about to join

        display joined data main table
        """
        selected_tables = [self.joinable_tables[table_index] for table_index in indices]
        self.cols_data, data = self.handler.join_tables(self.current_table, *selected_tables)
        self.cols_names = [col.get_full_name() for col in self.cols_data]
        self.filter_columns_combobox['values'] = self.cols_names
        self.display_new_data_in_table(self.cols_names, data)
        self.filters_applying.clear()
        self.listbox.delete(0, tk.END)

    def display_joinable_tables(self) -> None:
        """
        Ze masbir et azmo..
        """
        self.joinable_tables = self.handler.get_related_tables(self.current_table)
        self.joinable_table_selected_box.set_options([t.table_name for t in self.joinable_tables])
        # self.joinable_table_selected_box['values'] = [t.table_name for t in self.joinable_tables]

    def view_table(self, table_name: str) -> None:
        """
        Args:
            table_name: name of the main table we are about to display
        1. get columns
        2. get data for required columns
        3. updating columns for filtering process
        """

        # ___ get current table's data ___
        # get columns
        self.current_table = table_name
        self.cols_data = self.handler.get_columns_for(table_name)
        self.cols_names = [col.title for col in self.cols_data]
        # get data for required columns
        all_data = self.handler.get_data_from_table(table_name, columns_names=self.cols_names)

        self.display_new_data_in_table(self.cols_names, all_data)

        # updating columns for filtering process
        self.filter_columns_combobox['values'] = self.cols_names
        self.display_joinable_tables()

    def display_new_data_in_table(self, cols_names, all_data) -> None:
        """
        Args:
            cols_names:  columns we are about to display
            all_data:  the data we are about to display

        displays data on main table
        """
        self.text_box['state'] = tk.DISABLED
        self.add_filter_bn['state'] = tk.DISABLED
        self.operator_combobox['state'] = tk.DISABLED
        self.operator_combobox.set('')
        self.filter_columns_combobox.set('')
        self.last_sort_col = ''
        # delete all existing data from table_view
        self.table.delete(*self.table.get_children())
        self.window.update()

        # ___ build view from data retrieved ___
        # set table's columns
        self.table['columns'] = cols_names

        # ___ Adding the data into the table_view ___
        for col in cols_names:
            self.table.heading(col, text=col.title(), command=lambda c=col: self.treeview_sort_column(self.table, c, 0),
                               anchor=tk.W)

        for i, item in enumerate(all_data):
            self.table.insert('', tk.END, i, values=item)

    def treeview_sort_column(self, table, col, reverse) -> None:
        """

        Args:
            table: don't ask me.. we have it in self
            col: the col we are sorting by
            reverse: is reversing the order or not

        sort the data in the table according to the col (ascending or descending order)

        """
        l = [(table.set(k, col), k) for k in table.get_children('')]
        try:
            l.sort(key=lambda t: int(t[0]), reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            table.move(k, '', index)

        if len(self.last_sort_col) > 0 and self.last_sort_col != col:
            temp = self.last_sort_col
            table.heading(self.last_sort_col, text=self.last_sort_col,
                          command=lambda: self.treeview_sort_column(table, temp, False))

        arrow = '▼' if reverse else '▲'
        table.heading(col, text=f'{col.title()} ({arrow})',
                      command=lambda: self.treeview_sort_column(table, col, not reverse))
        self.last_sort_col = col


def main() -> None:
    """
        Runs the program
    """
    main_view = MainView()
    main_view.mainloop()


if __name__ == '__main__':
    main()

import customtkinter as ctk
from . import styles # 新增

class BookListView(ctk.CTkFrame):
    def __init__(self, master, library_instance, master_app, **kwargs):
        super().__init__(master, **kwargs)
        self.library_instance = library_instance
        self.master_app = master_app

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) # 修改: 为 info_label 和 header_frame 调整行号

        # --- Search Frame ---
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=styles.PAD_X_MEDIUM, pady=(styles.PAD_Y_MEDIUM, styles.PAD_Y_SMALL))
        search_frame.grid_columnconfigure(3, weight=1) 

        ctk.CTkLabel(search_frame, text="搜索类型:", font=styles.FONT_ENTRY_LABEL).pack(side="left", padx=(0, styles.PAD_X_SMALL))
        self.search_type_var = ctk.StringVar(value="ISBN")
        search_type_options = ["ISBN", "作者", "书名"] 
        self.search_type_menu = ctk.CTkOptionMenu(
            search_frame, 
            variable=self.search_type_var, 
            values=search_type_options,
            height=styles.HEIGHT_OPTIONMENU,
            corner_radius=styles.CORNER_RADIUS_BUTTON, # 使用按钮圆角或特定条目圆角
            font=styles.FONT_BUTTON # 与按钮字体一致
        )
        self.search_type_menu.pack(side="left", padx=styles.PAD_X_SMALL)

        ctk.CTkLabel(search_frame, text="关键词:", font=styles.FONT_ENTRY_LABEL).pack(side="left", padx=(styles.PAD_X_MEDIUM, styles.PAD_X_SMALL))
        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="输入搜索关键词...",
            height=styles.HEIGHT_ENTRY,
            corner_radius=styles.CORNER_RADIUS_ENTRY,
            font=styles.FONT_NORMAL
        )
        self.search_entry.pack(side="left", padx=styles.PAD_X_SMALL, fill="x", expand=True)
        self.search_entry.bind("<Return>", self.perform_search) 

        search_button = ctk.CTkButton(
            search_frame, 
            text="搜索", 
            command=self.perform_search,
            height=styles.HEIGHT_BUTTON,
            width=80, # 可根据styles调整
            corner_radius=styles.CORNER_RADIUS_BUTTON,
            font=styles.FONT_BUTTON,
            fg_color=styles.PRIMARY_COLOR,
            hover_color=styles.PRIMARY_COLOR_HOVER
        )
        search_button.pack(side="left", padx=styles.PAD_X_SMALL)
        
        clear_search_button = ctk.CTkButton(
            search_frame, 
            text="显示全部", 
            command=self.show_all_books,
            height=styles.HEIGHT_BUTTON,
            width=100, # 可根据styles调整
            corner_radius=styles.CORNER_RADIUS_BUTTON,
            font=styles.FONT_BUTTON,
            fg_color=styles.SECONDARY_COLOR,
            hover_color=styles.SECONDARY_COLOR_HOVER
        )
        clear_search_button.pack(side="left", padx=(styles.PAD_X_SMALL,0))

        # --- Info Label for search results --- 新增
        self.info_label = ctk.CTkLabel(self, text="", font=styles.FONT_NORMAL)
        self.info_label.grid(row=1, column=0, sticky="w", padx=styles.PAD_X_MEDIUM, pady=(styles.PAD_Y_SMALL, 0))
        
        # --- Header Frame for Table ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=2, column=0, sticky="ew", padx=styles.PAD_X_MEDIUM, pady=(styles.PAD_Y_SMALL,0)) # 修改: 调整行号
        header_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1) # 5 data columns
        header_frame.grid_columnconfigure(5, weight=0) # Action column

        headers = ["ISBN", "书名", "作者", "出版年份", "总副本数", "操作"]
        for i, header_text in enumerate(headers):
            label = ctk.CTkLabel( # 修改: 应用表头样式
                header_frame, 
                text=header_text, 
                font=styles.FONT_TABLE_HEADER,
                fg_color=styles.PRIMARY_COLOR,
                text_color="white",
                corner_radius=styles.CORNER_RADIUS_TABLE_HEADER,
                padx=styles.PAD_X_MEDIUM, # 内边距
                pady=styles.PAD_Y_SMALL
            )
            sticky_val = "ew" # 让标签填充单元格宽度以显示背景色
            if header_text == "操作":
                 pass # 操作列通常较窄，其内容（按钮）会右对齐
            label.grid(row=0, column=i, padx=(0 if i == 0 else styles.PAD_X_SMALL, 0 if i == len(headers)-1 else styles.PAD_X_SMALL) , pady=styles.PAD_Y_SMALL, sticky=sticky_val)


        # Scrollable Frame for book entries
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=3, column=0, sticky="nsew", padx=styles.PAD_X_MEDIUM, pady=(0, styles.PAD_Y_MEDIUM)) # 修改: 调整行号和边距
        self.scrollable_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1) # 5 data columns
        self.scrollable_frame.grid_columnconfigure(5, weight=0) # Action column (less weight or fixed)

    def populate_table(self, books_data):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not books_data: # 修改: 更新info_label
            self.info_label.configure(text="没有可显示的书籍。", text_color=styles.WARNING_COLOR)
            no_data_label = ctk.CTkLabel(
                self.scrollable_frame, 
                text="没有可显示的书籍数据。", 
                pady=styles.PAD_Y_LARGE, 
                font=styles.FONT_LARGE_NORMAL,
                text_color=("gray60", "gray40")
            )
            no_data_label.grid(row=0, column=0, columnspan=6, sticky="ew")
            return
        
        self.info_label.configure(text=f"共找到 {len(books_data)} 本书籍。", text_color=styles.SUCCESS_COLOR)

        for i, book in enumerate(books_data):
            # 修改: 使用带背景的row_frame实现Zebra Striping
            row_fg_color = (styles.TABLE_ROW_LIGHT_EVEN, styles.TABLE_ROW_DARK_EVEN) if i % 2 == 0 else \
                           (styles.TABLE_ROW_LIGHT_ODD, styles.TABLE_ROW_DARK_ODD)
            row_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=row_fg_color, corner_radius=styles.CORNER_RADIUS_FRAME / 2 if styles.CORNER_RADIUS_FRAME else 0)
            row_frame.grid(row=i, column=0, columnspan=6, sticky="ew", pady=(styles.PAD_Y_SMALL / 2, styles.PAD_Y_SMALL / 2), padx=2)
            
            # 配置row_frame的列权重，与表头和scrollable_frame一致
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
            row_frame.grid_columnconfigure(5, weight=0)

            # ISBN
            isbn_label = ctk.CTkLabel(row_frame, text=book.isbn, anchor="w", font=styles.FONT_TABLE_CELL)
            isbn_label.grid(row=0, column=0, padx=styles.PAD_X_MEDIUM, pady=styles.PAD_Y_SMALL, sticky="ew")

            # Title
            title_label = ctk.CTkLabel(row_frame, text=book.title, anchor="w", font=styles.FONT_TABLE_CELL)
            title_label.grid(row=0, column=1, padx=styles.PAD_X_MEDIUM, pady=styles.PAD_Y_SMALL, sticky="ew")

            # Author
            author_label = ctk.CTkLabel(row_frame, text=book.author, anchor="w", font=styles.FONT_TABLE_CELL)
            author_label.grid(row=0, column=2, padx=styles.PAD_X_MEDIUM, pady=styles.PAD_Y_SMALL, sticky="ew")

            # Publication Year
            year_label = ctk.CTkLabel(row_frame, text=str(book.publication_year), anchor="w", font=styles.FONT_TABLE_CELL)
            year_label.grid(row=0, column=3, padx=styles.PAD_X_MEDIUM, pady=styles.PAD_Y_SMALL, sticky="ew")
            
            # Total Copies
            copies_label = ctk.CTkLabel(row_frame, text=str(book.total_copies), anchor="w", font=styles.FONT_TABLE_CELL)
            copies_label.grid(row=0, column=4, padx=styles.PAD_X_MEDIUM, pady=styles.PAD_Y_SMALL, sticky="ew")

            # Action buttons frame
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=5, padx=styles.PAD_X_SMALL, pady=0, sticky="e") 
            
            edit_button = ctk.CTkButton( # 修改: 应用按钮样式
                actions_frame,
                text="修改",
                width=styles.WIDTH_TABLE_ROW_ACTION_BUTTON,
                height=styles.HEIGHT_TABLE_ROW_ACTION_BUTTON,
                corner_radius=styles.CORNER_RADIUS_BUTTON / 1.5, # 稍小圆角
                font=styles.FONT_BUTTON,
                fg_color=styles.SECONDARY_COLOR,
                hover_color=styles.SECONDARY_COLOR_HOVER,
                command=lambda b_isbn=book.isbn: self.master_app.open_edit_book_dialog(b_isbn)
            )
            edit_button.pack(side="left", padx=(0,styles.PAD_X_SMALL))

            delete_button = ctk.CTkButton( # 修改: 应用按钮样式
                actions_frame,
                text="删除",
                width=styles.WIDTH_TABLE_ROW_ACTION_BUTTON,
                height=styles.HEIGHT_TABLE_ROW_ACTION_BUTTON,
                corner_radius=styles.CORNER_RADIUS_BUTTON / 1.5,
                font=styles.FONT_BUTTON,
                fg_color=styles.DANGER_COLOR, 
                hover_color=styles.DANGER_COLOR_HOVER,
                command=lambda b_isbn=book.isbn: self.master_app.confirm_delete_book(b_isbn)
            )
            delete_button.pack(side="left")

    def perform_search(self, event=None): 
        search_type = self.search_type_var.get()
        keyword = self.search_entry.get().strip()

        if not keyword:
            self.info_label.configure(text="请输入搜索关键词。", text_color=styles.WARNING_COLOR) # 修改: 更新info_label
            # self.master_app.update_status("请输入搜索关键词。", success=False) # 改为使用本地info_label
            self.populate_table([]) # 清空表格并显示无数据提示
            return

        found_books = []
        try:
            if search_type == "ISBN":
                book = self.library_instance.find_book_by_isbn(keyword)
                if book:
                    found_books = [book]
            elif search_type == "作者":
                found_books = self.library_instance.find_books_by_author(keyword)
            elif search_type == "书名": 
                found_books = self.library_instance.find_books_by_title(keyword)
            
            self.populate_table(found_books) # populate_table内部会更新info_label
            # if found_books: # 修改: 状态栏更新移至 populate_table
            #     self.master_app.update_status(f"找到 {len(found_books)} 本关于 '{keyword}' 的书籍。", success=True)
            # else:
            #     self.master_app.update_status(f"未找到关于 '{keyword}' 的书籍。", success=False)
        except Exception as e:
            self.info_label.configure(text=f"搜索时发生错误: {e}", text_color=styles.DANGER_COLOR) # 修改: 更新info_label
            # self.master_app.update_status(f"搜索时发生错误: {e}", success=False)
            self.populate_table([])
            print(f"Search error: {e}") 

    def show_all_books(self):
        self.search_entry.delete(0, ctk.END) 
        all_books_list = list(self.library_instance.books.values())
        self.populate_table(all_books_list) # populate_table内部会更新info_label
        # self.master_app.update_status(f"已显示所有 {len(all_books_list) if all_books_list else 0} 本书籍。", success=True) # 移至populate_table

if __name__ == '__main__':
    # Example Usage (for testing BookListView independently)
    # Note: This test App needs to be updated to reflect style changes if run directly
    class App(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Book List View Test")
            self.geometry("800x600")
            
            # Mock styles for testing if styles.py is not fully integrated in this test
            class MockStyles:
                FONT_ENTRY_LABEL = ctk.CTkFont(size=12)
                FONT_BUTTON = ctk.CTkFont(size=12)
                FONT_TABLE_HEADER = ctk.CTkFont(size=14, weight="bold")
                FONT_TABLE_CELL = ctk.CTkFont(size=12)
                FONT_NORMAL = ctk.CTkFont(size=12)
                FONT_LARGE_NORMAL = ctk.CTkFont(size=14)

                PRIMARY_COLOR = "#3B8ED0"
                PRIMARY_COLOR_HOVER = "#36719F"
                SECONDARY_COLOR = "#6c757d"
                SECONDARY_COLOR_HOVER = "#545b62"
                DANGER_COLOR = "#dc3545"
                DANGER_COLOR_HOVER = "#C82333"
                SUCCESS_COLOR = "#28a745"
                WARNING_COLOR = "#ffc107"
                
                TABLE_ROW_LIGHT_EVEN = "gray92"
                TABLE_ROW_LIGHT_ODD = "gray98"
                TABLE_ROW_DARK_EVEN = "gray22"
                TABLE_ROW_DARK_ODD = "gray18"

                PAD_X_SMALL = 5
                PAD_Y_SMALL = 5
                PAD_X_MEDIUM = 10
                PAD_Y_MEDIUM = 10
                PAD_Y_LARGE = 20
                
                HEIGHT_BUTTON = 30
                HEIGHT_ENTRY = 30
                HEIGHT_OPTIONMENU = 30
                HEIGHT_TABLE_ROW_ACTION_BUTTON = 28
                WIDTH_TABLE_ROW_ACTION_BUTTON = 60
                
                CORNER_RADIUS_BUTTON = 6
                CORNER_RADIUS_ENTRY = 6
                CORNER_RADIUS_FRAME = 0 # Example, might be 0 for rows
                CORNER_RADIUS_TABLE_HEADER = 6

            # Replace global styles with MockStyles for this test scope
            global styles
            _original_styles = styles
            styles = MockStyles()


            class MockBook:
                def __init__(self, title, author, isbn, publication_year, total_copies):
                    self.title = title
                    self.author = author
                    self.isbn = isbn
                    self.publication_year = publication_year
                    self.total_copies = total_copies
            
            class MockLibrary:
                def __init__(self):
                    self.books = {
                        "978-7-115-42802-8": MockBook("Python编程从入门到实践", "埃里克·马瑟斯", "978-7-115-42802-8", 2016, 10),
                        "978-7-115-45415-7": MockBook("流畅的Python", "Luciano Ramalho", "978-7-115-45415-7", 2017, 5),
                        "978-7-115-45602-1": MockBook("算法图解", "Aditya Bhargava", "978-7-115-45602-1", 2017, 8),
                        "978-7-115-51800-2": MockBook("Effective Python", "Brett Slatkin", "978-7-115-51800-2", 2020, 3)
                    }
                def find_book_by_isbn(self, isbn): return self.books.get(isbn)
                def find_books_by_author(self, author_keyword): 
                    return [b for b in self.books.values() if author_keyword.lower() in b.author.lower()]
                def find_books_by_title(self, title_keyword):
                    return [b for b in self.books.values() if title_keyword.lower() in b.title.lower()]


            self.library_instance = MockLibrary()
            
            self.book_list_view = BookListView(self, library_instance=self.library_instance, master_app=self)
            self.book_list_view.pack(fill="both", expand=True, padx=10, pady=10)
            
            self.book_list_view.populate_table(list(self.library_instance.books.values()))

            # Restore original styles if it was mocked
            styles = _original_styles


        def open_edit_book_dialog(self, isbn):
            print(f"Master app: Request to edit book with ISBN: {isbn}")
            dialog = ctk.CTkToplevel(self)
            dialog.geometry("300x200")
            dialog.title("Edit Book (Placeholder)")
            label = ctk.CTkLabel(dialog, text=f"Editing book: {isbn}")
            label.pack(padx=20, pady=20)

        def confirm_delete_book(self, isbn):
            print(f"Master app: Request to delete book with ISBN: {isbn}")
            dialog = ctk.CTkToplevel(self)
            dialog.geometry("300x200")
            dialog.title("Confirm Delete (Placeholder)")
            label = ctk.CTkLabel(dialog, text=f"Confirm delete book: {isbn}?")
            label.pack(padx=20, pady=20)
        
        def update_status(self, message, success=True): # Mock for testing
            print(f"Status Update: {message} (Success: {success})")


    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
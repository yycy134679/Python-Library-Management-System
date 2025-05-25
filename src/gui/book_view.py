import customtkinter as ctk

class BookListView(ctk.CTkFrame):
    def __init__(self, master, library_instance, master_app, **kwargs):
        # Extract master_app before calling super().__init__ if it's in kwargs,
        # or ensure it's passed explicitly and not part of **kwargs to super.
        # For clarity, we'll assume master_app is always passed explicitly and not in kwargs for super.
        super().__init__(master, **kwargs)
        self.library_instance = library_instance
        self.master_app = master_app

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Adjusted row for scrollable_frame due to search_frame

        # --- Search Frame ---
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,5))
        search_frame.grid_columnconfigure(3, weight=1) # Allow search entry to expand

        ctk.CTkLabel(search_frame, text="搜索类型:").pack(side="left", padx=(0,5))
        self.search_type_var = ctk.StringVar(value="ISBN")
        search_type_options = ["ISBN", "作者", "书名"] # Added "书名"
        # Using CTkOptionMenu as CTkSegmentedButton might be too wide for this layout
        self.search_type_menu = ctk.CTkOptionMenu(search_frame, variable=self.search_type_var, values=search_type_options)
        self.search_type_menu.pack(side="left", padx=5)

        ctk.CTkLabel(search_frame, text="关键词:").pack(side="left", padx=(10,5))
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="输入搜索关键词...")
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.search_entry.bind("<Return>", self.perform_search) # Allow Enter key to search

        search_button = ctk.CTkButton(search_frame, text="搜索", width=80, command=self.perform_search)
        search_button.pack(side="left", padx=5)
        
        clear_search_button = ctk.CTkButton(search_frame, text="显示全部", width=100, command=self.show_all_books)
        clear_search_button.pack(side="left", padx=(5,0))


        # --- Header Frame for Table ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5,0)) # Adjusted row
        header_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        headers = ["ISBN", "书名", "作者", "出版年份", "总副本数", "操作"]
        for i, header_text in enumerate(headers):
            label = ctk.CTkLabel(header_frame, text=header_text, font=ctk.CTkFont(weight="bold"))
            if header_text == "操作":
                label.grid(row=0, column=i, padx=5, pady=5, sticky="e") # Align "操作" to the right
            else:
                label.grid(row=0, column=i, padx=5, pady=5, sticky="w")


        # Scrollable Frame for book entries
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10) # Adjusted row
        self.scrollable_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

    def populate_table(self, books_data):
        # Clear existing rows
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not books_data:
            no_data_label = ctk.CTkLabel(self.scrollable_frame, text="没有可显示的书籍。", pady=10)
            no_data_label.grid(row=0, column=0, columnspan=6, sticky="ew")
            return

        for i, book in enumerate(books_data):
            # ISBN
            isbn_label = ctk.CTkLabel(self.scrollable_frame, text=book.isbn, anchor="w")
            isbn_label.grid(row=i, column=0, padx=5, pady=5, sticky="ew")

            # Title
            title_label = ctk.CTkLabel(self.scrollable_frame, text=book.title, anchor="w")
            title_label.grid(row=i, column=1, padx=5, pady=5, sticky="ew")

            # Author
            author_label = ctk.CTkLabel(self.scrollable_frame, text=book.author, anchor="w")
            author_label.grid(row=i, column=2, padx=5, pady=5, sticky="ew")

            # Publication Year
            year_label = ctk.CTkLabel(self.scrollable_frame, text=str(book.publication_year), anchor="w")
            year_label.grid(row=i, column=3, padx=5, pady=5, sticky="ew")
            
            # Total Copies
            copies_label = ctk.CTkLabel(self.scrollable_frame, text=str(book.total_copies), anchor="w")
            copies_label.grid(row=i, column=4, padx=5, pady=5, sticky="ew")

            # Action buttons frame
            actions_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            actions_frame.grid(row=i, column=5, padx=5, pady=2, sticky="e") # Align buttons to the right
            
            edit_button = ctk.CTkButton(
                actions_frame,
                text="修改",
                width=60,
                command=lambda b_isbn=book.isbn: self.master_app.open_edit_book_dialog(b_isbn)
            )
            edit_button.pack(side="left", padx=(0,5))

            delete_button = ctk.CTkButton(
                actions_frame,
                text="删除",
                width=60,
                fg_color="red", # Or use theme color for danger
                hover_color="darkred",
                command=lambda b_isbn=book.isbn: self.master_app.confirm_delete_book(b_isbn)
            )
            delete_button.pack(side="left")

    def perform_search(self, event=None): # Added event=None for bind compatibility
        search_type = self.search_type_var.get()
        keyword = self.search_entry.get().strip()

        if not keyword:
            self.master_app.update_status("请输入搜索关键词。", success=False)
            # Optionally, show all books if keyword is empty and search is pressed
            # self.show_all_books()
            return

        found_books = []
        try:
            if search_type == "ISBN":
                book = self.library_instance.find_book_by_isbn(keyword)
                if book:
                    found_books = [book]
            elif search_type == "作者":
                found_books = self.library_instance.find_books_by_author(keyword)
            elif search_type == "书名": # Added case for "书名"
                found_books = self.library_instance.find_books_by_title(keyword)
            
            self.populate_table(found_books)
            if found_books:
                self.master_app.update_status(f"找到 {len(found_books)} 本关于 '{keyword}' 的书籍。", success=True)
            else:
                self.master_app.update_status(f"未找到关于 '{keyword}' 的书籍。", success=False)
        except Exception as e:
            self.master_app.update_status(f"搜索时发生错误: {e}", success=False)
            print(f"Search error: {e}") # For debugging

    def show_all_books(self):
        """Clears search and shows all books."""
        self.search_entry.delete(0, ctk.END) # Clear search entry
        # self.library_instance.books is a dictionary, we need its values
        all_books_list = list(self.library_instance.books.values())
        self.populate_table(all_books_list)
        self.master_app.update_status(f"已显示所有 {len(all_books_list) if all_books_list else 0} 本书籍。", success=True)


if __name__ == '__main__':
    # Example Usage (for testing BookListView independently)
    class App(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Book List View Test")
            self.geometry("800x600")

            # Mock library_instance and Book class for testing
            class MockBook:
                def __init__(self, title, author, isbn, publication_year, total_copies):
                    self.title = title
                    self.author = author
                    self.isbn = isbn
                    self.publication_year = publication_year
                    self.total_copies = total_copies
            
            class MockLibrary:
                def get_all_books(self): # Example method
                    return [
                        MockBook("Python编程从入门到实践", "埃里克·马瑟斯", "978-7-115-42802-8", 2016, 10),
                        MockBook("流畅的Python", "Luciano Ramalho", "978-7-115-45415-7", 2017, 5),
                        MockBook("算法图解", "Aditya Bhargava", "978-7-115-45602-1", 2017, 8),
                        MockBook("Effective Python", "Brett Slatkin", "978-7-115-51800-2", 2020, 3)
                    ]

            self.library_instance = MockLibrary()
            
            self.book_list_view = BookListView(self, library_instance=self.library_instance)
            self.book_list_view.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Populate with dummy data
            self.book_list_view.populate_table(self.library_instance.get_all_books())

        def open_edit_book_dialog(self, isbn):
            print(f"Master app: Request to edit book with ISBN: {isbn}")
            # Placeholder for actual dialog opening
            dialog = ctk.CTkToplevel(self)
            dialog.geometry("300x200")
            dialog.title("Edit Book (Placeholder)")
            label = ctk.CTkLabel(dialog, text=f"Editing book: {isbn}")
            label.pack(padx=20, pady=20)


        def confirm_delete_book(self, isbn):
            print(f"Master app: Request to delete book with ISBN: {isbn}")
            # Placeholder for actual confirmation
            dialog = ctk.CTkToplevel(self) # Using Toplevel for simplicity here, real would be messagebox
            dialog.geometry("300x200")
            dialog.title("Confirm Delete (Placeholder)")
            label = ctk.CTkLabel(dialog, text=f"Confirm delete book: {isbn}?")
            label.pack(padx=20, pady=20)
            # Add Yes/No buttons if using a custom dialog

    app = App()
    app.mainloop()
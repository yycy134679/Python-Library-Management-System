import customtkinter as ctk
from tkinter import messagebox
from src.core_logic.book import Book
from src.core_logic import exceptions
from . import styles # 新增

class AddBookDialog(ctk.CTkToplevel):
    def __init__(self, master, library_instance):
        super().__init__(master)
        self.master_app = master 
        self.library_instance = library_instance

        self.title("添加新书籍")
        self.geometry("450x430") # 修改: 调整尺寸以适应内容和边距
        self.resizable(False, False)
        self.grab_set() 

        self.grid_columnconfigure(1, weight=1)
        # 为内容区域添加统一边距
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=styles.PAD_X_LARGE, pady=styles.PAD_Y_LARGE)
        content_frame.grid_columnconfigure(1, weight=1)

        # --- Input Fields ---
        row_num = 0
        ctk.CTkLabel(content_frame, text="ISBN:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.isbn_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.isbn_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")
        self.isbn_entry.focus() 

        row_num += 1
        ctk.CTkLabel(content_frame, text="书名:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.title_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.title_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")

        row_num += 1
        ctk.CTkLabel(content_frame, text="作者:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.author_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.author_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")

        row_num += 1
        ctk.CTkLabel(content_frame, text="出版年份:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.year_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.year_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")

        row_num += 1
        ctk.CTkLabel(content_frame, text="总副本数:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.copies_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.copies_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")
        
        # --- Error Label ---
        row_num += 1
        self.error_label = ctk.CTkLabel( # 修改: 应用样式
            content_frame, 
            text="", 
            font=styles.FONT_ERROR_TEXT,
            text_color=styles.DANGER_COLOR,
            fg_color=(styles.ERROR_BG_LIGHT, styles.ERROR_BG_DARK),
            corner_radius=styles.CORNER_RADIUS_ERROR_LABEL,
            wraplength=380 # 限制宽度以自动换行
        )
        self.error_label.grid(row=row_num, column=0, columnspan=2, pady=(styles.PAD_Y_SMALL, styles.PAD_Y_MEDIUM), padx=0, sticky="ew")
        self.error_label.grid_remove() # Initially hidden


        # --- Buttons ---
        row_num += 1
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.grid(row=row_num, column=0, columnspan=2, pady=(styles.PAD_Y_MEDIUM, 0), sticky="e") # sticky e to align right
        # button_frame.grid_columnconfigure((0,1), weight=1) # Not needed if sticky="e"

        confirm_button = ctk.CTkButton( # 修改: 应用样式
            button_frame, 
            text="确认添加", 
            command=self.confirm_add,
            height=styles.HEIGHT_BUTTON,
            corner_radius=styles.CORNER_RADIUS_BUTTON,
            font=styles.FONT_BUTTON,
            fg_color=styles.PRIMARY_COLOR,
            hover_color=styles.PRIMARY_COLOR_HOVER
        )
        confirm_button.pack(side="right", padx=(styles.PAD_X_SMALL, 0)) # Pack right first

        cancel_button = ctk.CTkButton( # 修改: 应用样式
            button_frame, 
            text="取消", 
            command=self.destroy, 
            height=styles.HEIGHT_BUTTON,
            corner_radius=styles.CORNER_RADIUS_BUTTON,
            font=styles.FONT_BUTTON,
            fg_color=styles.SECONDARY_COLOR,
            hover_color=styles.SECONDARY_COLOR_HOVER
        )
        cancel_button.pack(side="right", padx=(0, styles.PAD_X_SMALL))

    def _show_error(self, message):
        self.error_label.configure(text=message)
        self.error_label.grid()

    def _clear_error(self):
        self.error_label.grid_remove()
        self.error_label.configure(text="")

    def confirm_add(self):
        self._clear_error()
        isbn = self.isbn_entry.get().strip()
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        year_str = self.year_entry.get().strip()
        copies_str = self.copies_entry.get().strip()

        if not all([isbn, title, author, year_str, copies_str]):
            self._show_error("错误：所有字段均为必填项。")
            return

        try:
            publication_year = int(year_str)
            if publication_year <= 0: 
                 raise ValueError("出版年份必须是正整数。")
        except ValueError:
            self._show_error("错误：出版年份必须是有效的数字。")
            return

        try:
            total_copies = int(copies_str)
            if total_copies <= 0:
                raise ValueError("副本数必须是正整数。")
        except ValueError:
            self._show_error("错误：总副本数必须是有效的正整数。")
            return
        
        try:
            new_book = Book(title=title, author=author, isbn=isbn, 
                            publication_year=publication_year, total_copies=total_copies)
            self.library_instance.add_book(new_book)
            self.library_instance.save_books_to_csv("data/books.csv") 
            
            self.master_app.update_status(f"书籍 '{title}' 添加成功并已保存。", success=True)
            if hasattr(self.master_app, 'switch_view') and callable(getattr(self.master_app, 'switch_view')):
                 self.master_app.switch_view("all_books") 
            self.destroy() 

        except exceptions.BookAlreadyExistsError:
            self._show_error(f"错误：ISBN '{isbn}' 已存在。")
        except exceptions.InvalidCopyNumberError as e:
             self._show_error(f"错误：{e}")
        except Exception as e:
            self._show_error(f"添加书籍时发生未知错误: {e}")
            print(f"Error adding book: {e}")

# Example Usage (for testing AddBookDialog independently) - Kept for now, but may need style updates
# if __name__ == '__main__':
#     # ... (rest of the test code, needs styles integration if run)


class EditBookDialog(ctk.CTkToplevel):
    def __init__(self, master, library_instance, isbn_to_edit):
        super().__init__(master)
        self.master_app = master
        self.library_instance = library_instance
        self.isbn_to_edit = isbn_to_edit
        
        try:
            self.book_to_edit = self.library_instance.find_book_by_isbn(self.isbn_to_edit)
            if not self.book_to_edit: # Should be caught by find_book_by_isbn raising exception
                raise exceptions.BookNotFoundError(f"未找到 ISBN 为 {self.isbn_to_edit} 的书籍。")
        except exceptions.BookNotFoundError as e:
            messagebox.showerror("错误", str(e), parent=self)
            self.after(100, self.destroy) 
            return

        self.title("修改书籍信息")
        self.geometry("450x460") # 修改: 调整尺寸 (比Add略高一点点，因为ISBN是标签)
        self.resizable(False, False)
        self.grab_set()

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=styles.PAD_X_LARGE, pady=styles.PAD_Y_LARGE)
        content_frame.grid_columnconfigure(1, weight=1)

        # --- Input Fields ---
        row_num = 0
        ctk.CTkLabel(content_frame, text="ISBN:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.isbn_label = ctk.CTkLabel(content_frame, text=self.book_to_edit.isbn, font=styles.FONT_NORMAL) 
        self.isbn_label.grid(row=row_num, column=1, padx=0, pady=styles.PAD_Y_MEDIUM, sticky="ew")

        row_num += 1
        ctk.CTkLabel(content_frame, text="书名:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.title_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.title_entry.insert(0, self.book_to_edit.title)
        self.title_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")
        self.title_entry.focus()

        row_num += 1
        ctk.CTkLabel(content_frame, text="作者:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.author_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.author_entry.insert(0, self.book_to_edit.author)
        self.author_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")

        row_num += 1
        ctk.CTkLabel(content_frame, text="出版年份:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.year_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.year_entry.insert(0, str(self.book_to_edit.publication_year))
        self.year_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")

        row_num += 1
        ctk.CTkLabel(content_frame, text="总副本数:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.copies_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.copies_entry.insert(0, str(self.book_to_edit.total_copies))
        self.copies_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")
        
        # --- Error Label ---
        row_num += 1
        self.error_label = ctk.CTkLabel( # 修改: 应用样式
            content_frame, 
            text="", 
            font=styles.FONT_ERROR_TEXT,
            text_color=styles.DANGER_COLOR,
            fg_color=(styles.ERROR_BG_LIGHT, styles.ERROR_BG_DARK),
            corner_radius=styles.CORNER_RADIUS_ERROR_LABEL,
            wraplength=380
        )
        self.error_label.grid(row=row_num, column=0, columnspan=2, pady=(styles.PAD_Y_SMALL, styles.PAD_Y_MEDIUM), padx=0, sticky="ew")
        self.error_label.grid_remove() # Initially hidden

        # --- Buttons ---
        row_num += 1
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.grid(row=row_num, column=0, columnspan=2, pady=(styles.PAD_Y_MEDIUM, 0), sticky="e")

        confirm_button = ctk.CTkButton( # 修改: 应用样式
            button_frame, 
            text="确认修改", 
            command=self.confirm_edit,
            height=styles.HEIGHT_BUTTON,
            corner_radius=styles.CORNER_RADIUS_BUTTON,
            font=styles.FONT_BUTTON,
            fg_color=styles.PRIMARY_COLOR,
            hover_color=styles.PRIMARY_COLOR_HOVER
        )
        confirm_button.pack(side="right", padx=(styles.PAD_X_SMALL, 0))

        cancel_button = ctk.CTkButton( # 修改: 应用样式
            button_frame, 
            text="取消", 
            command=self.destroy,
            height=styles.HEIGHT_BUTTON,
            corner_radius=styles.CORNER_RADIUS_BUTTON,
            font=styles.FONT_BUTTON,
            fg_color=styles.SECONDARY_COLOR,
            hover_color=styles.SECONDARY_COLOR_HOVER
        )
        cancel_button.pack(side="right", padx=(0, styles.PAD_X_SMALL))

    def _show_error(self, message): # Copied from AddBookDialog
        self.error_label.configure(text=message)
        self.error_label.grid()

    def _clear_error(self): # Copied from AddBookDialog
        self.error_label.grid_remove()
        self.error_label.configure(text="")

    def confirm_edit(self):
        self._clear_error()
        new_title = self.title_entry.get().strip()
        new_author = self.author_entry.get().strip()
        year_str = self.year_entry.get().strip()
        copies_str = self.copies_entry.get().strip()

        if not all([new_title, new_author, year_str, copies_str]):
            self._show_error("错误：书名、作者、年份和副本数不能为空。")
            return

        try:
            new_publication_year = int(year_str)
            if new_publication_year <= 0:
                 raise ValueError("出版年份必须是正整数。")
        except ValueError:
            self._show_error("错误：出版年份必须是有效的数字。")
            return

        try:
            new_total_copies = int(copies_str)
            # Backend will validate if new_total_copies < borrowed_copies
        except ValueError:
            self._show_error("错误：总副本数必须是有效的数字。")
            return

        try:
            self.library_instance.modify_book_details(
                isbn=self.isbn_to_edit,
                title=new_title,
                author=new_author,
                publication_year=new_publication_year,
                total_copies=new_total_copies
            )
            self.library_instance.save_books_to_csv("data/books.csv") # Save after modifying
            self.master_app.update_status(f"书籍 '{new_title}' (ISBN: {self.isbn_to_edit}) 修改成功。", success=True)
            if hasattr(self.master_app, 'switch_view') and callable(getattr(self.master_app, 'switch_view')):
                 self.master_app.switch_view("all_books") 
            self.destroy()

        except exceptions.BookNotFoundError: # Should be caught in __init__ but good fallback
            self._show_error(f"错误：尝试修改时未找到书籍 ISBN '{self.isbn_to_edit}'。")
        except ValueError as ve: 
            self._show_error(f"错误：{ve}") # e.g. copies less than borrowed
        except Exception as e:
            self._show_error(f"修改书籍时发生未知错误: {e}")
            print(f"Error editing book: {e}")

if __name__ == '__main__': # Minimal test setup
    class MockMasterApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Dialog Test App")
            # Mock library and styles for testing
            class MockBook:
                def __init__(self, title, author, isbn, publication_year, total_copies):
                    self.title, self.author, self.isbn, self.publication_year, self.total_copies = title, author, isbn, publication_year, total_copies
            class MockLibrary:
                BookNotFoundError = exceptions.BookNotFoundError
                BookAlreadyExistsError = exceptions.BookAlreadyExistsError
                InvalidCopyNumberError = exceptions.InvalidCopyNumberError
                def __init__(self): self.books = {"123": MockBook("Test Book", "Test Author", "123", 2023, 5)}
                def add_book(self, book): 
                    if book.isbn in self.books: raise self.BookAlreadyExistsError()
                    self.books[book.isbn] = book
                def find_book_by_isbn(self, isbn): 
                    b = self.books.get(isbn)
                    if not b: raise self.BookNotFoundError()
                    return b
                def modify_book_details(self, isbn, title, author, publication_year, total_copies):
                     book = self.find_book_by_isbn(isbn) # Raises if not found
                     if total_copies < 0 : raise ValueError("Copies cannot be negative") # Example validation
                     book.title, book.author, book.publication_year, book.total_copies = title, author, publication_year, total_copies
                def save_books_to_csv(self, _path): print("Mock save books")

            self.library_instance = MockLibrary()
            ctk.CTkButton(self, text="Open Add Book", command=lambda: AddBookDialog(self, self.library_instance)).pack(pady=10)
            ctk.CTkButton(self, text="Open Edit Book (ISBN 123)", command=lambda: EditBookDialog(self, self.library_instance, "123")).pack(pady=10)

        def update_status(self, msg, success): print(f"Status: {msg} (Success: {success})")
        def switch_view(self, view): print(f"Switch to: {view}")

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = MockMasterApp()
    app.mainloop()
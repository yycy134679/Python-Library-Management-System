import customtkinter as ctk
from tkinter import messagebox
from src.core_logic import exceptions
from . import styles # 新增

class BorrowBookDialog(ctk.CTkToplevel):
    def __init__(self, master, library_instance):
        super().__init__(master)
        self.master_app = master 
        self.library_instance = library_instance

        self.title("借阅书籍")
        self.geometry("450x330") # 修改: 调整尺寸
        self.resizable(False, False)
        self.grab_set() 

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=styles.PAD_X_LARGE, pady=styles.PAD_Y_LARGE)
        content_frame.grid_columnconfigure(1, weight=1)

        # --- Input Fields ---
        row_num = 0
        ctk.CTkLabel(content_frame, text="书籍ISBN:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.isbn_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.isbn_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")
        self.isbn_entry.focus() 

        row_num += 1
        ctk.CTkLabel(content_frame, text="会员ID:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.member_id_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.member_id_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")
        
        # --- Error Label ---
        row_num += 1
        self.error_label = ctk.CTkLabel(
            content_frame, 
            text="", 
            font=styles.FONT_ERROR_TEXT,
            text_color=styles.DANGER_COLOR,
            fg_color=(styles.ERROR_BG_LIGHT, styles.ERROR_BG_DARK),
            corner_radius=styles.CORNER_RADIUS_ERROR_LABEL,
            wraplength=380
        )
        self.error_label.grid(row=row_num, column=0, columnspan=2, pady=(styles.PAD_Y_SMALL, styles.PAD_Y_MEDIUM), padx=0, sticky="ew")
        self.error_label.grid_remove()

        # --- Buttons ---
        row_num += 1
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.grid(row=row_num, column=0, columnspan=2, pady=(styles.PAD_Y_MEDIUM, 0), sticky="e")

        confirm_button = ctk.CTkButton(
            button_frame, 
            text="确认借阅", 
            command=self.confirm_borrow,
            height=styles.HEIGHT_BUTTON,
            corner_radius=styles.CORNER_RADIUS_BUTTON,
            font=styles.FONT_BUTTON,
            fg_color=styles.PRIMARY_COLOR,
            hover_color=styles.PRIMARY_COLOR_HOVER
        )
        confirm_button.pack(side="right", padx=(styles.PAD_X_SMALL, 0))

        cancel_button = ctk.CTkButton(
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

    def confirm_borrow(self):
        self._clear_error()
        isbn = self.isbn_entry.get().strip()
        member_id = self.member_id_entry.get().strip()

        if not all([isbn, member_id]):
            self._show_error("错误：书籍ISBN和会员ID均为必填项。")
            return
        
        try:
            book = self.library_instance.find_book_by_isbn(isbn) # find_book_by_isbn should raise BookNotFoundError
            member = self.library_instance.find_member_by_id(member_id) # find_member_by_id should raise MemberNotFoundError
            
            self.library_instance.borrow_book_item(isbn, member_id)
            
            self.library_instance.save_books_to_csv("data/books.csv") 
            self.library_instance.save_borrowings_to_csv("data/borrowings.csv") 
            
            self.master_app.update_status(f"会员 '{member.member_name}' 成功借阅《{book.title}》。", success=True)
            if hasattr(self.master_app, 'switch_view') and callable(getattr(self.master_app, 'switch_view')):
                # Refresh book list view if it's the current view to show updated copies
                if hasattr(self.master_app, 'book_list_view_instance') and \
                   self.master_app.main_content_frame.winfo_children() and \
                   self.master_app.book_list_view_instance in self.master_app.main_content_frame.winfo_children():
                    self.master_app.switch_view("all_books")
            self.destroy()
            
        except exceptions.BookNotFoundError:
            self._show_error(f"错误：ISBN为'{isbn}'的书籍不存在。")
        except exceptions.MemberNotFoundError:
            self._show_error(f"错误：ID为'{member_id}'的会员不存在。")
        except exceptions.BookNotAvailableError as e:
            self._show_error(f"错误：{e}")
        except Exception as e:
            self._show_error(f"借阅时发生错误: {e}")
            print(f"Error borrowing book: {e}")


class ReturnBookDialog(ctk.CTkToplevel):
    def __init__(self, master, library_instance):
        super().__init__(master)
        self.master_app = master 
        self.library_instance = library_instance

        self.title("归还书籍")
        self.geometry("450x330") # 修改: 调整尺寸
        self.resizable(False, False)
        self.grab_set() 

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=styles.PAD_X_LARGE, pady=styles.PAD_Y_LARGE)
        content_frame.grid_columnconfigure(1, weight=1)

        # --- Input Fields ---
        row_num = 0
        ctk.CTkLabel(content_frame, text="书籍ISBN:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.isbn_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.isbn_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")
        self.isbn_entry.focus() 

        row_num += 1
        ctk.CTkLabel(content_frame, text="会员ID:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.member_id_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.member_id_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")
        
        # --- Error Label ---
        row_num += 1
        self.error_label = ctk.CTkLabel(
            content_frame, 
            text="", 
            font=styles.FONT_ERROR_TEXT,
            text_color=styles.DANGER_COLOR,
            fg_color=(styles.ERROR_BG_LIGHT, styles.ERROR_BG_DARK),
            corner_radius=styles.CORNER_RADIUS_ERROR_LABEL,
            wraplength=380
        )
        self.error_label.grid(row=row_num, column=0, columnspan=2, pady=(styles.PAD_Y_SMALL, styles.PAD_Y_MEDIUM), padx=0, sticky="ew")
        self.error_label.grid_remove()

        # --- Buttons ---
        row_num += 1
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.grid(row=row_num, column=0, columnspan=2, pady=(styles.PAD_Y_MEDIUM, 0), sticky="e")

        confirm_button = ctk.CTkButton(
            button_frame, 
            text="确认归还", 
            command=self.confirm_return,
            height=styles.HEIGHT_BUTTON,
            corner_radius=styles.CORNER_RADIUS_BUTTON,
            font=styles.FONT_BUTTON,
            fg_color=styles.PRIMARY_COLOR,
            hover_color=styles.PRIMARY_COLOR_HOVER
        )
        confirm_button.pack(side="right", padx=(styles.PAD_X_SMALL, 0))

        cancel_button = ctk.CTkButton(
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

    def confirm_return(self):
        self._clear_error()
        isbn = self.isbn_entry.get().strip()
        member_id = self.member_id_entry.get().strip()

        if not all([isbn, member_id]):
            self._show_error("错误：书籍ISBN和会员ID均为必填项。")
            return
        
        try:
            book = self.library_instance.find_book_by_isbn(isbn)
            member = self.library_instance.find_member_by_id(member_id)
            
            self.library_instance.return_book_item(isbn, member_id)
            
            self.library_instance.save_books_to_csv("data/books.csv") 
            self.library_instance.save_borrowings_to_csv("data/borrowings.csv") 
            
            self.master_app.update_status(f"会员 '{member.member_name}' 成功归还《{book.title}》。", success=True)
            if hasattr(self.master_app, 'switch_view') and callable(getattr(self.master_app, 'switch_view')):
                if hasattr(self.master_app, 'book_list_view_instance') and \
                   self.master_app.main_content_frame.winfo_children() and \
                   self.master_app.book_list_view_instance in self.master_app.main_content_frame.winfo_children():
                    self.master_app.switch_view("all_books")
            self.destroy()
            
        except exceptions.BookNotFoundError:
            self._show_error(f"错误：ISBN为'{isbn}'的书籍不存在。")
        except exceptions.MemberNotFoundError:
            self._show_error(f"错误：ID为'{member_id}'的会员不存在。")
        except exceptions.BookNotBorrowedError as e:
            self._show_error(f"错误：{e}")
        except Exception as e:
            self._show_error(f"归还时发生错误: {e}")
            print(f"Error returning book: {e}")

if __name__ == '__main__': # Minimal test setup
    class MockMasterApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Borrow/Return Dialog Test App")
            # Mock library and styles for testing
            class MockBook:
                def __init__(self, title, isbn, available_copies=1): self.title, self.isbn, self.available_copies = title, isbn, available_copies
            class MockMember:
                def __init__(self, member_id, member_name): self.member_id, self.member_name, self.borrowed_books = member_id, member_name, []
                def borrow_book(self, book): self.borrowed_books.append(book)
                def return_book(self, book): 
                    if book in self.borrowed_books: self.borrowed_books.remove(book)
                    else: raise exceptions.BookNotBorrowedError("Not borrowed by member")
            class MockLibrary:
                BookNotFoundError, MemberNotFoundError = exceptions.BookNotFoundError, exceptions.MemberNotFoundError
                BookNotAvailableError, BookNotBorrowedError = exceptions.BookNotAvailableError, exceptions.BookNotBorrowedError
                def __init__(self):
                    self.books = {"B001": MockBook("Book One", "B001"), "B002": MockBook("Book Two", "B002", 0)}
                    self.members = {"M001": MockMember("M001", "Member One")}
                def find_book_by_isbn(self, isbn): 
                    b = self.books.get(isbn)
                    if not b: raise self.BookNotFoundError()
                    return b
                def find_member_by_id(self, member_id):
                    m = self.members.get(member_id)
                    if not m: raise self.MemberNotFoundError()
                    return m
                def borrow_book_item(self, isbn, member_id):
                    book, member = self.find_book_by_isbn(isbn), self.find_member_by_id(member_id)
                    if book.available_copies <= 0: raise self.BookNotAvailableError()
                    book.available_copies -= 1
                    member.borrow_book(book)
                def return_book_item(self, isbn, member_id):
                    book, member = self.find_book_by_isbn(isbn), self.find_member_by_id(member_id)
                    # Simplified: assume book object equality works for borrowed_books list
                    if not any(b.isbn == book.isbn for b in member.borrowed_books): raise self.BookNotBorrowedError()
                    book.available_copies += 1
                    member.borrowed_books = [b for b in member.borrowed_books if b.isbn != book.isbn]

                def save_books_to_csv(self, _p): print("Mock save books")
                def save_borrowings_to_csv(self, _p): print("Mock save borrowings")

            self.library_instance = MockLibrary()
            ctk.CTkButton(self, text="Open Borrow Dialog", command=lambda: BorrowBookDialog(self, self.library_instance)).pack(pady=10)
            ctk.CTkButton(self, text="Open Return Dialog", command=lambda: ReturnBookDialog(self, self.library_instance)).pack(pady=10)

        def update_status(self, msg, success): print(f"Status: {msg} (Success: {success})")
        def switch_view(self, view): print(f"Switch to: {view}")

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = MockMasterApp()
    app.mainloop()
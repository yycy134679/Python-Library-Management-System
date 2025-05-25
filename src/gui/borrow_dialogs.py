import customtkinter as ctk
from tkinter import messagebox
from src.core_logic import exceptions

class BorrowBookDialog(ctk.CTkToplevel):
    def __init__(self, master, library_instance):
        super().__init__(master)
        self.master_app = master # Reference to the main LibraryApp instance
        self.library_instance = library_instance

        self.title("借阅书籍")
        self.geometry("400x300")
        self.resizable(False, False)
        self.grab_set() # Make dialog modal

        self.grid_columnconfigure(1, weight=1)

        # --- Input Fields ---
        row_num = 0
        ctk.CTkLabel(self, text="书籍ISBN:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.isbn_entry = ctk.CTkEntry(self, width=200)
        self.isbn_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")
        self.isbn_entry.focus() # Set focus to ISBN entry initially

        row_num += 1
        ctk.CTkLabel(self, text="会员ID:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.member_id_entry = ctk.CTkEntry(self, width=200)
        self.member_id_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")
        
        # --- Error Label ---
        row_num += 1
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.grid(row=row_num, column=0, columnspan=2, padx=10, pady=(0,5), sticky="ew")

        # --- Buttons ---
        row_num += 1
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=row_num, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        button_frame.grid_columnconfigure((0,1), weight=1) # Center buttons

        confirm_button = ctk.CTkButton(button_frame, text="确认借阅", command=self.confirm_borrow)
        confirm_button.grid(row=0, column=0, padx=(0,5), pady=5, sticky="e")

        cancel_button = ctk.CTkButton(button_frame, text="取消", command=self.destroy, fg_color="gray")
        cancel_button.grid(row=0, column=1, padx=(5,0), pady=5, sticky="w")

    def confirm_borrow(self):
        self.error_label.configure(text="") # Clear previous errors
        isbn = self.isbn_entry.get().strip()
        member_id = self.member_id_entry.get().strip()

        # --- Frontend Validation ---
        if not all([isbn, member_id]):
            self.error_label.configure(text="错误：书籍ISBN和会员ID均为必填项。")
            return
        
        try:
            # 前端验证书籍和会员是否存在
            try:
                book = self.library_instance.find_book_by_isbn(isbn)
                member = self.library_instance.find_member_by_id(member_id)
            except exceptions.BookNotFoundError:
                self.error_label.configure(text=f"错误：ISBN为'{isbn}'的书籍不存在。")
                return
            except exceptions.MemberNotFoundError:
                self.error_label.configure(text=f"错误：ID为'{member_id}'的会员不存在。")
                return
            
            # 执行借阅操作
            self.library_instance.borrow_book_item(isbn, member_id)
            
            # 保存数据
            self.library_instance.save_books_to_csv("data/books.csv") # Keep this to save available_copies
            self.library_instance.save_borrowings_to_csv("data/borrowings.csv") # Add this to save new borrowing record
            
            # 更新状态并关闭对话框
            self.master_app.update_status(f"会员 '{member.member_name}' 成功借阅《{book.title}》。", success=True)
            self.destroy()
            
        except exceptions.BookNotAvailableError as e:
            self.error_label.configure(text=f"错误：{e}")
        except Exception as e:
            self.error_label.configure(text=f"借阅时发生错误: {e}")
            print(f"Error borrowing book: {e}")


class ReturnBookDialog(ctk.CTkToplevel):
    def __init__(self, master, library_instance):
        super().__init__(master)
        self.master_app = master # Reference to the main LibraryApp instance
        self.library_instance = library_instance

        self.title("归还书籍")
        self.geometry("400x300")
        self.resizable(False, False)
        self.grab_set() # Make dialog modal

        self.grid_columnconfigure(1, weight=1)

        # --- Input Fields ---
        row_num = 0
        ctk.CTkLabel(self, text="书籍ISBN:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.isbn_entry = ctk.CTkEntry(self, width=200)
        self.isbn_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")
        self.isbn_entry.focus() # Set focus to ISBN entry initially

        row_num += 1
        ctk.CTkLabel(self, text="会员ID:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.member_id_entry = ctk.CTkEntry(self, width=200)
        self.member_id_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")
        
        # --- Error Label ---
        row_num += 1
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.grid(row=row_num, column=0, columnspan=2, padx=10, pady=(0,5), sticky="ew")

        # --- Buttons ---
        row_num += 1
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=row_num, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        button_frame.grid_columnconfigure((0,1), weight=1) # Center buttons

        confirm_button = ctk.CTkButton(button_frame, text="确认归还", command=self.confirm_return)
        confirm_button.grid(row=0, column=0, padx=(0,5), pady=5, sticky="e")

        cancel_button = ctk.CTkButton(button_frame, text="取消", command=self.destroy, fg_color="gray")
        cancel_button.grid(row=0, column=1, padx=(5,0), pady=5, sticky="w")

    def confirm_return(self):
        self.error_label.configure(text="") # Clear previous errors
        isbn = self.isbn_entry.get().strip()
        member_id = self.member_id_entry.get().strip()

        # --- Frontend Validation ---
        if not all([isbn, member_id]):
            self.error_label.configure(text="错误：书籍ISBN和会员ID均为必填项。")
            return
        
        try:
            # 前端验证书籍和会员是否存在
            try:
                book = self.library_instance.find_book_by_isbn(isbn)
                member = self.library_instance.find_member_by_id(member_id)
            except exceptions.BookNotFoundError:
                self.error_label.configure(text=f"错误：ISBN为'{isbn}'的书籍不存在。")
                return
            except exceptions.MemberNotFoundError:
                self.error_label.configure(text=f"错误：ID为'{member_id}'的会员不存在。")
                return
            
            # 执行归还操作
            self.library_instance.return_book_item(isbn, member_id)
            
            # 保存数据
            self.library_instance.save_books_to_csv("data/books.csv") # Keep this to save available_copies
            self.library_instance.save_borrowings_to_csv("data/borrowings.csv") # Add this to save updated borrowing record
            
            # 更新状态并关闭对话框
            self.master_app.update_status(f"会员 '{member.member_name}' 成功归还《{book.title}》。", success=True)
            self.destroy()
            
        except exceptions.BookNotBorrowedError as e:
            self.error_label.configure(text=f"错误：{e}")
        except Exception as e:
            self.error_label.configure(text=f"归还时发生错误: {e}")
            print(f"Error returning book: {e}")


# Example Usage (for testing dialogs independently)
if __name__ == '__main__':
    class MockLibraryApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Borrow/Return Dialog Test Host")
            self.geometry("300x200")

            class MockBook:
                def __init__(self, title, isbn):
                    self.title = title
                    self.isbn = isbn
                    self.available_copies = 1
            
            class MockMember:
                def __init__(self, member_id, member_name):
                    self.member_id = member_id
                    self.member_name = member_name
                    self.borrowed_books = []
                
                def borrow_book(self, book):
                    self.borrowed_books.append(book)
                
                def return_book(self, book):
                    if book in self.borrowed_books:
                        self.borrowed_books.remove(book)
                    else:
                        raise exceptions.BookNotBorrowedError(f"会员未借阅该书籍")

            class MockLibrary:
                def __init__(self):
                    self.book1 = MockBook("Python编程", "ISBN001")
                    self.book2 = MockBook("Java编程", "ISBN002")
                    self.member1 = MockMember("M001", "张三")
                    self.member2 = MockMember("M002", "李四")
                    
                    self.books = {"ISBN001": self.book1, "ISBN002": self.book2}
                    self.members = {"M001": self.member1, "M002": self.member2}
                
                def find_book_by_isbn(self, isbn):
                    if isbn in self.books:
                        return self.books[isbn]
                    raise exceptions.BookNotFoundError(f"ISBN为'{isbn}'的书籍未找到")
                
                def find_member_by_id(self, member_id):
                    if member_id in self.members:
                        return self.members[member_id]
                    raise exceptions.MemberNotFoundError(f"ID为'{member_id}'的会员未找到")
                
                def borrow_book_item(self, isbn, member_id):
                    book = self.find_book_by_isbn(isbn)
                    member = self.find_member_by_id(member_id)
                    if book.available_copies > 0:
                        book.available_copies -= 1
                        member.borrow_book(book)
                        return True
                    else:
                        raise exceptions.BookNotAvailableError(f"《{book.title}》当前没有可借阅的副本")
                
                def return_book_item(self, isbn, member_id):
                    book = self.find_book_by_isbn(isbn)
                    member = self.find_member_by_id(member_id)
                    if book in member.borrowed_books:
                        book.available_copies += 1
                        member.return_book(book)
                        return True
                    else:
                        raise exceptions.BookNotBorrowedError(f"会员'{member.member_name}'未借阅《{book.title}》")
                
                def save_books_to_csv(self, filename):
                    print(f"Mock: Saving books to {filename}")

            self.library_instance = MockLibrary()
            
            borrow_button = ctk.CTkButton(self, text="Open Borrow Dialog", command=self.open_borrow_dialog)
            borrow_button.pack(pady=10)
            
            return_button = ctk.CTkButton(self, text="Open Return Dialog", command=self.open_return_dialog)
            return_button.pack(pady=10)

        def open_borrow_dialog(self):
            dialog = BorrowBookDialog(self, self.library_instance)

        def open_return_dialog(self):
            dialog = ReturnBookDialog(self, self.library_instance)

        def update_status(self, message, success=True):
            print(f"Status Update: {message} (Success: {success})")

    app = MockLibraryApp()
    app.mainloop()
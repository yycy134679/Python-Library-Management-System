import customtkinter as ctk
from tkinter import messagebox
from src.core_logic.book import Book
from src.core_logic import exceptions

class AddBookDialog(ctk.CTkToplevel):
    def __init__(self, master, library_instance):
        super().__init__(master)
        self.master_app = master # Reference to the main LibraryApp instance
        self.library_instance = library_instance

        self.title("添加新书籍")
        self.geometry("450x400") # Adjusted size
        self.resizable(False, False)
        self.grab_set() # Make dialog modal

        self.grid_columnconfigure(1, weight=1)

        # --- Input Fields ---
        row_num = 0
        ctk.CTkLabel(self, text="ISBN:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.isbn_entry = ctk.CTkEntry(self, width=250)
        self.isbn_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")
        self.isbn_entry.focus() # Set focus to ISBN entry initially

        row_num += 1
        ctk.CTkLabel(self, text="书名:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.title_entry = ctk.CTkEntry(self, width=250)
        self.title_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")

        row_num += 1
        ctk.CTkLabel(self, text="作者:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.author_entry = ctk.CTkEntry(self, width=250)
        self.author_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")

        row_num += 1
        ctk.CTkLabel(self, text="出版年份:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.year_entry = ctk.CTkEntry(self, width=250)
        self.year_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")

        row_num += 1
        ctk.CTkLabel(self, text="总副本数:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.copies_entry = ctk.CTkEntry(self, width=250)
        self.copies_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")
        
        # --- Error Label ---
        row_num += 1
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.grid(row=row_num, column=0, columnspan=2, padx=10, pady=(0,5), sticky="ew")


        # --- Buttons ---
        row_num += 1
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=row_num, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        button_frame.grid_columnconfigure((0,1), weight=1) # Center buttons

        confirm_button = ctk.CTkButton(button_frame, text="确认添加", command=self.confirm_add)
        confirm_button.grid(row=0, column=0, padx=(0,5), pady=5, sticky="e")

        cancel_button = ctk.CTkButton(button_frame, text="取消", command=self.destroy, fg_color="gray")
        cancel_button.grid(row=0, column=1, padx=(5,0), pady=5, sticky="w")

    def confirm_add(self):
        self.error_label.configure(text="") # Clear previous errors
        isbn = self.isbn_entry.get().strip()
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        year_str = self.year_entry.get().strip()
        copies_str = self.copies_entry.get().strip()

        # --- Frontend Validation ---
        if not all([isbn, title, author, year_str, copies_str]):
            self.error_label.configure(text="错误：所有字段均为必填项。")
            return

        try:
            publication_year = int(year_str)
            if publication_year <= 0: # Basic year validation
                 raise ValueError("出版年份必须是正整数。")
        except ValueError:
            self.error_label.configure(text="错误：出版年份必须是有效的数字。")
            return

        try:
            total_copies = int(copies_str)
            if total_copies <= 0:
                raise ValueError("副本数必须是正整数。")
        except ValueError:
            self.error_label.configure(text="错误：总副本数必须是有效的正整数。")
            return
        
        # ISBN uniqueness is typically checked by the backend, but a frontend check can be added if needed.

        try:
            new_book = Book(title=title, author=author, isbn=isbn, 
                            publication_year=publication_year, total_copies=total_copies)
            self.library_instance.add_book(new_book)
            self.library_instance.save_books_to_csv("data/books.csv") # Save after adding
            
            self.master_app.update_status(f"书籍 '{title}' 添加成功并已保存。", success=True)
            self.master_app.switch_view("all_books") # Refresh the book list
            self.destroy() # Close dialog

        except exceptions.BookAlreadyExistsError:
            self.error_label.configure(text=f"错误：ISBN '{isbn}' 已存在。")
        except exceptions.InvalidCopyNumberError as e:
             self.error_label.configure(text=f"错误：{e}")
        except Exception as e:
            self.error_label.configure(text=f"添加书籍时发生未知错误: {e}")
            # For debugging, you might want to print the full traceback
            print(f"Error adding book: {e}")

# Example Usage (for testing AddBookDialog independently)
if __name__ == '__main__':
    class MockLibraryApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Dialog Test Host")
            self.geometry("300x200")

            class MockLibrary:
                def __init__(self):
                    self.books = []
                def add_book(self, book):
                    for b in self.books:
                        if b.isbn == book.isbn:
                            raise exceptions.BookAlreadyExistsError(f"ISBN {book.isbn} already exists.")
                    if book.total_copies <=0:
                        raise exceptions.InvalidCopyNumberError("Copies must be > 0")
                    self.books.append(book)
                    print(f"MockLibrary: Book '{book.title}' added. Total books: {len(self.books)}")
                
                def get_all_books(self):
                    return self.books

            self.library_instance = MockLibrary()
            
            button = ctk.CTkButton(self, text="Open Add Book Dialog", command=self.open_dialog)
            button.pack(pady=20)

        def open_dialog(self):
            dialog = AddBookDialog(self, self.library_instance)
            # dialog.grab_set() # Already done in AddBookDialog __init__

        def update_status(self, message, success=True):
            print(f"Host Status: {message} (Success: {success})")

        def switch_view(self, view_name):
            print(f"Host: Switch to view '{view_name}' requested.")
            if view_name == "all_books":
                print("Books in mock library:")
                for book in self.library_instance.get_all_books():
                    print(f"  - {book.isbn}: {book.title}")


    app = MockLibraryApp()
    app.mainloop()


class EditBookDialog(ctk.CTkToplevel):
    def __init__(self, master, library_instance, isbn_to_edit):
        super().__init__(master)
        self.master_app = master
        self.library_instance = library_instance
        self.isbn_to_edit = isbn_to_edit
        self.book_to_edit = self.library_instance.find_book_by_isbn(self.isbn_to_edit)

        self.title("修改书籍信息")
        self.geometry("450x430") # Slightly taller for read-only ISBN
        self.resizable(False, False)
        self.grab_set()

        if not self.book_to_edit:
            messagebox.showerror("错误", f"未找到 ISBN 为 {self.isbn_to_edit} 的书籍。", parent=self)
            self.after(100, self.destroy) # Destroy after error dialog
            return

        self.grid_columnconfigure(1, weight=1)

        # --- Input Fields ---
        row_num = 0
        ctk.CTkLabel(self, text="ISBN:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.isbn_label = ctk.CTkLabel(self, text=self.book_to_edit.isbn) # Display as label, not entry
        self.isbn_label.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")

        row_num += 1
        ctk.CTkLabel(self, text="书名:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.title_entry = ctk.CTkEntry(self, width=250)
        self.title_entry.insert(0, self.book_to_edit.title)
        self.title_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")
        self.title_entry.focus()

        row_num += 1
        ctk.CTkLabel(self, text="作者:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.author_entry = ctk.CTkEntry(self, width=250)
        self.author_entry.insert(0, self.book_to_edit.author)
        self.author_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")

        row_num += 1
        ctk.CTkLabel(self, text="出版年份:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.year_entry = ctk.CTkEntry(self, width=250)
        self.year_entry.insert(0, str(self.book_to_edit.publication_year))
        self.year_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")

        row_num += 1
        ctk.CTkLabel(self, text="总副本数:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.copies_entry = ctk.CTkEntry(self, width=250)
        self.copies_entry.insert(0, str(self.book_to_edit.total_copies))
        self.copies_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")
        
        # --- Error Label ---
        row_num += 1
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.grid(row=row_num, column=0, columnspan=2, padx=10, pady=(0,5), sticky="ew")

        # --- Buttons ---
        row_num += 1
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=row_num, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        button_frame.grid_columnconfigure((0,1), weight=1)

        confirm_button = ctk.CTkButton(button_frame, text="确认修改", command=self.confirm_edit)
        confirm_button.grid(row=0, column=0, padx=(0,5), pady=5, sticky="e")

        cancel_button = ctk.CTkButton(button_frame, text="取消", command=self.destroy, fg_color="gray")
        cancel_button.grid(row=0, column=1, padx=(5,0), pady=5, sticky="w")

    def confirm_edit(self):
        self.error_label.configure(text="")
        new_title = self.title_entry.get().strip()
        new_author = self.author_entry.get().strip()
        year_str = self.year_entry.get().strip()
        copies_str = self.copies_entry.get().strip()

        if not all([new_title, new_author, year_str, copies_str]):
            self.error_label.configure(text="错误：书名、作者、年份和副本数不能为空。")
            return

        try:
            new_publication_year = int(year_str)
            if new_publication_year <= 0:
                 raise ValueError("出版年份必须是正整数。")
        except ValueError:
            self.error_label.configure(text="错误：出版年份必须是有效的数字。")
            return

        try:
            new_total_copies = int(copies_str)
            # Validation for total_copies (e.g., non-negative) is handled by Book.update_book_info or library.modify_book_details
        except ValueError:
            self.error_label.configure(text="错误：总副本数必须是有效的数字。")
            return

        try:
            # Note: modify_book_details in library.py is expected to handle
            # cases like new_total_copies < currently borrowed copies.
            self.library_instance.modify_book_details(
                isbn=self.isbn_to_edit,
                title=new_title,
                author=new_author,
                publication_year=new_publication_year,
                total_copies=new_total_copies
            )
            self.master_app.update_status(f"书籍 '{new_title}' (ISBN: {self.isbn_to_edit}) 修改成功。", success=True)
            self.master_app.switch_view("all_books") # Refresh list
            self.destroy()

        except exceptions.BookNotFoundError:
            self.error_label.configure(text=f"错误：尝试修改时未找到书籍 ISBN '{self.isbn_to_edit}'。")
        except ValueError as ve: # Catch specific ValueErrors from backend if any
            self.error_label.configure(text=f"错误：{ve}")
        except Exception as e:
            self.error_label.configure(text=f"修改书籍时发生未知错误: {e}")
            print(f"Error editing book: {e}")
import customtkinter
import tkinter # 导入 tkinter

from src.core_logic.library import Library
from src.core_logic.book import Book
from src.core_logic.library_member import LibraryMember
from src.core_logic import exceptions
from .book_view import BookListView
from .book_dialogs import AddBookDialog as AddBookDialogCtl, EditBookDialog as EditBookDialogCtl # Renamed to avoid conflict
from .member_view import MemberListView
from .member_dialogs import AddMemberDialog, EditMemberDialog # Added EditMemberDialog import

class LibraryApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("图书馆管理系统")
        self.geometry("900x700") # 设置窗口大小
        self.library_handler = Library()

        # --- 状态栏 --- (提前初始化)
        self.status_bar = customtkinter.CTkLabel(self, text="正在初始化...", anchor="w")
        self.status_bar.pack(side="bottom", fill="x", padx=5, pady=5)

        try:
            self.library_handler.load_books_from_csv("data/books.csv")
            self.library_handler.load_members_from_csv("data/members.csv")
            self.update_status("数据加载成功。", success=True)
        except FileNotFoundError as e:
            self.update_status(f"错误：数据文件未找到 ({e.filename})。请确保 data 文件夹下有相应文件。", success=False)
        except Exception as e:
            self.update_status(f"加载数据时发生错误: {e}", success=False)

        # --- 菜单栏 ---
        self.menu_bar = tkinter.Menu(self)
        self.config(menu=self.menu_bar)

        # --- 文件菜单 ---
        file_menu = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="退出", command=self.quit_application)

        # --- 书籍管理菜单 ---
        book_menu = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="书籍管理", menu=book_menu)
        book_menu.add_command(label="添加书籍", command=self.open_add_book_dialog)
        book_menu.add_command(label="显示所有书籍", command=lambda: self.switch_view("all_books"))
        book_menu.add_command(label="查找书籍", command=self.activate_book_search)

        # --- 会员管理菜单 ---
        member_menu = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="会员管理", menu=member_menu)
        member_menu.add_command(label="添加会员", command=self.open_add_member_dialog) # Correct: this will call the new method
        member_menu.add_command(label="显示所有会员", command=lambda: self.switch_view("all_members"))
        member_menu.add_command(label="查找会员", command=self.activate_member_search)

        # --- 借阅管理菜单 ---
        borrow_menu = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="借阅管理", menu=borrow_menu)
        borrow_menu.add_command(label="借阅书籍", command=self.placeholder_command)
        borrow_menu.add_command(label="归还书籍", command=self.placeholder_command)

        # --- 工具栏 ---
        self.toolbar_frame = customtkinter.CTkFrame(self, height=50)
        self.toolbar_frame.pack(side="top", fill="x", padx=5, pady=5) # 添加一些边距

        # --- 工具栏按钮 ---
        btn_add_book = customtkinter.CTkButton(self.toolbar_frame, text="添加书籍", command=self.open_add_book_dialog) # Uses AddBookDialogCtl
        btn_add_book.pack(side="left", padx=5, pady=5)

        btn_add_member = customtkinter.CTkButton(self.toolbar_frame, text="添加会员", command=self.open_add_member_dialog) # Correct: this will call the new method
        btn_add_member.pack(side="left", padx=5, pady=5)

        btn_borrow_book = customtkinter.CTkButton(self.toolbar_frame, text="借阅书籍", command=self.placeholder_command)
        btn_borrow_book.pack(side="left", padx=5, pady=5)

        btn_return_book = customtkinter.CTkButton(self.toolbar_frame, text="归还书籍", command=self.placeholder_command)
        btn_return_book.pack(side="left", padx=5, pady=5)

        btn_show_all_books = customtkinter.CTkButton(self.toolbar_frame, text="所有书籍", command=lambda: self.switch_view("all_books"))
        btn_show_all_books.pack(side="left", padx=5, pady=5)

        btn_show_all_members = customtkinter.CTkButton(self.toolbar_frame, text="所有会员", command=lambda: self.switch_view("all_members"))
        btn_show_all_members.pack(side="left", padx=5, pady=5)


        # --- 主内容区 ---
        self.main_content_frame = customtkinter.CTkFrame(self)
        self.main_content_frame.pack(side="top", fill="both", expand=True, padx=5, pady=0) # pady 调整为0，避免和状态栏重叠太多

        # 初始视图
        self.switch_view("welcome")


    def quit_application(self):
        try:
            self.library_handler.save_books_to_csv("data/books.csv")
            self.library_handler.save_members_to_csv("data/members.csv")
        except Exception as e:
            import tkinter.messagebox
            tkinter.messagebox.showerror("保存错误", f"保存数据时发生错误: {e}")
        self.destroy()

    def placeholder_command(self):
        self.update_status("功能暂未实现", success=False)
        print("命令占位符被调用")

    def update_status(self, message, success=True):
        self.status_bar.configure(text=message)
        if success:
            self.status_bar.configure(text_color="green")
        else:
            self.status_bar.configure(text_color="red")

    def switch_view(self, view_name, *args):
        # 清空主内容区
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

        if view_name == "welcome":
            self.show_welcome_view()
        elif view_name == "all_books":
            self.show_all_books_view()
        elif view_name == "all_members": # Added case for all_members view
            self.show_all_members_view()
        # elif view_name == "add_book_form": # Removed as we use a dialog now
        #     self.show_add_book_form_view()
        # 可以根据需要添加更多视图
        else:
            self.show_welcome_view() # 默认或未知视图显示欢迎页

    def show_welcome_view(self):
        welcome_label = customtkinter.CTkLabel(self.main_content_frame, text="欢迎来到图书馆管理系统！", font=customtkinter.CTkFont(size=20, weight="bold"))
        welcome_label.pack(pady=20, padx=20, anchor="center")
        self.update_status("欢迎使用图书馆管理系统")

    def show_all_books_view(self):
        # Clear existing widgets in main_content_frame (already done by switch_view)
        
        # self.library_handler.books is a dictionary, we need its values (Book objects)
        all_books_data = list(self.library_handler.books.values())
        
        if hasattr(self, 'book_list_view_instance') and self.book_list_view_instance.winfo_exists():
            self.book_list_view_instance.destroy()

        self.book_list_view_instance = BookListView(self.main_content_frame,
                                                    library_instance=self.library_handler,
                                                    master_app=self)
        self.book_list_view_instance.pack(fill="both", expand=True, padx=5, pady=5)
        self.book_list_view_instance.populate_table(all_books_data)
        
        self.update_status(f"已显示 {len(all_books_data) if all_books_data else 0} 本书籍。", success=True)

    # def show_add_book_form_view(self): # Removed as we use a dialog now
    #     # 占位符：后续实现添加书籍表单的视图
    #     label = customtkinter.CTkLabel(self.main_content_frame, text="添加书籍表单（待实现）", font=customtkinter.CTkFont(size=16))
    #     label.pack(pady=20, padx=20, anchor="center")
    #     self.update_status("准备添加新书")

    def open_add_book_dialog(self): # This is for Books, should use AddBookDialogCtl
        dialog = AddBookDialogCtl(master=self, library_instance=self.library_handler)
        # The dialog handles grab_set itself
    
    def open_add_member_dialog(self): # This is for Members, should use AddMemberDialog
        dialog = AddMemberDialog(master=self, library_instance=self.library_handler)
        # The dialog handles grab_set itself

    def activate_book_search(self):
        """Switches to the book list view and focuses the search bar."""
        self.switch_view("all_books")
        # Ensure book_list_view_instance and its search_entry exist before focusing
        if hasattr(self, 'book_list_view_instance') and \
           self.book_list_view_instance.winfo_exists() and \
           hasattr(self.book_list_view_instance, 'search_entry'):
            self.book_list_view_instance.search_entry.focus()
            self.update_status("准备查找书籍，请输入搜索条件。", success=True)
        else:
            self.update_status("无法激活书籍搜索功能。", success=False)

    def show_all_members_view(self):
        """Displays the list of all members."""
        all_members_data = list(self.library_handler.members.values())

        if hasattr(self, 'member_list_view_instance') and self.member_list_view_instance.winfo_exists():
            self.member_list_view_instance.destroy()

        self.member_list_view_instance = MemberListView(
            self.main_content_frame,
            library_instance=self.library_handler,
            master_app=self
        )
        self.member_list_view_instance.pack(fill="both", expand=True, padx=5, pady=5)
        self.member_list_view_instance.populate_table(all_members_data)
        
        self.update_status(f"已显示 {len(all_members_data) if all_members_data else 0} 位会员。", success=True)

    # activate_member_search method should already be present from the previous read.
    # If it was not fully applied or was overwritten, this ensures it's correct.
    # If it is already correct, this part of the diff won't change anything.
    def activate_member_search(self):
        """Switches to the member list view and focuses the search bar."""
        self.switch_view("all_members")
        if hasattr(self, 'member_list_view_instance') and \
           self.member_list_view_instance.winfo_exists() and \
           hasattr(self.member_list_view_instance, 'search_entry'):
            self.member_list_view_instance.search_entry.focus()
            self.update_status("准备查找会员，请输入会员ID。", success=True)
        else:
            self.update_status("无法激活会员搜索功能。", success=False)


    # --- Callbacks for BookListView ---
    def open_edit_book_dialog(self, isbn):
        """Opens the edit book dialog for the given ISBN."""
        dialog = EditBookDialog(master=self, library_instance=self.library_handler, isbn_to_edit=isbn)
        # The dialog handles grab_set itself
        # No need to print here as dialog will show.
        # self.update_status(f"正在修改书籍 ISBN: {isbn}", success=True) # Status update can be handled by dialog if needed

    def confirm_delete_book(self, isbn):
        """Confirms and deletes a book with the given ISBN."""
        book_to_delete = self.library_handler.find_book_by_isbn(isbn)
        if not book_to_delete:
            self.update_status(f"错误：尝试删除时未找到 ISBN 为 {isbn} 的书籍。", success=False)
            tkinter.messagebox.showerror("删除错误", f"未找到 ISBN 为 {isbn} 的书籍。", parent=self)
            return

        confirm_message = f"您确定要删除书籍 '{book_to_delete.title}' (ISBN: {isbn}) 吗？"
        if tkinter.messagebox.askyesno("确认删除", confirm_message, parent=self):
            try:
                self.library_handler.remove_book(isbn)
                self.library_handler.save_books_to_csv("data/books.csv") # Save after deleting
                self.update_status(f"书籍 '{book_to_delete.title}' (ISBN: {isbn}) 删除成功并已保存。", success=True)
                self.switch_view("all_books") # Refresh the book list
            except exceptions.BookNotFoundError:
                # This case should ideally be caught by the check above, but good to have as a fallback.
                self.update_status(f"错误：删除时未找到 ISBN 为 {isbn} 的书籍。", success=False)
                tkinter.messagebox.showerror("删除错误", f"删除时未找到 ISBN 为 {isbn} 的书籍。", parent=self)
            except Exception as e:
                self.update_status(f"删除书籍 '{book_to_delete.title}' 时发生错误: {e}", success=False)
                tkinter.messagebox.showerror("删除错误", f"删除书籍时发生未知错误: {e}", parent=self)
        else:
            self.update_status(f"取消删除书籍 ISBN: {isbn}", success=True)

    # --- Callbacks for MemberListView ---
    def open_edit_member_dialog(self, member_id):
        """Opens the edit member dialog for the given member ID."""
        dialog = EditMemberDialog(master=self, library_instance=self.library_handler, member_id_to_edit=member_id)
        # The dialog handles grab_set itself

    def confirm_delete_member(self, member_id):
        """Confirms and deletes a member with the given ID."""
        member_to_delete = self.library_handler.find_member_by_id(member_id) # Find to get name for confirm message
        if not member_to_delete:
            self.update_status(f"错误：尝试删除时未找到会员ID为 {member_id} 的会员。", success=False)
            tkinter.messagebox.showerror("删除错误", f"未找到会员ID为 {member_id} 的会员。", parent=self)
            return

        confirm_message = f"您确定要删除会员 '{member_to_delete.member_name}' (ID: {member_id}) 吗？"
        if tkinter.messagebox.askyesno("确认删除", confirm_message, parent=self):
            try:
                self.library_handler.remove_member(member_id)
                self.library_handler.save_members_to_csv("data/members.csv") # Save after deleting
                self.update_status(f"会员 '{member_to_delete.member_name}' (ID: {member_id}) 删除成功并已保存。", success=True)
                self.switch_view("all_members") # Refresh the member list
            except exceptions.MemberNotFoundError:
                self.update_status(f"错误：删除时未找到会员ID为 {member_id} 的会员。", success=False)
                tkinter.messagebox.showerror("删除错误", f"删除时未找到会员ID为 {member_id} 的会员。", parent=self)
            except Exception as e:
                self.update_status(f"删除会员 '{member_to_delete.member_name}' 时发生错误: {e}", success=False)
                tkinter.messagebox.showerror("删除错误", f"删除会员时发生未知错误: {e}", parent=self)
        else:
            self.update_status(f"取消删除会员 ID: {member_id}", success=True)


if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()
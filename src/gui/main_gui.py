import customtkinter
import tkinter # 导入 tkinter

# 导入样式常量
from . import styles # 新增

from src.core_logic.library import Library
from src.core_logic.book import Book
from src.core_logic.library_member import LibraryMember
from src.core_logic import exceptions
from .book_view import BookListView
from .book_dialogs import AddBookDialog as AddBookDialogCtl, EditBookDialog as EditBookDialogCtl # Renamed to avoid conflict
from .member_view import MemberListView
from .member_dialogs import AddMemberDialog, EditMemberDialog
from .borrow_dialogs import BorrowBookDialog, ReturnBookDialog # 导入借阅和归还对话框

class LibraryApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        styles.initialize_fonts() # 新增: 初始化字体
        self.title("图书馆管理系统")
        self.geometry("960x720") # 修改: 调整窗口大小
        self.library_handler = Library()

        self._apply_styles() # 新增: 应用全局样式

        # --- 状态栏 --- (提前初始化)
        self.status_bar = customtkinter.CTkLabel( # 修改: 应用样式
            self, 
            text="正在初始化...", 
            anchor="w",
            font=styles.FONT_STATUS_BAR,
            height=25 
        )
        self.status_bar.pack(side="bottom", fill="x", padx=styles.PAD_X_MEDIUM, pady=styles.PAD_Y_SMALL)

        try:
            self.library_handler.load_books_from_csv("data/books.csv")
            self.library_handler.load_members_from_csv("data/members.csv")
            self.library_handler.load_borrowings_from_csv("data/borrowings.csv")
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
        member_menu.add_command(label="添加会员", command=self.open_add_member_dialog)
        member_menu.add_command(label="显示所有会员", command=lambda: self.switch_view("all_members"))
        member_menu.add_command(label="查找会员", command=self.activate_member_search)

        # --- 借阅管理菜单 ---
        borrow_menu = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="借阅管理", menu=borrow_menu)
        borrow_menu.add_command(label="借阅书籍", command=self.open_borrow_book_dialog)
        borrow_menu.add_command(label="归还书籍", command=self.open_return_book_dialog)

        # --- 工具栏 --- # 修改: 应用样式
        self.toolbar_frame = customtkinter.CTkFrame(
            self, 
            height=styles.HEIGHT_TOOLBAR_BUTTON + styles.PAD_Y_MEDIUM * 2, 
            corner_radius=styles.CORNER_RADIUS_FRAME,
            fg_color=("gray85", "gray20") 
        )
        self.toolbar_frame.pack(side="top", fill="x", padx=styles.PAD_X_MEDIUM, pady=(styles.PAD_Y_MEDIUM, styles.PAD_Y_SMALL))

        # --- 工具栏按钮 --- # 修改: 应用样式, 移除图标
        common_button_config = {
            "height": styles.HEIGHT_TOOLBAR_BUTTON,
            "corner_radius": styles.CORNER_RADIUS_BUTTON,
            "font": styles.FONT_BUTTON,
            "fg_color": styles.PRIMARY_COLOR,
            "hover_color": styles.PRIMARY_COLOR_HOVER
        }
        
        action_button_config = { # 用于“所有书籍/会员”这类导航/动作按钮
            "height": styles.HEIGHT_TOOLBAR_BUTTON,
            "corner_radius": styles.CORNER_RADIUS_BUTTON,
            "font": styles.FONT_BUTTON,
            "fg_color": styles.SECONDARY_COLOR, 
            "hover_color": styles.SECONDARY_COLOR_HOVER
        }

        btn_add_book = customtkinter.CTkButton(
            self.toolbar_frame, text="添加书籍", command=self.open_add_book_dialog, 
            **common_button_config
        )
        btn_add_book.pack(side="left", padx=styles.PAD_X_SMALL, pady=styles.PAD_Y_SMALL)

        btn_add_member = customtkinter.CTkButton(
            self.toolbar_frame, text="添加会员", command=self.open_add_member_dialog, 
            **common_button_config
        )
        btn_add_member.pack(side="left", padx=styles.PAD_X_SMALL, pady=styles.PAD_Y_SMALL)

        btn_borrow_book = customtkinter.CTkButton(
            self.toolbar_frame, text="借阅书籍", command=self.open_borrow_book_dialog, 
            **common_button_config
        )
        btn_borrow_book.pack(side="left", padx=styles.PAD_X_SMALL, pady=styles.PAD_Y_SMALL)

        btn_return_book = customtkinter.CTkButton(
            self.toolbar_frame, text="归还书籍", command=self.open_return_book_dialog, 
            **common_button_config
        )
        btn_return_book.pack(side="left", padx=styles.PAD_X_SMALL, pady=styles.PAD_Y_SMALL)

        btn_show_all_books = customtkinter.CTkButton(
            self.toolbar_frame, text="所有书籍", command=lambda: self.switch_view("all_books"), 
            **action_button_config
        )
        btn_show_all_books.pack(side="left", padx=styles.PAD_X_SMALL, pady=styles.PAD_Y_SMALL)

        btn_show_all_members = customtkinter.CTkButton(
            self.toolbar_frame, text="所有会员", command=lambda: self.switch_view("all_members"), 
            **action_button_config
        )
        btn_show_all_members.pack(side="left", padx=styles.PAD_X_SMALL, pady=styles.PAD_Y_SMALL)


        # --- 主内容区 --- # 修改: 应用样式
        self.main_content_frame = customtkinter.CTkFrame(self, fg_color="transparent") 
        self.main_content_frame.pack(side="top", fill="both", expand=True, padx=styles.PAD_X_MEDIUM, pady=0)

        # 初始视图
        self.switch_view("welcome")


    def quit_application(self):
        try:
            self.library_handler.save_books_to_csv("data/books.csv")
            self.library_handler.save_members_to_csv("data/members.csv")
            self.library_handler.save_borrowings_to_csv("data/borrowings.csv")
        except Exception as e:
            import tkinter.messagebox
            tkinter.messagebox.showerror("保存错误", f"保存数据时发生错误: {e}")
        self.destroy()

    def placeholder_command(self):
        self.update_status("功能暂未实现", success=False)
        print("命令占位符被调用")

    def update_status(self, message, success=True): # 修改: 使用样式颜色
        self.status_bar.configure(text=message)
        if success:
            self.status_bar.configure(text_color=styles.SUCCESS_COLOR)
        else:
            self.status_bar.configure(text_color=styles.DANGER_COLOR)

    def switch_view(self, view_name, *args):
        # 清空主内容区
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

        if view_name == "welcome":
            self.show_welcome_view()
        elif view_name == "all_books":
            self.show_all_books_view()
        elif view_name == "all_members": 
            self.show_all_members_view()
        else:
            self.show_welcome_view() 

    def show_welcome_view(self): # 修改: 改进欢迎视图
        welcome_frame = customtkinter.CTkFrame(self.main_content_frame, fg_color="transparent")
        welcome_frame.pack(expand=True, fill="both", padx=styles.PAD_X_XLARGE, pady=styles.PAD_Y_XLARGE)
        
        welcome_label = customtkinter.CTkLabel(
            welcome_frame, 
            text="欢迎来到图书馆管理系统！", 
            font=customtkinter.CTkFont(size=24, weight="bold") 
        )
        welcome_label.pack(pady=(styles.PAD_Y_XLARGE, styles.PAD_Y_MEDIUM), anchor="center")
        
        info_label = customtkinter.CTkLabel(
            welcome_frame,
            text="请使用顶部菜单或工具栏开始操作。",
            font=styles.FONT_LARGE_NORMAL
        )
        info_label.pack(pady=styles.PAD_Y_MEDIUM, anchor="center")
        self.update_status("欢迎使用图书馆管理系统")

    def show_all_books_view(self):
        all_books_data = list(self.library_handler.books.values())
        
        if hasattr(self, 'book_list_view_instance') and self.book_list_view_instance.winfo_exists():
            self.book_list_view_instance.destroy()

        self.book_list_view_instance = BookListView(self.main_content_frame,
                                                    library_instance=self.library_handler,
                                                    master_app=self)
        self.book_list_view_instance.pack(fill="both", expand=True, padx=styles.PAD_X_SMALL, pady=styles.PAD_Y_SMALL) # 使用styles
        self.book_list_view_instance.populate_table(all_books_data)
        
        self.update_status(f"已显示 {len(all_books_data) if all_books_data else 0} 本书籍。", success=True)

    def open_add_book_dialog(self): 
        dialog = AddBookDialogCtl(master=self, library_instance=self.library_handler)
    
    def open_add_member_dialog(self): 
        dialog = AddMemberDialog(master=self, library_instance=self.library_handler)
    
    def open_borrow_book_dialog(self):
        dialog = BorrowBookDialog(master=self, library_instance=self.library_handler)
    
    def open_return_book_dialog(self):
        dialog = ReturnBookDialog(master=self, library_instance=self.library_handler)

    def activate_book_search(self):
        self.switch_view("all_books")
        if hasattr(self, 'book_list_view_instance') and \
           self.book_list_view_instance.winfo_exists() and \
           hasattr(self.book_list_view_instance, 'search_entry'):
            self.book_list_view_instance.search_entry.focus()
            self.update_status("准备查找书籍，请输入搜索条件。", success=True)
        else:
            self.update_status("无法激活书籍搜索功能。", success=False)

    def show_all_members_view(self):
        all_members_data = list(self.library_handler.members.values())

        if hasattr(self, 'member_list_view_instance') and self.member_list_view_instance.winfo_exists():
            self.member_list_view_instance.destroy()

        self.member_list_view_instance = MemberListView(
            self.main_content_frame,
            library_instance=self.library_handler,
            master_app=self
        )
        self.member_list_view_instance.pack(fill="both", expand=True, padx=styles.PAD_X_SMALL, pady=styles.PAD_Y_SMALL) # 使用styles
        self.member_list_view_instance.populate_table(all_members_data)
        
        self.update_status(f"已显示 {len(all_members_data) if all_members_data else 0} 位会员。", success=True)

    def activate_member_search(self):
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
        dialog = EditBookDialogCtl(master=self, library_instance=self.library_handler, isbn_to_edit=isbn) # Use renamed import

    def confirm_delete_book(self, isbn):
        book_to_delete = self.library_handler.find_book_by_isbn(isbn)
        if not book_to_delete:
            self.update_status(f"错误：尝试删除时未找到 ISBN 为 {isbn} 的书籍。", success=False)
            tkinter.messagebox.showerror("删除错误", f"未找到 ISBN 为 {isbn} 的书籍。", parent=self)
            return

        confirm_message = f"您确定要删除书籍 '{book_to_delete.title}' (ISBN: {isbn}) 吗？"
        if tkinter.messagebox.askyesno("确认删除", confirm_message, parent=self):
            try:
                self.library_handler.remove_book(isbn)
                self.library_handler.save_books_to_csv("data/books.csv") 
                self.update_status(f"书籍 '{book_to_delete.title}' (ISBN: {isbn}) 删除成功并已保存。", success=True)
                self.switch_view("all_books") 
            except exceptions.BookNotFoundError:
                self.update_status(f"错误：删除时未找到 ISBN 为 {isbn} 的书籍。", success=False)
                tkinter.messagebox.showerror("删除错误", f"删除时未找到 ISBN 为 {isbn} 的书籍。", parent=self)
            except Exception as e:
                self.update_status(f"删除书籍 '{book_to_delete.title}' 时发生错误: {e}", success=False)
                tkinter.messagebox.showerror("删除错误", f"删除书籍时发生未知错误: {e}", parent=self)
        else:
            self.update_status(f"取消删除书籍 ISBN: {isbn}", success=True)

    # --- Callbacks for MemberListView ---
    def open_edit_member_dialog(self, member_id):
        dialog = EditMemberDialog(master=self, library_instance=self.library_handler, member_id_to_edit=member_id)

    def confirm_delete_member(self, member_id):
        member_to_delete = self.library_handler.find_member_by_id(member_id) 
        if not member_to_delete:
            self.update_status(f"错误：尝试删除时未找到会员ID为 {member_id} 的会员。", success=False)
            tkinter.messagebox.showerror("删除错误", f"未找到会员ID为 {member_id} 的会员。", parent=self)
            return

        confirm_message = f"您确定要删除会员 '{member_to_delete.member_name}' (ID: {member_id}) 吗？"
        if tkinter.messagebox.askyesno("确认删除", confirm_message, parent=self):
            try:
                self.library_handler.remove_member(member_id)
                self.library_handler.save_members_to_csv("data/members.csv") 
                self.update_status(f"会员 '{member_to_delete.member_name}' (ID: {member_id}) 删除成功并已保存。", success=True)
                self.switch_view("all_members") 
            except exceptions.MemberNotFoundError:
                self.update_status(f"错误：删除时未找到会员ID为 {member_id} 的会员。", success=False)
                tkinter.messagebox.showerror("删除错误", f"删除时未找到会员ID为 {member_id} 的会员。", parent=self)
            except Exception as e:
                self.update_status(f"删除会员 '{member_to_delete.member_name}' 时发生错误: {e}", success=False)
                tkinter.messagebox.showerror("删除错误", f"删除会员时发生未知错误: {e}", parent=self)
        else:
            self.update_status(f"取消删除会员 ID: {member_id}", success=True)
    
    def _apply_styles(self): # 新增方法
        """应用一些全局样式设置"""
        self.protocol("WM_DELETE_WINDOW", self.quit_application)


if __name__ == "__main__":
    # 修改: 设置CustomTkinter外观和颜色主题应在创建主应用实例之前
    customtkinter.set_appearance_mode("System")  # System, Light, Dark
    customtkinter.set_default_color_theme("blue") # blue, dark-blue, green
    
    app = LibraryApp()
    app.mainloop()
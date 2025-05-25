import customtkinter
import tkinter # 导入 tkinter

from src.core_logic.library import Library
from src.core_logic.book import Book
from src.core_logic.library_member import LibraryMember
from src.core_logic import exceptions

class LibraryApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("图书馆管理系统")
        self.geometry("800x600")
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
        book_menu.add_command(label="添加书籍", command=self.placeholder_command)
        book_menu.add_command(label="显示所有书籍", command=self.placeholder_command)
        book_menu.add_command(label="查找书籍", command=self.placeholder_command)

        # --- 会员管理菜单 ---
        member_menu = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="会员管理", menu=member_menu)
        member_menu.add_command(label="添加会员", command=self.placeholder_command)
        member_menu.add_command(label="显示所有会员", command=self.placeholder_command)
        member_menu.add_command(label="查找会员", command=self.placeholder_command)

        # --- 借阅管理菜单 ---
        borrow_menu = tkinter.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="借阅管理", menu=borrow_menu)
        borrow_menu.add_command(label="借阅书籍", command=self.placeholder_command)
        borrow_menu.add_command(label="归还书籍", command=self.placeholder_command)

        # --- 工具栏 ---
        self.toolbar_frame = customtkinter.CTkFrame(self, height=50)
        self.toolbar_frame.pack(side="top", fill="x", padx=5, pady=5) # 添加一些边距

        # --- 工具栏按钮 ---
        btn_add_book = customtkinter.CTkButton(self.toolbar_frame, text="添加书籍", command=self.placeholder_command)
        btn_add_book.pack(side="left", padx=5, pady=5)

        btn_add_member = customtkinter.CTkButton(self.toolbar_frame, text="添加会员", command=self.placeholder_command)
        btn_add_member.pack(side="left", padx=5, pady=5)

        btn_borrow_book = customtkinter.CTkButton(self.toolbar_frame, text="借阅书籍", command=self.placeholder_command)
        btn_borrow_book.pack(side="left", padx=5, pady=5)

        btn_return_book = customtkinter.CTkButton(self.toolbar_frame, text="归还书籍", command=self.placeholder_command)
        btn_return_book.pack(side="left", padx=5, pady=5)

        btn_show_all_books = customtkinter.CTkButton(self.toolbar_frame, text="所有书籍", command=self.placeholder_command)
        btn_show_all_books.pack(side="left", padx=5, pady=5)

        btn_show_all_members = customtkinter.CTkButton(self.toolbar_frame, text="所有会员", command=self.placeholder_command)
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
        elif view_name == "add_book_form":
            self.show_add_book_form_view()
        # 可以根据需要添加更多视图
        else:
            self.show_welcome_view() # 默认或未知视图显示欢迎页

    def show_welcome_view(self):
        welcome_label = customtkinter.CTkLabel(self.main_content_frame, text="欢迎来到图书馆管理系统！", font=customtkinter.CTkFont(size=20, weight="bold"))
        welcome_label.pack(pady=20, padx=20, anchor="center")
        self.update_status("欢迎使用图书馆管理系统")

    def show_all_books_view(self):
        # 占位符：后续实现显示所有书籍的视图
        label = customtkinter.CTkLabel(self.main_content_frame, text="所有书籍视图（待实现）", font=customtkinter.CTkFont(size=16))
        label.pack(pady=20, padx=20, anchor="center")
        self.update_status("正在查看所有书籍")

    def show_add_book_form_view(self):
        # 占位符：后续实现添加书籍表单的视图
        label = customtkinter.CTkLabel(self.main_content_frame, text="添加书籍表单（待实现）", font=customtkinter.CTkFont(size=16))
        label.pack(pady=20, padx=20, anchor="center")
        self.update_status("准备添加新书")


if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()
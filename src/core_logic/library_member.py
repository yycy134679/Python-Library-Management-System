from .exceptions import BookNotBorrowedError

"""
图书馆会员管理模块
该模块定义了图书馆会员类(LibraryMember)，用于管理图书馆会员的基本信息和借阅操作。
"""

# 成员类
class LibraryMember(object):
    # 属性：姓名、成员ID、联系方式
    def __init__(self, member_id, member_name, phone):
        self.member_name = member_name
        self.member_id = member_id
        self.phone = phone
        self.borrowed_books = []  # （Book对象列表）：存储会员当前借阅的书籍列表。

    def display_info(self):
        """打印会员的信息"""
        print("*" * 15 + " 会员信息 " + "*" * 15)
        print(f"姓名：{self.member_name}")
        print(f"会员ID：{self.member_id}")
        print(f"联系方式：{self.phone}")
        print(f"借阅书籍：")
        if not self.borrowed_books:
            print("该会员没有借阅任何书籍")
        else:
            for i in self.borrowed_books:
                print(i.title, end=" ")
        print()

    def borrow_book(self, book):
        """借阅书籍"""
        self.borrowed_books.append(book)

    def return_book(self, book):
        """归还书籍"""
        if book in self.borrowed_books:
            self.borrowed_books.remove(book)
        else:
            raise BookNotBorrowedError(f"{self.member_name}没有借阅书籍{book.title}")
def update_member_info(self, name=None, phone=None):
        """ 更新会员信息 (姓名, 电话) """
        if name is not None:
            self.member_name = name
        if phone is not None:
            self.phone = phone
        print(f"会员 {self.member_id} ({self.member_name}) 的信息已更新。")

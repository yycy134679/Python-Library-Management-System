from .exceptions import InvalidCopyNumberError, BookNotAvailableError  # 从 exceptions.py 导入异常类

'''
图书类
该模块定义了图书类(Book)，用于管理图书馆中的书籍信息和借阅操作。
书籍类包含以下功能：
1. 显示书籍信息
2. 增加书籍副本数
3. 减少当前可借阅的副本数
4. 增加当前可借阅的副本数
5. 更新书籍信息
'''

# 图书类
class Book(object):
    # 属性：书名、作者、ISBN、出版年份、副本数、当前可借阅的副本数
    def __init__(self, title, author, isbn, publication_year, total_copies):
        self.title = title  # 书名
        self.author = author  # 作者
        self.isbn = isbn
        self.publication_year = publication_year  # 出版年份
        self.total_copies = total_copies  # 副本数
        self.available_copies = total_copies  # 当前可借阅副本数，初始值等于总副本数

    def display_info(self):
        """ 打印书籍信息"""
        print("*" * 15 + " 书籍信息 " + "*" * 15)
        print(f"书名：{self.title}")
        print(f"作者：{self.author}")
        print(f"ISBN：{self.isbn}")
        print(f"出版年份：{self.publication_year}")
        print(f"副本数：{self.total_copies}")
        print(f"当前可借阅的副本数：{self.available_copies}")
        print()

    def increase_copies(self, number):
        """ 增加书籍副本数"""
        if number <= 0:
            raise InvalidCopyNumberError("副本数必须大于0")
        self.total_copies += number
        self.available_copies += number

    # 将available_copies减少1（当书籍被借出时）。
    def decrease_available_copies(self):
        """ 减少当前可借阅的副本数"""
        if self.available_copies > 0:
            self.available_copies -= 1
            return True
        else:
            raise BookNotAvailableError(f"《{self.title}》当前没有可借阅的副本")

    # 将available_copies增加1（当书籍被归还时）。
    def increase_available_copies(self):
        if self.available_copies >= self.total_copies:
            raise Exception(f"逻辑错误：可用副本数 {self.available_copies} 不能大于总副本数 {self.total_copies}")
        else:
            self.available_copies += 1

    def update_book_info(self, title=None, author=None, publication_year=None, total_copies=None):
        """ 更新书籍信息 """
        if title is not None:
            self.title = title
        if author is not None:
            self.author = author
        if publication_year is not None:
            self.publication_year = publication_year
        
        if total_copies is not None:
            if not isinstance(total_copies, int) or total_copies < 0:
                raise ValueError("总副本数必须是一个非负整数。")
            
            borrowed_copies = self.total_copies - self.available_copies
            if total_copies < borrowed_copies:
                raise ValueError(f"新的总副本数 ({total_copies}) 不能少于已借出的副本数 ({borrowed_copies})。")
            
            delta_copies = total_copies - self.total_copies
            self.total_copies = total_copies
            self.available_copies += delta_copies
            if self.available_copies < 0:
                self.available_copies = 0
            if self.available_copies > self.total_copies:
                self.available_copies = self.total_copies
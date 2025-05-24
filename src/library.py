from book import Book  
from exceptions import (BookNotFoundError, MemberNotFoundError, BookNotAvailableError,
    BookAlreadyExistsError, MemberAlreadyExistsError, InvalidCopyNumberError,
    BookNotBorrowedError
)

import csv
import os


# 图书馆类
class Library(object):

    def __init__(self):
        self.books = {}
        self.members = {}

    # 将Book对象添加到books字典中。确保ISBN唯一。处理ISBN已存在的情况（例如更新副本或引发错误）。
    def add_book(self, book):
        if book.isbn in self.books:
            raise BookAlreadyExistsError(f"ISBN为‘{book.isbn}’的书籍已存在，无法添加")
        else:
            self.books[book.isbn] = book
            return True

    # 根据ISBN从books字典中移除书籍。处理ISBN未找到的情况。
    def remove_book(self, isbn):
        if isbn in self.books:
            del self.books[isbn]
            return True
        else:
            raise BookNotFoundError(f"ISBN为‘{isbn}’的书籍未找到，无法删除")

    # 通过ISBN在books字典中查找书籍，如果找到则返回Book对象
    def find_book_by_isbn(self, isbn):
        if isbn in self.books:
            return self.books[isbn]
        else:
            raise BookNotFoundError(f"ISBN为‘{isbn}’的书籍未找到")

    # 返回给定作者所写的书籍列表。
    def find_books_by_author(self, author_name):
        matching_books = []
        for book in self.books.values():
            if author_name == book.author:
                matching_books.append(book)
        return matching_books

    def modify_book_details(self, isbn, title=None, author=None, publication_year=None, total_copies=None):
        """
        修改指定ISBN的图书信息。
        允许修改书名、作者、出版年份和总副本数。
        """
        book = self.find_book_by_isbn(isbn) # 会在找不到时抛出 BookNotFoundError
        
        try:
            book.update_book_info(title=title,
                                  author=author,
                                  publication_year=publication_year,
                                  total_copies=total_copies)
            # 更新信息后，如果图书数据持久化到CSV，可能需要重新保存
            # self.save_books_to_csv() # 暂时注释掉，避免每次修改都保存，可以由调用者决定何时保存
            print(f"ISBN 为 '{isbn}' 的图书信息已成功更新。")
            return True
        except ValueError as ve:
            print(f"更新图书信息失败：{ve}")
            return False
        except Exception as e:
            print(f"更新图书信息时发生未知错误：{e}")
            return False
    # 将LibraryMember对象添加到members字典中。
    def add_member(self, member):
        if member.member_id in self.members:
            raise MemberAlreadyExistsError(f"ID为‘{member.member_id}’的会员已存在，无法添加")
        else:
            self.members[member.member_id] = member
            return True

    # 根据member_id从members字典中移除会员。处理member_id未找到的情况。
    def remove_member(self, member_id):
        if member_id in self.members:
            del self.members[member_id]
            return True
        else:
            raise MemberNotFoundError(f"ID为‘{member_id}’的会员未找到，无法删除")

    def find_member_by_id(self, member_id):
        """根据会员ID在members字典中查找会员，如果找到则返回LibraryMember对象"""
        if member_id in self.members:
            return self.members[member_id]
        else:
            raise MemberNotFoundError(f"ID为‘{member_id}’的会员未找到")
    def modify_member_details(self, member_id, name=None, phone=None):
        """
        修改指定ID的会员信息。
        允许修改姓名和电话。
        """
        member = self.find_member_by_id(member_id) # 会在找不到时抛出 MemberNotFoundError
        
        try:
            member.update_member_info(name=name, phone=phone)
            # 更新信息后，如果会员数据持久化到CSV，可能需要重新保存
            # self.save_members_to_csv() # 暂时注释掉，避免每次修改都保存
            print(f"会员 ID '{member_id}' 的信息已成功更新。")
            return True
        except Exception as e: # 更通用的异常捕获，因为 update_member_info 目前不抛特定异常
            print(f"更新会员信息时发生未知错误：{e}")
            return False

    def borrow_book_item(self, isbn, member_id):
        """处理借阅书籍的过程"""
        book = self.find_book_by_isbn(isbn)
        member = self.find_member_by_id(member_id)
        if book.available_copies > 0:
            book.decrease_available_copies()
            member.borrow_book(book)
            return True
        else:
            raise BookNotAvailableError(f"《{book.title}》当前没有可借阅的副本")

    def return_book_item(self, isbn, member_id):
        """处理书籍的归还过程"""
        book = self.find_book_by_isbn(isbn)
        member = self.find_member_by_id(member_id)
        if book in member.borrowed_books:
            book.increase_available_copies()
            member.return_book(book)
        else:
            raise BookNotBorrowedError(f"会员‘{member.member_name}’未借阅《{book.title}》")

    def display_all_books(self):
        """打印图书馆中所有书籍的信息"""
        if self.books:
            for i in self.books:
                self.books[i].display_info()
            print("所有书籍信息打印完毕")
        else:
            print("图书管中没有书籍")

    def display_all_members(self):
        """打印图书馆中所有会员的信息"""
        if self.members:
            for i in self.members:
                self.members[i].display_info()
            print("所有会员信息打印完毕")
        else:
            print("图书馆中没有会员")

    def save_books_to_csv(self, filename="books.csv"):  # 将 filename 设置为可选参数，默认值为 "books.csv"
        """保存书籍数据到 CSV 文件"""
        try:
            with open(filename, "w", encoding="utf8", newline="") as file:
                w = csv.writer(file)
                # 写入表头
                w.writerow(["ISBN", "书名", "作者", "出版年份", "总副本数", "可用副本数"])
                # 写入每条书籍数据
                for book in self.books.values():
                    w.writerow([book.isbn,
                                book.title,
                                book.author,
                                book.publication_year,
                                book.total_copies,
                                book.available_copies])
                print(f"书籍数据已保存到文件‘{filename}’")
        except Exception as e:
            print(f"保存书籍数据到文件‘{filename}’失败：{e}")

    def load_books_from_csv(self, filename="books.csv"):
        """从 CSV 文件中读取书籍数据"""
        if not os.path.exists(filename):
            print(f"文件‘{filename}’不存在，正在创建空文件...")
            with open(filename, "w", encoding="utf8", newline="") as file:
                w = csv.writer(file)
                # 写入表头
                w.writerow(["ISBN", "书名", "作者", "出版年份", "总副本数", "可用副本数"])
                print(f"文件‘{filename}’已创建，请添加书籍数据后再次尝试读取。")
            return
        try:
            with open(filename, "r", encoding="utf8") as file:
                r = csv.reader(file)
                # 跳过表头
                next(r)
                # 读取每条书籍数据
                for row in r:
                    # 从数据行中解构出书籍信息
                    isbn, title, author, publication_year, total_copies, available_copies = row
                    # 将读取到的字符串数据转换为正确的类型
                    publication_year = int(publication_year)
                    total_copies = int(total_copies)
                    available_copies = int(available_copies)
                    book = Book(title, author, isbn, publication_year, total_copies)
                    book.available_copies = available_copies  # 从 CSV 加载时，需要设置正确的 available_copies
                    self.books[isbn] = book  # 使用 ISBN 作为键添加到 books 字典
            print(f"书籍数据已成功从 '{filename}' 文件加载。")
        except FileNotFoundError:  # 明确捕获 FileNotFoundError 异常
            print(f"CSV 文件 '{filename}' 未找到。")
        except Exception as e:  # 捕获其他可能的 CSV 读取或数据转换异常
            print(f"从 CSV 文件加载书籍数据时发生错误: {e}")

    def save_members_to_csv(self, filename="members.csv"):
        """保存会员数据到 CSV 文件"""
        try:
            with open(filename, "w", encoding="utf8", newline="") as file:
                w = csv.writer(file)
                w.writerow(["ID", "姓名", "电话"])
                for member in self.members.values():
                    w.writerow([member.member_id, member.member_name, member.phone])
                print(f"会员数据已保存到文件‘{filename}’")
        except Exception as e:
            print(f"保存会员数据到文件‘{filename}’失败：{e}")

    def load_members_from_csv(self, filename="members.csv"):
        """从 CSV 文件中读取会员数据"""
        if not os.path.exists(filename):
            print(f"文件‘{filename}’不存在，正在创建空文件...")
            with open(filename, "w", encoding="utf8", newline="") as file:
                w = csv.writer(file)
                w.writerow(["ID", "姓名", "电话"])
                print(f"文件‘{filename}’已创建，请添加会员数据后再次尝试读取。")
            return
        try:
            from library_member import LibraryMember
            with open(filename, "r", encoding="utf8") as file:
                r = csv.reader(file)
                next(r)
                for row in r:
                    member_id, member_name, phone = row
                    member = LibraryMember(member_id, member_name, phone)
                    self.members[member_id] = member
            print(f"会员数据已成功从 '{filename}' 文件加载。")
        except FileNotFoundError:
            print(f"CSV 文件 '{filename}' 未找到。")
        except Exception as e:
            print(f"从 CSV 文件加载会员数据时发生错误: {e}")


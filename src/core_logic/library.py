from .book import Book
from .exceptions import (BookNotFoundError, MemberNotFoundError, BookNotAvailableError,
    BookAlreadyExistsError, MemberAlreadyExistsError, InvalidCopyNumberError,
    BookNotBorrowedError
)
from .borrow_record import BorrowRecord

import csv
import os
from datetime import datetime

'''
图书馆管理模块
该模块定义了图书馆类(Library)，用于管理图书馆的书籍、会员和借阅记录。
该模块包含以下功能：
1. 添加、删除和查找书籍
2. 添加、删除和查找会员
3. 借阅和归还书籍
4. 管理借阅记录
5. 保存和加载书籍、会员和借阅记录到CSV文件
'''



# 图书馆类
class Library(object):

    def __init__(self):
        self.books = {}
        self.members = {}
        self.borrowings = {}  # 借阅记录字典，键为借阅ID，值为BorrowRecord对象
        self.next_borrowing_id = 1  # 下一个可用的借阅ID

    def add_book(self, book):
        """添加书籍到图书馆"""
        if book.isbn in self.books:
            raise BookAlreadyExistsError(f"ISBN为‘{book.isbn}’的书籍已存在，无法添加")
        else:
            self.books[book.isbn] = book
            return True

    def remove_book(self, isbn):
        """根据ISBN从图书馆中移除书籍"""
        if isbn in self.books:
            del self.books[isbn]
            return True
        else:
            raise BookNotFoundError(f"ISBN为‘{isbn}’的书籍未找到，无法删除")

    def find_book_by_isbn(self, isbn):
        """根据ISBN在books字典中查找书籍，如果找到则返回Book对象"""
        if isbn in self.books:
            return self.books[isbn]
        else:
            raise BookNotFoundError(f"ISBN为‘{isbn}’的书籍未找到")

    def find_books_by_author(self, author_name):
        """根据作者名查找书籍"""
        matching_books = []
        for book in self.books.values():
            if author_name == book.author:
                matching_books.append(book)
        return matching_books

    def find_books_by_title(self, title_keyword):
        """根据书名关键词查找书籍 (大小写不敏感，部分匹配)"""
        matching_books = []
        title_keyword_lower = title_keyword.lower()
        for book in self.books.values():
            if title_keyword_lower in book.title.lower():
                matching_books.append(book)
        return matching_books

    def modify_book_details(self, isbn, title=None, author=None, publication_year=None, total_copies=None):
        """
        修改指定ISBN的图书信息。
        允许修改书名、作者、出版年份和总副本数。
        """
        book = self.find_book_by_isbn(isbn) 
        
        try:
            book.update_book_info(title=title,
                                  author=author,
                                  publication_year=publication_year,
                                  total_copies=total_copies)
            print(f"ISBN 为 '{isbn}' 的图书信息已成功更新。")
            return True
        except ValueError as ve:
            print(f"更新图书信息失败：{ve}")
            return False
        except Exception as e:
            print(f"更新图书信息时发生未知错误：{e}")
            return False
    def add_member(self, member):
        """添加会员到图书馆"""
        if member.member_id in self.members:
            raise MemberAlreadyExistsError(f"ID为‘{member.member_id}’的会员已存在，无法添加")
        else:
            self.members[member.member_id] = member
            return True

    def remove_member(self, member_id):
        """根据会员ID从图书馆中移除会员"""
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
            raise MemberNotFoundError(f"ID为'{member_id}'的会员未找到")
            
    def find_members_by_name(self, name_keyword):
        """根据会员姓名关键词查找会员 (大小写不敏感，部分匹配)"""
        matching_members = []
        name_keyword_lower = name_keyword.lower()
        for member in self.members.values():
            if name_keyword_lower in member.member_name.lower():
                matching_members.append(member)
        return matching_members
    
    def find_members_by_phone(self, phone_keyword):
        """根据会员电话号码关键词查找会员 (部分匹配)"""
        matching_members = []
        for member in self.members.values():
            if phone_keyword in member.phone:
                matching_members.append(member)
        return matching_members
            
    def modify_member_details(self, member_id, name=None, phone=None):
        """
        修改指定ID的会员信息。
        允许修改姓名和电话。
        """
        member = self.find_member_by_id(member_id) # 会在找不到时抛出 MemberNotFoundError
        
        try:
            member.update_member_info(name=name, phone=phone)
            print(f"会员 ID '{member_id}' 的信息已成功更新。")
            return True
        except Exception as e: 
            print(f"更新会员信息时发生未知错误：{e}")
            return False

    def borrow_book_item(self, isbn, member_id):
        """处理借阅书籍的过程，并创建借阅记录"""
        book = self.find_book_by_isbn(isbn)
        member = self.find_member_by_id(member_id)
        
        if book.available_copies > 0:
            # 减少可用副本数
            book.decrease_available_copies()
            
            # 更新会员的借阅书籍列表
            member.borrow_book(book)
            
            # 创建借阅记录
            record_id = self.next_borrowing_id
            self.next_borrowing_id += 1
            
            borrow_record = BorrowRecord(
                record_id=record_id,
                book_isbn=isbn,
                member_id=member_id,
                borrow_date=datetime.now()
            )
            
            # 将借阅记录添加到借阅记录字典
            self.borrowings[record_id] = borrow_record
            
            return True
        else:
            raise BookNotAvailableError(f"《{book.title}》当前没有可借阅的副本")

    def return_book_item(self, isbn, member_id):
        """处理书籍的归还过程，并更新借阅记录"""
        book = self.find_book_by_isbn(isbn)
        member = self.find_member_by_id(member_id)
        
        if book in member.borrowed_books:
            # 增加可用副本数
            book.increase_available_copies()
            
            # 更新会员的借阅书籍列表
            member.return_book(book)
            
            # 更新借阅记录
            # 查找该会员借阅该书籍的未归还记录
            for record in self.borrowings.values():
                if (record.book_isbn == isbn and
                    record.member_id == member_id and
                    record.status == "已借出"):
                    # 更新记录状态为已归还
                    record.return_book()
                    break
            
            return True
        else:
            raise BookNotBorrowedError(f"会员'{member.member_name}'未借阅《{book.title}》")
    
    def get_member_borrowings(self, member_id):
        """获取指定会员的所有借阅记录"""
        return [record for record in self.borrowings.values()
                if record.member_id == member_id]
    
    def get_book_borrowings(self, isbn):
        """获取指定书籍的所有借阅记录"""
        return [record for record in self.borrowings.values()
                if record.book_isbn == isbn]
    
    def get_active_borrowings(self):
        """获取所有未归还的借阅记录"""
        return [record for record in self.borrowings.values()
                if record.status == "已借出"]
    
    def get_overdue_borrowings(self):
        """获取所有逾期的借阅记录"""
        return [record for record in self.borrowings.values()
                if record.status == "已借出" and record.is_overdue()]

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

    def save_books_to_csv(self, filename="books.csv"):  
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
                    book.available_copies = available_copies  
                    self.books[isbn] = book  
            print(f"书籍数据已成功从 '{filename}' 文件加载。")
        except FileNotFoundError:  
            print(f"CSV 文件 '{filename}' 未找到。")
        except Exception as e: 
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
            from .library_member import LibraryMember
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
    
    def save_borrowings_to_csv(self, filename="borrowings.csv"):
        """保存借阅记录到 CSV 文件"""
        try:
            with open(filename, "w", encoding="utf8", newline="") as file:
                w = csv.writer(file)
                # 写入表头
                w.writerow(["借阅ID", "书籍ISBN", "会员ID", "借阅日期", "预计归还日期", "实际归还日期", "状态"])
                # 写入每条借阅记录
                for record in self.borrowings.values():
                    w.writerow(record.to_csv_row())
                print(f"借阅记录已保存到文件'{filename}'")
        except Exception as e:
            print(f"保存借阅记录到文件'{filename}'失败：{e}")
    
    def load_borrowings_from_csv(self, filename="borrowings.csv"):
        """从 CSV 文件中读取借阅记录"""
        if not os.path.exists(filename):
            print(f"文件'{filename}'不存在，正在创建空文件...")
            with open(filename, "w", encoding="utf8", newline="") as file:
                w = csv.writer(file)
                w.writerow(["借阅ID", "书籍ISBN", "会员ID", "借阅日期", "预计归还日期", "实际归还日期", "状态"])
                print(f"文件'{filename}'已创建，请添加借阅记录后再次尝试读取。")
            return
        
        try:
            with open(filename, "r", encoding="utf8") as file:
                r = csv.reader(file)
                # 跳过表头
                next(r)
                # 读取每条借阅记录
                self.borrowings = {}
                max_id = 0
                
                for row in r:
                    if not row:  
                        continue
                        
                    record = BorrowRecord.from_csv_row(row)
                    record_id = int(record.record_id)
                    self.borrowings[record_id] = record
                    
                    if record_id > max_id:
                        max_id = record_id
                
                self.next_borrowing_id = max_id + 1
                
            print(f"借阅记录已成功从 '{filename}' 文件加载。")
        except FileNotFoundError:
            print(f"CSV 文件 '{filename}' 未找到。")
        except Exception as e:
            print(f"从 CSV 文件加载借阅记录时发生错误: {e}")

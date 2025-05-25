import os
from .library import Library
from .book import Book
from .library_member import LibraryMember
from .exceptions import (
    BookNotFoundError, MemberNotFoundError, BookNotAvailableError,
    BookAlreadyExistsError, MemberAlreadyExistsError, InvalidCopyNumberError,
    BookNotBorrowedError
)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# 实例化一个图书馆类
my_library = Library()
# 加载书籍和会员数据
my_library.load_books_from_csv()  # 加载书籍数据，默认从 books.csv 文件加载
my_library.load_members_from_csv()  # 加载会员数据，默认从 members.csv 文件加载

while True:
    print("""欢迎来到图书馆管理系统！
        请选择操作：
        1. 添加书籍
        2. 移除书籍
        3. 查找书籍 (按 ISBN)
        4. 查找书籍 (按作者)
        5. 显示所有书籍
        6. 添加会员
        7. 移除会员
        8. 查找会员 (按 ID)
        9. 显示所有会员
        10. 借阅书籍
        11. 归还书籍
        12. 修改图书信息
        13. 修改会员信息
        14. 退出系统
    请选择 (输入数字 1-14):""")

    choose = int(input("请输入你的选择："))
    match choose:
        case 1:  # 添加书籍
            title = input("书名：")
            author = input("作者：")
            isbn = input("ISBN：")
            try:
                publication_year = int(input("出版年份："))
                total_copies = int(input("总副本数"))
                new_book = Book(title, author, isbn, publication_year, total_copies)
                my_library.add_book(new_book)
                print("添加成功")
            except ValueError:  # 捕获 ValueError 异常 (输入年份或副本数不是整数)
                print("年份和副本数必须是整数")
            except BookAlreadyExistsError as e:
                print(f"错误：{e}")
            except Exception as e:
                print("发生未知错误")

            input("\n按任意键继续...")
            clear_screen()

        case 2:  # 移除书籍
            isbn = input("请输入要移除书籍的ISBN：")
            try:
                if my_library.remove_book(isbn):
                    print("移除成功")
            except BookNotFoundError as e:
                print(f"错误：{e}")
            except Exception as e:
                print("发生未知错误")

            input("\n按任意键继续...")
            clear_screen()

        case 3:  # 查找书籍 (按 ISBN)
            isbn = input("请输入要查找书籍的ISBN：")
            try:
                book = my_library.find_book_by_isbn(isbn)
                book.display_info()
            except BookNotFoundError as e:
                print(f"错误：{e}")
            except Exception as e:
                print("发生未知错误")

            input("\n按任意键继续...")
            clear_screen()

        case 4:  # 查找书籍 (按作者)
            author = input("请输入要查找书籍的作者：")
            books = my_library.find_books_by_author(author)
            if books:
                for book in books:
                    book.display_info()
            else:
                print("未找到书籍")
            input("\n按任意键继续...")
            clear_screen()

        case 5:  # 显示所有书籍
            my_library.display_all_books()
            input("\n按任意键继续...")
            clear_screen()

        case 6:  # 添加会员
            member_id = input("请输入你的ID：")
            member_name = input("请输入你的姓名：")
            phone = input("请输入你的联系电话：")
            try:
                new_member = LibraryMember(member_id, member_name, phone)
                my_library.add_member(new_member)
                print("添加成功")
            except MemberAlreadyExistsError as e:
                print(f"错误：{e}")
            except Exception as e:
                print("发生未知错误")

            input("\n按任意键继续...")
            clear_screen()

        case 7:  # 移除会员
            member_id = input("请输入要移除会员的ID：")
            try:
                my_library.remove_member(member_id)
                print("移除成功")
            except MemberNotFoundError as e:
                print(f"错误：{e}")
            except Exception as e:
                print("发生未知错误")

            input("\n按任意键继续...")
            clear_screen()

        case 8:  # 查找会员 (按 ID)
            member_id = input("请输入要查找会员的ID：")
            try:
                member = my_library.find_member_by_id(member_id)
                member.display_info()
            except MemberNotFoundError as e:
                print(f"错误：{e}")

            input("\n按任意键继续...")
            clear_screen()

        case 9:  # 显示所有会员
            my_library.display_all_members()
            input("\n按任意键继续...")
            clear_screen()

        case 10:  # 借阅书籍
            isbn = input("请输入要借阅书籍的ISBN：")
            member_id = input("请输入要借阅书籍的会员ID：")
            try:
                my_library.borrow_book_item(isbn, member_id)
            except BookNotFoundError as e:
                print(f"错误：{e}")
            except MemberNotFoundError as e:
                print(f"错误：{e}")
            except BookNotAvailableError as e:
                print(f"错误：{e}")
            except Exception as e:
                print("发生未知错误")

            input("\n按任意键继续...")
            clear_screen()

        case 11:  # 归还书籍
            isbn = input("请输入要归还书籍的ISBN：")
            member_id = input("请输入要归还书籍的会员ID：")
            try:
                my_library.return_book_item(isbn, member_id)
            except BookNotFoundError as e:
                print(f"错误：{e}")
            except MemberNotFoundError as e:
                print(f"错误：{e}")
            except BookNotBorrowedError as e:
                print(f"错误：{e}")
            except Exception as e:
                print("发生未知错误")

            input("\n按任意键继续...")
            clear_screen()

        case 12: # 修改图书信息
            isbn = input("请输入要修改信息的图书ISBN：")
            print("请输入新的图书信息（留空表示不修改）：")
            title = input(f"新书名 (当前: {my_library.find_book_by_isbn(isbn).title if isbn in my_library.books else '未知'}): ") or None
            author = input(f"新作者 (当前: {my_library.find_book_by_isbn(isbn).author if isbn in my_library.books else '未知'}): ") or None
            
            publication_year_str = input(f"新出版年份 (当前: {my_library.find_book_by_isbn(isbn).publication_year if isbn in my_library.books else '未知'}): ")
            publication_year = int(publication_year_str) if publication_year_str else None
            
            total_copies_str = input(f"新总副本数 (当前: {my_library.find_book_by_isbn(isbn).total_copies if isbn in my_library.books else '未知'}): ")
            total_copies = int(total_copies_str) if total_copies_str else None

            try:
                if my_library.modify_book_details(isbn, title, author, publication_year, total_copies):
                    print("图书信息修改成功。")
                # modify_book_details 内部会打印失败信息
            except BookNotFoundError as e:
                print(f"错误：{e}")
            except ValueError as e:
                print(f"输入错误：{e}")
            except Exception as e:
                print(f"发生未知错误：{e}")
            input("\n按任意键继续...")
            clear_screen()

        case 13: # 修改会员信息
            member_id = input("请输入要修改信息的会员ID：")
            print("请输入新的会员信息（留空表示不修改）：")
            
            name = input(f"新姓名 (当前: {my_library.find_member_by_id(member_id).member_name if member_id in my_library.members else '未知'}): ") or None
            phone = input(f"新电话 (当前: {my_library.find_member_by_id(member_id).phone if member_id in my_library.members else '未知'}): ") or None
            
            try:
                if my_library.modify_member_details(member_id, name, phone):
                    print("会员信息修改成功。")
                # modify_member_details 内部会打印失败信息
            except MemberNotFoundError as e:
                print(f"错误：{e}")
            except Exception as e:
                print(f"发生未知错误：{e}")
            input("\n按任意键继续...")
            clear_screen()

        case 14:  # 退出系统
            print("感谢使用图书管理系统")
            # **保存书籍和会员数据**
            my_library.save_books_to_csv()  # 调用时无需传递参数，使用默认文件名 "books.csv"
            my_library.save_members_to_csv() # 添加保存会员数据
            break
        case _:
            print("输入错误，请重新输入")

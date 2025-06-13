"""
借阅记录模块
该模块定义了借阅记录类(BorrowRecord)，用于管理图书馆的借阅记录。
该模块包含以下功能：
1. 创建借阅记录
2. 更新借阅记录
3. 查询借阅记录
4. 删除借阅记录
"""

from datetime import datetime, timedelta

class BorrowRecord:
    """借阅记录类，表示一条借阅记录"""
    
    def __init__(self, record_id, book_isbn, member_id, borrow_date=None, 
                 expected_return_date=None, actual_return_date=None, status="已借出"):
        """
        初始化一条借阅记录
        
        参数:
            record_id: 借阅记录ID，唯一标识一条借阅记录
            book_isbn: 被借阅书籍的ISBN
            member_id: 借阅会员的ID
            borrow_date: 借阅日期和时间，默认为当前时间
            expected_return_date: 预计归还日期，默认为借阅日期后30天
            actual_return_date: 实际归还日期和时间，如果尚未归还则为None
            status: 借阅记录的状态，可以是"已借出"或"已归还"
        """
        self.record_id = record_id
        self.book_isbn = book_isbn
        self.member_id = member_id
        
        # 如果没有提供借阅日期，则使用当前时间
        if borrow_date is None:
            self.borrow_date = datetime.now()
        else:
            self.borrow_date = borrow_date
            
        # 如果没有提供预计归还日期，则默认为借阅日期后30天
        if expected_return_date is None:
            if isinstance(self.borrow_date, datetime):
                self.expected_return_date = (self.borrow_date + timedelta(days=30)).date()
            else:
                # 如果borrow_date已经是字符串，则不处理expected_return_date
                self.expected_return_date = None
        else:
            self.expected_return_date = expected_return_date
            
        self.actual_return_date = actual_return_date
        self.status = status
    
    def return_book(self):
        """将借阅记录标记为已归还，并记录归还日期"""
        self.actual_return_date = datetime.now()
        self.status = "已归还"
        
    def is_overdue(self):
        """检查借阅是否已逾期"""
        if self.status == "已归还":
            return False
        
        today = datetime.now().date()
        if isinstance(self.expected_return_date, str):
            # 如果expected_return_date是字符串，尝试转换为日期对象
            try:
                expected_date = datetime.strptime(self.expected_return_date, "%Y-%m-%d").date()
                return today > expected_date
            except ValueError:
                # 如果无法解析日期字符串，则返回False
                return False
        else:
            # 如果expected_return_date已经是日期对象
            return today > self.expected_return_date
    
    def to_csv_row(self):
        """将借阅记录转换为CSV行格式"""
        borrow_date_str = self.borrow_date.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.borrow_date, datetime) else self.borrow_date
        expected_return_date_str = self.expected_return_date.strftime("%Y-%m-%d") if isinstance(self.expected_return_date, datetime) else self.expected_return_date
        actual_return_date_str = self.actual_return_date.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.actual_return_date, datetime) else self.actual_return_date or ""
        
        return [
            str(self.record_id),
            self.book_isbn,
            self.member_id,
            borrow_date_str,
            expected_return_date_str,
            actual_return_date_str,
            self.status
        ]
    
    @classmethod
    def from_csv_row(cls, row):
        """从CSV行创建借阅记录对象"""
        record_id, book_isbn, member_id, borrow_date, expected_return_date, actual_return_date, status = row
        
        # 转换日期字符串为日期对象
        try:
            borrow_date = datetime.strptime(borrow_date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # 如果无法解析，保持原样
            pass
            
        try:
            expected_return_date = datetime.strptime(expected_return_date, "%Y-%m-%d").date()
        except ValueError:
            # 如果无法解析，保持原样
            pass
            
        if actual_return_date:
            try:
                actual_return_date = datetime.strptime(actual_return_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # 如果无法解析，保持原样
                pass
        else:
            actual_return_date = None
            
        return cls(
            record_id=record_id,
            book_isbn=book_isbn,
            member_id=member_id,
            borrow_date=borrow_date,
            expected_return_date=expected_return_date,
            actual_return_date=actual_return_date,
            status=status
        )
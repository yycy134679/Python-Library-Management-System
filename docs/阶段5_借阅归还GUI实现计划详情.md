# 阶段 5: 借阅与归还模块 GUI 实现 - 详细计划

## Mermaid 流程图

```mermaid
graph TD
    subgraph "阶段 5: 借阅与归还模块 GUI 实现"
        T5_1["任务 5.1: 实现"借阅书籍"功能"]
        T5_2["任务 5.2: 实现"归还书籍"功能"]

        D_Task2_1["(依赖) 任务 2.1: 后端逻辑集成"]

        D_Task2_1 --> T5_1
        D_Task2_1 --> T5_2
    end

    %% 外部依赖
    Ext_LibraryLogic["src/core_logic/library.py (后端逻辑)"] --> D_Task2_1

    %% GUI 交互组件与后端调用示意
    subgraph "借阅与归还 GUI 组件与后端交互"
        BorrowDialog["BorrowBookDialog (CTkToplevel)"]
        ReturnDialog["ReturnBookDialog (CTkToplevel)"]

        T5_1 --> BorrowDialog
        BorrowDialog -.-> |调用 library.borrow_book_item()| Ext_LibraryLogic
        BorrowDialog -.-> |调用 library.save_books_to_csv()| Ext_LibraryLogic
        
        T5_2 --> ReturnDialog
        ReturnDialog -.-> |调用 library.return_book_item()| Ext_LibraryLogic
        ReturnDialog -.-> |调用 library.save_books_to_csv()| Ext_LibraryLogic
    end
```

## 详细实施计划：阶段 5 借阅与归还模块 GUI

**总体说明:**
* 所有 GUI 组件应使用 `CustomTkinter`。
* 所有与后端数据的交互都应通过 `src/core_logic/library.py` 中定义的 `Library` 类实例进行。
* 错误处理和用户反馈应通过状态栏更新或模态对话框实现。
* 假定 `Library` 类实例在主 GUI 应用中为 `self.library_handler`。
* 所有借阅和归还操作完成后，应调用 `self.library_handler.save_books_to_csv("data/books.csv")` 以确保数据持久化。

---

**任务 5.1: 实现"借阅书籍"功能 (通过对话框输入，调用后端，处理反馈)**
* **目标:** 创建一个模态对话框，让用户输入书籍ISBN和会员ID进行借阅操作。
* **依赖:** 任务 2.1 (后端逻辑集成)
* **步骤:**
    1. **创建借阅对话框类:**
        * 在 `src/gui/` 目录下创建一个新文件 `borrow_dialogs.py`。
        * 定义一个类 `BorrowBookDialog` 继承自 `CTkToplevel`。
        * **输入字段:** 添加 `CTkLabel` 和 `CTkEntry` 用于输入：
            * 书籍ISBN
            * 会员ID
        * **按钮:** 添加 "确认借阅" 和 "取消" 按钮。
    2. **触发借阅对话框:**
        * 在 `src/gui/main_gui.py` 中，定义 `open_borrow_book_dialog` 方法。
        * 将菜单栏的"借阅书籍"菜单项和工具栏的"借阅书籍"按钮连接到此方法。
    3. **"确认借阅"按钮逻辑 (`BorrowBookDialog` 内):**
        * 获取输入的ISBN和会员ID。
        * **前端校验:**
            * 检查ISBN和会员ID是否为空。
            * 可选：尝试使用 `library_instance.find_book_by_isbn()` 和 `library_instance.find_member_by_id()` 验证ISBN和会员ID是否存在。
        * **调用后端:**
            * 如果前端校验通过，调用 `self.library_instance.borrow_book_item(isbn, member_id)`。
        * **保存数据:**
            * 调用 `self.library_instance.save_books_to_csv("data/books.csv")`。
        * **处理结果:**
            * **成功:** 关闭对话框，更新主GUI状态栏 ("借阅成功")。
            * **失败 (如书籍不存在、会员不存在、书籍无可用副本):** 显示相应错误信息。
    4. **"取消"按钮逻辑:** 关闭对话框。
    5. **异常处理:**
        * 处理 `BookNotFoundError`、`MemberNotFoundError`、`BookNotAvailableError` 等可能的异常。

---

**任务 5.2: 实现"归还书籍"功能 (通过对话框输入，调用后端，处理反馈)**
* **目标:** 创建一个模态对话框，让用户输入书籍ISBN和会员ID进行归还操作。
* **依赖:** 任务 2.1 (后端逻辑集成)
* **步骤:**
    1. **创建归还对话框类:**
        * 在 `borrow_dialogs.py` 中定义一个类 `ReturnBookDialog` 继承自 `CTkToplevel`。
        * **输入字段:** 添加 `CTkLabel` 和 `CTkEntry` 用于输入：
            * 书籍ISBN
            * 会员ID
        * **按钮:** 添加 "确认归还" 和 "取消" 按钮。
    2. **触发归还对话框:**
        * 在 `src/gui/main_gui.py` 中，定义 `open_return_book_dialog` 方法。
        * 将菜单栏的"归还书籍"菜单项和工具栏的"归还书籍"按钮连接到此方法。
    3. **"确认归还"按钮逻辑 (`ReturnBookDialog` 内):**
        * 获取输入的ISBN和会员ID。
        * **前端校验:**
            * 检查ISBN和会员ID是否为空。
            * 可选：尝试使用 `library_instance.find_book_by_isbn()` 和 `library_instance.find_member_by_id()` 验证ISBN和会员ID是否存在。
        * **调用后端:**
            * 如果前端校验通过，调用 `self.library_instance.return_book_item(isbn, member_id)`。
        * **保存数据:**
            * 调用 `self.library_instance.save_books_to_csv("data/books.csv")`。
        * **处理结果:**
            * **成功:** 关闭对话框，更新主GUI状态栏 ("归还成功")。
            * **失败 (如书籍不存在、会员不存在、会员未借阅该书籍):** 显示相应错误信息。
    4. **"取消"按钮逻辑:** 关闭对话框。
    5. **异常处理:**
        * 处理 `BookNotFoundError`、`MemberNotFoundError`、`BookNotBorrowedError` 等可能的异常。

---

**改进建议 (可选):**

1. **借阅/归还书籍选择器:**
   * 可以考虑增加一个下拉选择器，显示所有可用书籍和会员，让用户直接选择而不是输入ISBN/ID。
   * 这需要修改对话框，添加 `CTkComboBox` 组件，并从 `library_instance` 获取书籍和会员列表。

2. **会员借阅状态视图:**
   * 可以考虑添加一个视图，显示特定会员当前借阅的所有书籍，并提供直接归还的按钮。
   * 这需要创建一个新的视图类，类似于 `BookListView` 和 `MemberListView`。

3. **书籍借阅状态显示:**
   * 在书籍列表中添加一列显示当前可借阅副本数，以及哪些会员借阅了该书籍。
   * 这需要修改 `BookListView` 类。


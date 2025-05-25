# 阶段 3: 书籍管理模块 GUI 实现 - 详细计划

## Mermaid 流程图

```mermaid
graph TD
    subgraph "阶段 3: 书籍管理模块 GUI 实现"
        T3_1["任务 3.1: 创建书籍列表GUI组件"]
        T3_2["任务 3.2: 实现“显示所有书籍”"]
        T3_3["任务 3.3: 实现“添加书籍”"]
        T3_4["任务 3.4: 实现“修改书籍”"]
        T3_5["任务 3.5: 实现“删除书籍”"]
        T3_6["任务 3.6: 实现“查找书籍”"]

        D_Task1_5["(依赖) 任务 1.5: 主内容区视图切换"]
        D_Task2_1["(依赖) 任务 2.1: 后端逻辑集成"]
        D_Task2_2["(依赖) 任务 2.2: 启动时加载数据"]

        D_Task1_5 --> T3_1
        D_Task2_2 --> T3_1

        T3_1 --> T3_2
        T3_1 --> T3_4
        T3_1 --> T3_5
        T3_1 --> T3_6

        D_Task2_1 --> T3_3
        T3_2 --> T3_3  // 添加后刷新列表

        D_Task2_1 --> T3_4
        D_Task2_1 --> T3_5
        D_Task2_1 --> T3_6
    end

    %% 外部依赖
    Ext_MainGUI["src/gui/main_gui.py (主GUI框架)"] --> D_Task1_5
    Ext_LibraryLogic["src/core_logic/library.py (后端逻辑)"] --> D_Task2_1
    Ext_CSVData["data/books.csv (数据源)"] --> D_Task2_2

    %% GUI 交互组件与后端调用示意
    subgraph "GUI 组件与后端交互 (示例)"
        BookListView["BookListView (CTkScrollableFrame)"]
        AddBookDialog["AddBookDialog (CTkToplevel)"]
        EditBookDialog["EditBookDialog (CTkToplevel)"]
        ConfirmDeleteDialog["ConfirmDeleteDialog (CTkMessagebox)"]
        SearchBar["搜索栏 (CTkFrame with Entry & Button)"]

        T3_1 --> BookListView
        T3_2 -.-> |调用 library.display_all_books() 或 get_all_books()| Ext_LibraryLogic
        T3_2 -.-> |填充数据| BookListView

        T3_3 --> AddBookDialog
        AddBookDialog -.-> |调用 library.add_book()| Ext_LibraryLogic
        AddBookDialog -.-> |成功后刷新| T3_2

        T3_4 --> EditBookDialog
        BookListView -.-> |触发修改, 传ISBN| EditBookDialog
        EditBookDialog -.-> |调用 library.find_book_by_isbn() 获取数据| Ext_LibraryLogic
        EditBookDialog -.-> |调用 library.modify_book_details()| Ext_LibraryLogic
        EditBookDialog -.-> |成功后刷新| T3_2

        T3_5 --> ConfirmDeleteDialog
        BookListView -.-> |触发删除, 传ISBN| ConfirmDeleteDialog
        ConfirmDeleteDialog -.-> |调用 library.remove_book()| Ext_LibraryLogic
        ConfirmDeleteDialog -.-> |成功后刷新| T3_2

        T3_6 --> SearchBar
        SearchBar -.-> |调用 library.find_book_by_isbn() / find_books_by_author()| Ext_LibraryLogic
        SearchBar -.-> |填充结果| BookListView
    end
```

## 详细实施计划：阶段 3 书籍管理模块 GUI

**总体说明:**
*   所有 GUI 组件应使用 `CustomTkinter`。
*   所有与后端数据的交互都应通过 `src/core_logic/library.py` 中定义的 `Library` 类实例进行。
*   错误处理和用户反馈应通过状态栏更新或模态对话框实现，如 `docs/需求建议书.md` 所述。
*   假定 `Library` 类实例在主 GUI 应用中已创建并可访问 (例如 `self.library_instance`)。
*   `library.display_all_books()` 可能需要调整为返回书籍列表 (例如，创建一个新方法 `get_all_books()` 返回 `self.books`) 以便 GUI 使用。

---

**任务 3.1: 创建书籍列表的GUI显示组件 (表格形式，含操作按钮)**
*   **目标:** 创建一个可复用的 `CustomTkinter` Frame 用于显示书籍列表。
*   **依赖:** 任务 1.5 (主内容区视图切换), 任务 2.2 (启动时加载数据，确保有数据可供潜在的初始显示)
*   **步骤:**
    1.  在 `src/gui/` 目录下创建一个新文件，例如 `book_view.py`。
    2.  在 `book_view.py` 中定义一个类 `BookListView` (或类似名称)，它可以是一个 `CTkFrame` 或包含一个 `CTkScrollableFrame` 用于显示表格数据。
    3.  **表格头部:**
        *   在 `BookListView` 中定义固定的表头标签，对应列： "ISBN", "书名", "作者", "出版年份", "副本数", "操作"。
    4.  **表格内容区域:**
        *   使用 `CTkScrollableFrame` 来容纳动态生成的书籍条目行。
    5.  **数据填充方法:**
        *   实现一个公共方法 `populate_table(self, books_data)`：
            *   该方法接收一个书籍数据列表 (每个元素是一个 `Book` 对象或包含书籍属性的字典)。
            *   清空 `CTkScrollableFrame` 中已有的书籍条目。
            *   遍历 `books_data`，为每本书籍创建一个行 Frame。
            *   在每行 Frame 中，为书籍的每个属性 (ISBN, 书名, 作者, 年份, 副本数) 创建 `CTkLabel`。
            *   **操作按钮:** 在每行的“操作”列中创建两个 `CTkButton`：“修改”和“删除”。
                *   将书籍的 ISBN (或其他唯一标识符) 与这些按钮关联起来，以便后续操作知道要处理哪本书。这可以通过 `lambda` 函数传递参数给按钮的 `command` 回调。
                *   按钮的 `command` 暂时可以为空或打印占位信息，具体实现在任务 3.4 和 3.5。
    6.  **集成到主GUI:**
        *   在 `src/gui/main_gui.py` 中，当需要显示书籍列表时，能够实例化 `BookListView` 并将其放置在主内容区。

---

**任务 3.2: 实现“显示所有书籍”功能，加载并展示数据**
*   **目标:** 当用户触发相应操作时，从后端获取所有书籍并在 `BookListView` 中展示。
*   **依赖:** 任务 3.1 (GUI组件已创建)
*   **步骤:**
    1.  **触发机制:**
        *   在 `src/gui/main_gui.py` 中，为菜单栏的“显示所有书籍”菜单项和/或工具栏的相应按钮绑定一个命令/回调函数，例如 `show_all_books_view()`。
    2.  **数据获取与展示:**
        *   在 `show_all_books_view()` 函数中：
            *   调用后端逻辑获取所有书籍数据。这可能需要 `self.library_instance.get_all_books()` (假设此方法返回 `self.books` 列表) 或调整 `self.library_instance.display_all_books()`。
            *   获取或创建 `BookListView` 的实例。
            *   调用 `book_list_view_instance.populate_table(all_books_data)` 方法，传入获取到的书籍数据。
            *   确保 `BookListView` 在主内容区可见 (利用任务 1.5 的视图切换逻辑)。
            *   更新状态栏，例如 "已显示所有书籍"。

---

**任务 3.3: 实现“添加书籍”功能 (通过对话框输入，调用后端)**
*   **目标:** 提供一个模态对话框让用户输入新书信息，并通过后端逻辑添加书籍。
*   **依赖:** 任务 2.1 (后端逻辑集成), 任务 3.2 (添加成功后刷新列表)
*   **步骤:**
    1.  **创建添加书籍对话框类:**
        *   在 `src/gui/` 目录下创建一个新文件，例如 `book_dialogs.py` (或者如果已有类似的，则添加到其中)。
        *   定义一个类 `AddBookDialog` 继承自 `CTkToplevel`。
        *   **输入字段:** 在对话框中添加 `CTkLabel` 和 `CTkEntry` 用于输入：书名、作者、ISBN、出版年份、副本数。
        *   **按钮:** 添加 "确认" (`CTkButton`) 和 "取消" (`CTkButton`)。
    2.  **触发添加对话框:**
        *   在 `src/gui/main_gui.py` 中，为菜单栏的“添加书籍”菜单项和/或工具栏的相应按钮绑定一个命令/回调函数，例如 `open_add_book_dialog()`。
        *   该函数实例化并显示 `AddBookDialog`。
    3.  **“确认”按钮逻辑 (`AddBookDialog` 内):**
        *   获取所有输入字段的值。
        *   **前端校验:**
            *   检查必填项 (如 ISBN, 书名, 作者) 是否为空。
            *   校验数据格式 (例如，年份和副本数应为数字)。
            *   如果校验失败，在对话框内显示错误提示 (例如，一个 `CTkLabel`)，并阻止后续操作。
        *   **调用后端:**
            *   如果前端校验通过，创建一个 `Book` 对象 (从 `src.core_logic.book` 导入)。
            *   调用 `self.library_instance.add_book(new_book_object)`。
        *   **处理结果:**
            *   根据后端返回的结果 (通常是成功，或因ISBN冲突等抛出异常):
                *   **成功:** 关闭对话框，更新主GUI状态栏 ("书籍添加成功")，并调用任务 3.2 的逻辑刷新书籍列表。
                *   **失败:** 在对话框内或主GUI状态栏显示错误信息 (例如 "ISBN已存在" 或 "添加失败")。
    4.  **“取消”按钮逻辑 (`AddBookDialog` 内):**
        *   关闭对话框。

---

**任务 3.4: 实现“修改书籍”功能 (从列表触发，通过对话框修改，调用后端)**
*   **目标:** 允许用户修改现有书籍的信息。
*   **依赖:** 任务 3.1 (列表中的修改按钮), 任务 2.1 (后端逻辑集成)
*   **步骤:**
    1.  **创建修改书籍对话框类:**
        *   在 `book_dialogs.py` (或类似文件) 中定义一个类 `EditBookDialog` 继承自 `CTkToplevel`。
        *   该对话框的构造函数应接收一个 `isbn` 参数。
        *   **数据预填充:**
            *   在对话框初始化时，使用传入的 `isbn` 调用 `self.library_instance.find_book_by_isbn(isbn)` 获取当前书籍的详细信息。
            *   如果未找到书籍，显示错误并关闭对话框或妥善处理。
            *   **输入字段:** 添加 `CTkLabel` 和 `CTkEntry` 用于：书名、作者、(ISBN 通常设为只读或不显示，因为它是主键)、出版年份、副本数。用获取到的书籍信息预填充这些字段。
        *   **按钮:** 添加 "确认" 和 "取消" 按钮。
    2.  **触发修改对话框 (在 `BookListView` 内):**
        *   在 `BookListView` 的 `populate_table` 方法中，为每行“修改”按钮的 `command` 绑定一个回调函数，例如 `self.master.open_edit_book_dialog(isbn)` (假设 `BookListView` 的 master 是主GUI控制器，或者通过其他方式传递ISBN并调用)。
        *   这个回调函数接收书籍的 `isbn`，然后实例化并显示 `EditBookDialog(isbn=book_isbn)`。
    3.  **“确认”按钮逻辑 (`EditBookDialog` 内):**
        *   获取所有输入字段修改后的值。
        *   **前端校验:** (类似添加功能，但注意ISBN通常不在此处修改)。
        *   **调用后端:**
            *   如果前端校验通过，调用 `self.library_instance.modify_book_details(isbn, title=new_title, author=new_author, publication_year=new_year, total_copies=new_copies)`。
        *   **处理结果:**
            *   **成功:** 关闭对话框，更新主GUI状态栏 ("书籍修改成功")，并刷新书籍列表 (调用任务 3.2 的逻辑)。
            *   **失败:** 在对话框内或主GUI状态栏显示错误信息。
    4.  **“取消”按钮逻辑 (`EditBookDialog` 内):**
        *   关闭对话框。

---

**任务 3.5: 实现“删除书籍”功能 (从列表触发，带确认，调用后端)**
*   **目标:** 允许用户删除书籍，并在操作前进行确认。
*   **依赖:** 任务 3.1 (列表中的删除按钮), 任务 2.1 (后端逻辑集成)
*   **步骤:**
    1.  **触发删除流程 (在 `BookListView` 内):**
        *   在 `BookListView` 的 `populate_table` 方法中，为每行“删除”按钮的 `command` 绑定一个回调函数，例如 `self.master.confirm_delete_book(isbn)`。
        *   这个回调函数接收书籍的 `isbn`。
    2.  **确认对话框:**
        *   在 `confirm_delete_book(isbn)` 函数中 (通常在主 GUI 控制器中实现):
            *   使用 `CTkMessagebox` (如果 CustomTkinter 没有内置的，可能需要自定义一个简单的确认对话框，或者使用 tkinter 的 `messagebox.askyesno`) 弹出一个确认对话框，例如 "您确定要删除 ISBN 为 [isbn] 的书籍吗？"。
    3.  **处理用户选择:**
        *   如果用户选择 "是" (确认删除):
            *   **调用后端:** 调用 `self.library_instance.remove_book(isbn)`。
            *   **处理结果:**
                *   **成功:** 更新主GUI状态栏 ("书籍删除成功")，并刷新书籍列表 (调用任务 3.2 的逻辑)。
                *   **失败 (例如，书籍未找到):** 在主GUI状态栏显示错误信息。
        *   如果用户选择 "否"，则不执行任何操作。

---

**任务 3.6: 实现“查找书籍（按ISBN/作者）”功能，筛选并显示结果**
*   **目标:** 允许用户根据 ISBN 或作者名搜索书籍，并在 `BookListView` 中显示结果。
*   **依赖:** 任务 3.1 (GUI组件用于显示结果), 任务 2.1 (后端逻辑集成)
*   **步骤:**
    1.  **创建搜索UI组件:**
        *   在主GUI界面中，与 `BookListView` 关联的区域（例如其上方），创建一个搜索区域。
        *   包含一个 `CTkComboBox` 或 `CTkSegmentedButton` 让用户选择搜索类型 ("ISBN" 或 "作者")。
        *   包含一个 `CTkEntry`供用户输入搜索关键词。
        *   包含一个 `CTkButton` ("搜索")。
    2.  **“搜索”按钮逻辑:**
        *   获取选择的搜索类型 (ISBN/作者) 和输入的搜索关键词。
        *   **前端校验:** 检查关键词是否为空。
        *   **调用后端:**
            *   如果搜索类型是 "ISBN":
                *   调用 `book_object = self.library_instance.find_book_by_isbn(keyword)`。
                *   将结果（单个 `Book` 对象或 `None`）包装成列表 `found_books = [book_object] if book_object else []`。
            *   如果搜索类型是 "作者":
                *   调用 `found_books = self.library_instance.find_books_by_author(keyword)` (此方法应返回书籍列表)。
        *   **显示结果:**
            *   获取 `BookListView` 实例。
            *   调用 `book_list_view_instance.populate_table(found_books)`。
            *   更新状态栏，例如 "找到 X 本书" 或 "未找到匹配书籍"。
    3.  **“显示所有/清空搜索”功能 (可选但推荐):**
        *   可以添加一个“显示所有书籍”按钮或在搜索后自动恢复到显示所有书籍的机制，或者当搜索框为空时点击搜索则显示所有。这可以通过再次调用任务 3.2 的逻辑实现。


**问题和补充：** 
* 添加搜索类型：按书名搜索
* 添加书籍后数据没有保存到books.csv中
* 搜索不存在的书籍时，提示未找到书籍 (如果之前有内容，清空列表)
* 更新图书信息时发生未知错误：'Book' object has no attribute 'update_book_info'
* 删除书籍没有把books.csv中对应的书籍删除
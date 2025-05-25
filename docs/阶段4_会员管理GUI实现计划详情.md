# 阶段 4: 会员管理模块 GUI 实现 - 详细计划

## Mermaid 流程图

```mermaid
graph TD
    subgraph "阶段 4: 会员管理模块 GUI 实现"
        T4_1["任务 4.1: 创建会员列表GUI组件"]
        T4_2["任务 4.2: 实现“显示所有会员”"]
        T4_3["任务 4.3: 实现“添加会员”"]
        T4_4["任务 4.4: 实现“修改会员”"]
        T4_5["任务 4.5: 实现“删除会员”"]
        T4_6["任务 4.6: 实现“查找会员 (按ID)”"]

        D_Task1_5_M["(依赖) 任务 1.5: 主内容区视图切换"]
        D_Task2_1_M["(依赖) 任务 2.1: 后端逻辑集成"]
        D_Task2_2_M["(依赖) 任务 2.2: 启动时加载数据 (会员数据)"]

        D_Task1_5_M --> T4_1
        D_Task2_2_M --> T4_1

        T4_1 --> T4_2
        T4_1 --> T4_4
        T4_1 --> T4_5
        T4_1 --> T4_6

        D_Task2_1_M --> T4_3
        T4_2 --> T4_3  // 添加后刷新列表

        D_Task2_1_M --> T4_4
        D_Task2_1_M --> T4_5
        D_Task2_1_M --> T4_6
    end

    %% 外部依赖 (与书籍管理类似，但针对会员)
    Ext_MainGUI_M["src/gui/main_gui.py (主GUI框架)"] --> D_Task1_5_M
    Ext_LibraryLogic_M["src/core_logic/library.py (后端逻辑)"] --> D_Task2_1_M
    Ext_CSVData_M["data/members.csv (数据源)"] --> D_Task2_2_M

    %% GUI 交互组件与后端调用示意 (会员模块)
    subgraph "会员GUI组件与后端交互 (示例)"
        MemberListView["MemberListView (CTkScrollableFrame)"]
        AddMemberDialog["AddMemberDialog (CTkToplevel)"]
        EditMemberDialog["EditMemberDialog (CTkToplevel)"]
        ConfirmDeleteMemberDialog["ConfirmDeleteMemberDialog (CTkMessagebox)"]
        MemberSearchBar["会员搜索栏 (CTkFrame with Entry & Button)"]

        T4_1 --> MemberListView
        T4_2 -.-> |调用 library.get_all_members() (或类似)| Ext_LibraryLogic_M
        T4_2 -.-> |填充数据| MemberListView

        T4_3 --> AddMemberDialog
        AddMemberDialog -.-> |调用 library.add_member()| Ext_LibraryLogic_M
        AddMemberDialog -.-> |成功后刷新| T4_2

        T4_4 --> EditMemberDialog
        MemberListView -.-> |触发修改, 传MemberID| EditMemberDialog
        EditMemberDialog -.-> |调用 library.find_member_by_id() 获取数据| Ext_LibraryLogic_M
        EditMemberDialog -.-> |调用 library.modify_member_details()| Ext_LibraryLogic_M
        EditMemberDialog -.-> |成功后刷新| T4_2

        T4_5 --> ConfirmDeleteMemberDialog
        MemberListView -.-> |触发删除, 传MemberID| ConfirmDeleteMemberDialog
        ConfirmDeleteMemberDialog -.-> |调用 library.remove_member()| Ext_LibraryLogic_M
        ConfirmDeleteMemberDialog -.-> |成功后刷新| T4_2

        T4_6 --> MemberSearchBar
        MemberSearchBar -.-> |调用 library.find_member_by_id()| Ext_LibraryLogic_M
        MemberSearchBar -.-> |填充结果| MemberListView
    end
```

## 详细实施计划：阶段 4 会员管理模块 GUI

**总体说明:**
*   所有 GUI 组件应使用 `CustomTkinter`。
*   所有与后端数据的交互都应通过 `src/core_logic/library.py` 中定义的 `Library` 类实例进行。
*   错误处理和用户反馈应通过状态栏更新或模态对话框实现。
*   假定 `Library` 类实例在主 GUI 应用中为 `self.library_handler`。
*   与书籍类似，`self.library_handler.members` 是一个字典，GUI层面需要使用 `list(self.library_handler.members.values())` 来获取会员对象列表。
*   所有添加、修改、删除会员的操作完成后，应调用 `self.library_handler.save_members_to_csv("data/members.csv")` 以确保数据持久化。

---

**任务 4.1: 创建会员列表的GUI显示组件 (表格形式，含操作按钮)**
*   **目标:** 创建一个可复用的 `CustomTkinter` Frame 用于显示会员列表。
*   **依赖:** 任务 1.5 (主内容区视图切换), 任务 2.2 (启动时加载会员数据)
*   **步骤:**
    1.  在 `src/gui/` 目录下创建一个新文件，例如 `member_view.py`。
    2.  在 `member_view.py` 中定义一个类 `MemberListView`，它可以是一个 `CTkFrame` 或包含一个 `CTkScrollableFrame`。
    3.  **表格头部:** 定义固定的表头标签："会员ID", "姓名", "电话", "操作"。
    4.  **表格内容区域:** 使用 `CTkScrollableFrame` 来容纳动态生成的会员条目行。
    5.  **数据填充方法 `populate_table(self, members_data)`:**
        *   接收会员数据列表 (每个元素是 `LibraryMember` 对象)。
        *   清空已有条目。
        *   遍历数据，为每个会员创建行 Frame，包含各属性的 `CTkLabel`。
        *   在“操作”列创建 "修改" 和 "删除" `CTkButton`，关联会员ID。
    6.  **集成到主GUI:** `src/gui/main_gui.py` 中能实例化并显示 `MemberListView`。

---

**任务 4.2: 实现“显示所有会员”功能**
*   **目标:** 加载并展示所有会员数据。
*   **依赖:** 任务 4.1
*   **步骤:**
    1.  **触发机制:** `src/gui/main_gui.py` 中，为“显示所有会员”菜单项和工具栏按钮绑定命令，调用如 `show_all_members_view()`。
    2.  **数据获取与展示 (`show_all_members_view()`):**
        *   调用 `list(self.library_handler.members.values())` 获取会员对象列表。
        *   获取或创建 `MemberListView` 实例。
        *   调用 `member_list_view_instance.populate_table(all_members_data)`。
        *   确保 `MemberListView` 在主内容区可见。
        *   更新状态栏。

---

**任务 4.3: 实现“添加会员”功能**
*   **目标:** 通过对话框输入新会员信息并添加。
*   **依赖:** 任务 2.1, 任务 4.2 (用于刷新)
*   **步骤:**
    1.  **创建添加会员对话框类:**
        *   在 `src/gui/` 目录下创建 `member_dialogs.py` (或复用现有对话框文件结构，例如 `book_dialogs.py` 并重命名或在其中添加新类)。
        *   定义 `AddMemberDialog` 类 (继承 `CTkToplevel`)。
        *   输入字段: "会员ID", "姓名", "电话"。
        *   按钮: "确认", "取消"。
    2.  **触发添加对话框:** `src/gui/main_gui.py` 中绑定菜单/工具栏按钮到 `open_add_member_dialog()`。
    3.  **“确认”按钮逻辑 (`AddMemberDialog` 内):**
        *   获取输入值。
        *   **前端校验:** 必填项、ID唯一性（可由后端主要处理，前端可做初步提示）。
        *   **调用后端:** 创建 `LibraryMember` 对象 (从 `src.core_logic.library_member` 导入)，调用 `self.library_instance.add_member(new_member_object)`。
        *   **保存数据:** 调用 `self.library_instance.save_members_to_csv("data/members.csv")`。
        *   **处理结果:** 关闭对话框，刷新会员列表，更新状态栏。处理错误（如ID已存在）。
    4.  **“取消”按钮逻辑:** 关闭对话框。

---

**任务 4.4: 实现“修改会员”功能**
*   **目标:** 修改现有会员信息。
*   **依赖:** 任务 4.1, 任务 2.1
*   **步骤:**
    1.  **创建修改会员对话框类:**
        *   在 `member_dialogs.py` 中定义 `EditMemberDialog` 类，接收 `member_id`。
        *   **数据预填充:** 使用 `member_id` 调用 `self.library_instance.find_member_by_id()` 获取信息并预填输入字段 (姓名, 电话；ID通常只读)。
        *   按钮: "确认", "取消"。
    2.  **触发修改对话框 (`MemberListView` 内):** “修改”按钮的 `command` 调用主GUI控制器的方法，传递 `member_id`。
    3.  **“确认”按钮逻辑 (`EditMemberDialog` 内):**
        *   获取修改后的值。
        *   **前端校验。**
        *   **调用后端:** `self.library_instance.modify_member_details(member_id, name=new_name, phone=new_phone)`。
        *   **保存数据:** 调用 `self.library_instance.save_members_to_csv("data/members.csv")`。
        *   **处理结果:** 关闭对话框，刷新列表，更新状态栏。
    4.  **“取消”按钮逻辑:** 关闭对话框。

---

**任务 4.5: 实现“删除会员”功能**
*   **目标:** 删除会员，带确认。
*   **依赖:** 任务 4.1, 任务 2.1
*   **步骤:**
    1.  **触发删除流程 (`MemberListView` 内):** “删除”按钮的 `command` 调用主GUI控制器的方法 `confirm_delete_member(member_id)`。
    2.  **确认对话框 (`confirm_delete_member` 内):** 使用 `tkinter.messagebox.askyesno` 确认。
    3.  **处理用户选择:**
        *   若确认：调用 `self.library_instance.remove_member(member_id)`。
        *   **保存数据:** 调用 `self.library_instance.save_members_to_csv("data/members.csv")`。
        *   处理结果：刷新列表，更新状态栏。
        *   若取消：无操作。

---

**任务 4.6: 实现“查找会员（按ID）”功能**
*   **目标:** 根据会员ID搜索会员。
*   **依赖:** 任务 4.1, 任务 2.1
*   **步骤:**
    1.  **创建搜索UI组件 (`MemberListView` 内):**
        *   与书籍搜索类似，但搜索类型固定为 "会员ID" (或只有一个输入框和搜索按钮)。
        *   包含 `CTkEntry` 输入ID，`CTkButton` ("搜索")。
        *   可选 "显示所有/清空搜索" 按钮。
    2.  **“搜索”按钮逻辑:**
        *   获取输入的ID。
        *   **调用后端:** `member_object = self.library_instance.find_member_by_id(member_id_keyword)`。
        *   **显示结果:** 调用 `populate_table()` (结果需包装成列表)。更新状态栏。
    3.  **“显示所有”逻辑:** 清空搜索框，调用 `list(self.library_instance.members.values())` 重新填充表格。

**问题与补充** 
* 添加搜索类型：按会员id搜索、按姓名搜索、按电话搜索
* 优化显示所有会员界面
* 查找不存在的会员id时会员列表显示 "没有可显示的会员信息。" (如果之前有内容，清空列表)

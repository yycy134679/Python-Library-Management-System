import customtkinter as ctk

class MemberListView(ctk.CTkFrame):
    def __init__(self, master, library_instance, master_app, **kwargs):
        super().__init__(master, **kwargs)
        self.library_instance = library_instance
        self.master_app = master_app # Reference to the main application instance

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1) # Main column for content
        self.grid_rowconfigure(2, weight=1) # Row for the scrollable list (调整为第3行，因为第2行是表头)

        # --- Search Frame with multiple search types ---
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5,2))
        search_frame.grid_columnconfigure(2, weight=1) # Allow search entry to expand

        # Search type selection
        ctk.CTkLabel(search_frame, text="搜索类型:").pack(side="left", padx=(0,5))
        self.search_type_var = ctk.StringVar(value="会员ID")
        search_type_options = ["会员ID", "姓名", "电话"]
        self.search_type_menu = ctk.CTkOptionMenu(search_frame, variable=self.search_type_var, values=search_type_options)
        self.search_type_menu.pack(side="left", padx=5)

        # Search entry
        ctk.CTkLabel(search_frame, text="关键词:").pack(side="left", padx=(10,5))
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="输入搜索关键词...")
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.search_entry.bind("<Return>", self.perform_search)

        # Buttons
        search_button = ctk.CTkButton(search_frame, text="搜索", width=80, command=self.perform_search)
        search_button.pack(side="left", padx=5)
        
        clear_search_button = ctk.CTkButton(search_frame, text="显示全部", width=100, command=self.show_all_members)
        clear_search_button.pack(side="left", padx=(5,0))

        # --- 信息显示标签 (直接放在搜索框下方) ---
        self.info_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.info_label.grid(row=1, column=0, sticky="w", padx=15, pady=(0,0))
        
        # --- Header Frame for Table ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(2,0))
        # Adjust column weights as needed, 3 for data, 1 for actions
        header_frame.grid_columnconfigure((0, 1, 2), weight=1)
        header_frame.grid_columnconfigure(3, weight=0) # Actions column less weight or fixed

        # 使用更醒目的样式来显示表头
        headers = ["会员ID", "姓名", "电话", "操作"]
        for i, header_text in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame,
                text=header_text,
                font=ctk.CTkFont(weight="bold", size=14),
                fg_color="#3B8ED0",  # 使用主题色
                corner_radius=6,
                text_color="white"
            )
            sticky_val = "w"
            if header_text == "操作":
                sticky_val = "e" # Align "操作" to the right
            elif header_text == "会员ID":
                 sticky_val = "w" # Default
            label.grid(row=0, column=i, padx=5, pady=5, sticky=sticky_val)


        # Scrollable Frame for member entries - 减小与上方元素的间距
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0,5))
        self.scrollable_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.scrollable_frame.grid_columnconfigure(3, weight=0)


    def populate_table(self, members_data):
        # Clear existing rows
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # 更新信息标签，显示结果数量
        if members_data:
            self.info_label.configure(text=f"共找到 {len(members_data)} 位会员", text_color="green")
        else:
            self.info_label.configure(text="没有可显示的会员信息", text_color="orange")
            no_data_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="没有可显示的会员信息。",
                pady=20,
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_data_label.grid(row=0, column=0, columnspan=4, sticky="ew")
            return

        for i, member in enumerate(members_data):
            # 为每一行创建一个背景框，使界面更美观
            row_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=("gray90", "gray20") if i % 2 == 0 else "transparent")
            row_frame.grid(row=i, column=0, columnspan=4, sticky="ew", padx=2, pady=2)
            row_frame.grid_columnconfigure((0, 1, 2), weight=1)
            row_frame.grid_columnconfigure(3, weight=0)
            
            # Member ID
            member_id_label = ctk.CTkLabel(row_frame, text=member.member_id, anchor="w")
            member_id_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

            # Name
            name_label = ctk.CTkLabel(row_frame, text=member.member_name, anchor="w")
            name_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            # Phone
            phone_label = ctk.CTkLabel(row_frame, text=member.phone, anchor="w")
            phone_label.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
            
            # Action buttons frame
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=3, padx=5, pady=2, sticky="e")
            
            edit_button = ctk.CTkButton(
                actions_frame,
                text="修改",
                width=60,
                command=lambda m_id=member.member_id: self.master_app.open_edit_member_dialog(m_id)
            )
            edit_button.pack(side="left", padx=(0,5))

            delete_button = ctk.CTkButton(
                actions_frame,
                text="删除",
                width=60,
                fg_color="red",
                hover_color="darkred",
                command=lambda m_id=member.member_id: self.master_app.confirm_delete_member(m_id)
            )
            delete_button.pack(side="left")

    def perform_search(self, event=None):
        keyword = self.search_entry.get().strip()
        search_type = self.search_type_var.get()
        
        if not keyword:
            self.master_app.update_status(f"请输入{search_type}关键词进行搜索。", success=False)
            return

        found_members = []
        try:
            if search_type == "会员ID":
                try:
                    member = self.library_instance.find_member_by_id(keyword)
                    if member:
                        found_members = [member]
                except:
                    # 如果会员ID不存在，find_member_by_id可能会抛出异常
                    # 我们捕获异常并保持found_members为空列表
                    pass
            elif search_type == "姓名":
                found_members = self.library_instance.find_members_by_name(keyword)
            elif search_type == "电话":
                found_members = self.library_instance.find_members_by_phone(keyword)
            
            # 无论搜索结果如何，都更新表格
            self.populate_table(found_members)
            
            # 更新状态栏
            if found_members:
                self.master_app.update_status(f"找到 {len(found_members)} 位符合{search_type}'{keyword}'的会员。", success=True)
            else:
                self.master_app.update_status(f"未找到符合{search_type}'{keyword}'的会员。", success=False)
        except Exception as e:
            self.master_app.update_status(f"搜索会员时发生错误: {e}", success=False)
            print(f"Member search error: {e}")

    def show_all_members(self):
        self.search_entry.delete(0, ctk.END)
        all_members_list = list(self.library_instance.members.values())
        self.populate_table(all_members_list)
        self.master_app.update_status(f"已显示所有 {len(all_members_list) if all_members_list else 0} 位会员。", success=True)
        # 当显示全部会员时，清空搜索类型下拉框的选择
        self.search_type_var.set("会员ID")

if __name__ == '__main__':
    # Example Usage (for testing MemberListView independently)
    class App(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Member List View Test")
            self.geometry("800x600")

            class MockMember:
                def __init__(self, member_id, member_name, phone):
                    self.member_id = member_id
                    self.member_name = member_name
                    self.phone = phone
            
            class MockLibrary:
                def __init__(self):
                    self.members = {
                        "M001": MockMember("M001", "张三", "13800138000"),
                        "M002": MockMember("M002", "李四", "13900139000"),
                        "M003": MockMember("M003", "王五", "13700137000")
                    }
                def find_member_by_id(self, member_id):
                    return self.members.get(member_id)

            self.library_instance = MockLibrary()
            
            self.member_list_view = MemberListView(self, library_instance=self.library_instance, master_app=self)
            self.member_list_view.pack(fill="both", expand=True, padx=10, pady=10)
            
            self.member_list_view.populate_table(list(self.library_instance.members.values()))

        def open_edit_member_dialog(self, member_id):
            print(f"Master app: Request to edit member with ID: {member_id}")
            # Placeholder
            dialog = ctk.CTkToplevel(self)
            dialog.geometry("300x200")
            dialog.title("Edit Member (Placeholder)")
            label = ctk.CTkLabel(dialog, text=f"Editing member: {member_id}")
            label.pack(padx=20, pady=20)

        def confirm_delete_member(self, member_id):
            print(f"Master app: Request to delete member with ID: {member_id}")
            # Placeholder
            dialog = ctk.CTkToplevel(self)
            dialog.geometry("300x200")
            dialog.title("Confirm Delete (Placeholder)")
            label = ctk.CTkLabel(dialog, text=f"Confirm delete member: {member_id}?")
            label.pack(padx=20, pady=20)
        
        def update_status(self, message, success=True):
            print(f"Status Update: {message} (Success: {success})")

    app = App()
    app.mainloop()
import customtkinter as ctk
from . import styles # 新增

class MemberListView(ctk.CTkFrame):
    def __init__(self, master, library_instance, master_app, **kwargs):
        super().__init__(master, **kwargs)
        self.library_instance = library_instance
        self.master_app = master_app 

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(3, weight=1) # 修改: 为 info_label 和 header_frame 调整行号

        # --- Search Frame with multiple search types ---
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=styles.PAD_X_MEDIUM, pady=(styles.PAD_Y_MEDIUM, styles.PAD_Y_SMALL))
        search_frame.grid_columnconfigure(2, weight=1) 

        ctk.CTkLabel(search_frame, text="搜索类型:", font=styles.FONT_ENTRY_LABEL).pack(side="left", padx=(0,styles.PAD_X_SMALL))
        self.search_type_var = ctk.StringVar(value="会员ID")
        search_type_options = ["会员ID", "姓名", "电话"]
        self.search_type_menu = ctk.CTkOptionMenu(
            search_frame, 
            variable=self.search_type_var, 
            values=search_type_options,
            height=styles.HEIGHT_OPTIONMENU,
            corner_radius=styles.CORNER_RADIUS_BUTTON,
            font=styles.FONT_BUTTON
        )
        self.search_type_menu.pack(side="left", padx=styles.PAD_X_SMALL)

        ctk.CTkLabel(search_frame, text="关键词:", font=styles.FONT_ENTRY_LABEL).pack(side="left", padx=(styles.PAD_X_MEDIUM,styles.PAD_X_SMALL))
        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="输入搜索关键词...",
            height=styles.HEIGHT_ENTRY,
            corner_radius=styles.CORNER_RADIUS_ENTRY,
            font=styles.FONT_NORMAL
        )
        self.search_entry.pack(side="left", padx=styles.PAD_X_SMALL, fill="x", expand=True)
        self.search_entry.bind("<Return>", self.perform_search)

        search_button = ctk.CTkButton(
            search_frame, 
            text="搜索", 
            command=self.perform_search,
            height=styles.HEIGHT_BUTTON,
            width=80,
            corner_radius=styles.CORNER_RADIUS_BUTTON,
            font=styles.FONT_BUTTON,
            fg_color=styles.PRIMARY_COLOR,
            hover_color=styles.PRIMARY_COLOR_HOVER
        )
        search_button.pack(side="left", padx=styles.PAD_X_SMALL)
        
        clear_search_button = ctk.CTkButton(
            search_frame, 
            text="显示全部", 
            command=self.show_all_members,
            height=styles.HEIGHT_BUTTON,
            width=100,
            corner_radius=styles.CORNER_RADIUS_BUTTON,
            font=styles.FONT_BUTTON,
            fg_color=styles.SECONDARY_COLOR,
            hover_color=styles.SECONDARY_COLOR_HOVER
        )
        clear_search_button.pack(side="left", padx=(styles.PAD_X_SMALL,0))

        # --- Info Label for search results ---
        self.info_label = ctk.CTkLabel(self, text="", font=styles.FONT_NORMAL) # 使用styles.FONT_NORMAL
        self.info_label.grid(row=1, column=0, sticky="w", padx=styles.PAD_X_MEDIUM, pady=(styles.PAD_Y_SMALL, 0))
        
        # --- Header Frame for Table ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=2, column=0, sticky="ew", padx=styles.PAD_X_MEDIUM, pady=(styles.PAD_Y_SMALL,0))
        header_frame.grid_columnconfigure((0, 1, 2), weight=1) # 3 data columns
        header_frame.grid_columnconfigure(3, weight=0) # Action column

        headers = ["会员ID", "姓名", "电话", "操作"]
        for i, header_text in enumerate(headers):
            label = ctk.CTkLabel( # 修改: 应用统一表头样式
                header_frame,
                text=header_text,
                font=styles.FONT_TABLE_HEADER,
                fg_color=styles.PRIMARY_COLOR,
                text_color="white",
                corner_radius=styles.CORNER_RADIUS_TABLE_HEADER,
                padx=styles.PAD_X_MEDIUM,
                pady=styles.PAD_Y_SMALL
            )
            sticky_val = "ew"
            # if header_text == "操作": # Sticky "e" is fine for action column header too
            #     sticky_val = "e" 
            label.grid(row=0, column=i, padx=(0 if i == 0 else styles.PAD_X_SMALL, 0 if i == len(headers)-1 else styles.PAD_X_SMALL), pady=styles.PAD_Y_SMALL, sticky=sticky_val)


        # Scrollable Frame for member entries
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=3, column=0, sticky="nsew", padx=styles.PAD_X_MEDIUM, pady=(0,styles.PAD_Y_MEDIUM))
        self.scrollable_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.scrollable_frame.grid_columnconfigure(3, weight=0)


    def populate_table(self, members_data):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not members_data: # 修改: 更新info_label颜色
            self.info_label.configure(text="没有可显示的会员信息", text_color=styles.WARNING_COLOR)
            no_data_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="没有可显示的会员数据。",
                pady=styles.PAD_Y_LARGE,
                font=styles.FONT_LARGE_NORMAL,
                text_color=("gray60", "gray40")
            )
            no_data_label.grid(row=0, column=0, columnspan=4, sticky="ew")
            return
        
        self.info_label.configure(text=f"共找到 {len(members_data)} 位会员", text_color=styles.SUCCESS_COLOR) # 修改: 更新info_label颜色

        for i, member in enumerate(members_data):
            # 修改: 使用统一样式实现Zebra Striping
            row_fg_color = (styles.TABLE_ROW_LIGHT_EVEN, styles.TABLE_ROW_DARK_EVEN) if i % 2 == 0 else \
                           (styles.TABLE_ROW_LIGHT_ODD, styles.TABLE_ROW_DARK_ODD)
            row_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=row_fg_color, corner_radius=styles.CORNER_RADIUS_FRAME / 2 if styles.CORNER_RADIUS_FRAME else 0)
            row_frame.grid(row=i, column=0, columnspan=4, sticky="ew", pady=(styles.PAD_Y_SMALL / 2, styles.PAD_Y_SMALL / 2), padx=2)
            row_frame.grid_columnconfigure((0, 1, 2), weight=1)
            row_frame.grid_columnconfigure(3, weight=0)
            
            # Member ID
            member_id_label = ctk.CTkLabel(row_frame, text=member.member_id, anchor="w", font=styles.FONT_TABLE_CELL)
            member_id_label.grid(row=0, column=0, padx=styles.PAD_X_MEDIUM, pady=styles.PAD_Y_SMALL, sticky="ew")

            # Name
            name_label = ctk.CTkLabel(row_frame, text=member.member_name, anchor="w", font=styles.FONT_TABLE_CELL)
            name_label.grid(row=0, column=1, padx=styles.PAD_X_MEDIUM, pady=styles.PAD_Y_SMALL, sticky="ew")

            # Phone
            phone_label = ctk.CTkLabel(row_frame, text=member.phone, anchor="w", font=styles.FONT_TABLE_CELL)
            phone_label.grid(row=0, column=2, padx=styles.PAD_X_MEDIUM, pady=styles.PAD_Y_SMALL, sticky="ew")
            
            # Action buttons frame
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=3, padx=styles.PAD_X_SMALL, pady=0, sticky="e")
            
            edit_button = ctk.CTkButton( # 修改: 应用按钮样式
                actions_frame,
                text="修改",
                width=styles.WIDTH_TABLE_ROW_ACTION_BUTTON,
                height=styles.HEIGHT_TABLE_ROW_ACTION_BUTTON,
                corner_radius=styles.CORNER_RADIUS_BUTTON / 1.5,
                font=styles.FONT_BUTTON,
                fg_color=styles.SECONDARY_COLOR,
                hover_color=styles.SECONDARY_COLOR_HOVER,
                command=lambda m_id=member.member_id: self.master_app.open_edit_member_dialog(m_id)
            )
            edit_button.pack(side="left", padx=(0,styles.PAD_X_SMALL))

            delete_button = ctk.CTkButton( # 修改: 应用按钮样式
                actions_frame,
                text="删除",
                width=styles.WIDTH_TABLE_ROW_ACTION_BUTTON,
                height=styles.HEIGHT_TABLE_ROW_ACTION_BUTTON,
                corner_radius=styles.CORNER_RADIUS_BUTTON / 1.5,
                font=styles.FONT_BUTTON,
                fg_color=styles.DANGER_COLOR,
                hover_color=styles.DANGER_COLOR_HOVER,
                command=lambda m_id=member.member_id: self.master_app.confirm_delete_member(m_id)
            )
            delete_button.pack(side="left")

    def perform_search(self, event=None):
        keyword = self.search_entry.get().strip()
        search_type = self.search_type_var.get()
        
        if not keyword:
            self.info_label.configure(text=f"请输入{search_type}关键词进行搜索。", text_color=styles.WARNING_COLOR) # 修改: 更新info_label
            self.populate_table([])
            return

        found_members = []
        try:
            if search_type == "会员ID":
                member = self.library_instance.find_member_by_id(keyword) # find_member_by_id should raise MemberNotFoundError
                if member:
                    found_members = [member]
            elif search_type == "姓名":
                found_members = self.library_instance.find_members_by_name(keyword)
            elif search_type == "电话":
                found_members = self.library_instance.find_members_by_phone(keyword)
            
            self.populate_table(found_members) # populate_table内部会更新info_label
            
        except self.library_instance.MemberNotFoundError: # Assuming MemberNotFoundError is an exception in library_instance
             self.populate_table([]) # Show no results
             self.info_label.configure(text=f"未找到符合{search_type} '{keyword}' 的会员。", text_color=styles.WARNING_COLOR)
        except Exception as e:
            self.info_label.configure(text=f"搜索会员时发生错误: {e}", text_color=styles.DANGER_COLOR) # 修改: 更新info_label
            self.populate_table([])
            print(f"Member search error: {e}")

    def show_all_members(self):
        self.search_entry.delete(0, ctk.END)
        all_members_list = list(self.library_instance.members.values())
        self.populate_table(all_members_list) # populate_table内部会更新info_label
        self.search_type_var.set("会员ID")

if __name__ == '__main__':
    # Example Usage (for testing MemberListView independently)
    # Note: This test App needs to be updated to reflect style changes if run directly
    class App(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Member List View Test")
            self.geometry("800x600")

            # Mock styles for testing if styles.py is not fully integrated in this test
            class MockStyles:
                FONT_ENTRY_LABEL = ctk.CTkFont(size=12)
                FONT_BUTTON = ctk.CTkFont(size=12)
                FONT_TABLE_HEADER = ctk.CTkFont(size=14, weight="bold")
                FONT_TABLE_CELL = ctk.CTkFont(size=12)
                FONT_NORMAL = ctk.CTkFont(size=12)
                FONT_LARGE_NORMAL = ctk.CTkFont(size=14)

                PRIMARY_COLOR = "#3B8ED0"
                PRIMARY_COLOR_HOVER = "#36719F"
                SECONDARY_COLOR = "#6c757d"
                SECONDARY_COLOR_HOVER = "#545b62"
                DANGER_COLOR = "#dc3545"
                DANGER_COLOR_HOVER = "#C82333"
                SUCCESS_COLOR = "#28a745"
                WARNING_COLOR = "#ffc107"
                
                TABLE_ROW_LIGHT_EVEN = "gray92"
                TABLE_ROW_LIGHT_ODD = "gray98"
                TABLE_ROW_DARK_EVEN = "gray22"
                TABLE_ROW_DARK_ODD = "gray18"

                PAD_X_SMALL = 5
                PAD_Y_SMALL = 5
                PAD_X_MEDIUM = 10
                PAD_Y_MEDIUM = 10
                PAD_Y_LARGE = 20
                
                HEIGHT_BUTTON = 30
                HEIGHT_ENTRY = 30
                HEIGHT_OPTIONMENU = 30
                HEIGHT_TABLE_ROW_ACTION_BUTTON = 28
                WIDTH_TABLE_ROW_ACTION_BUTTON = 60
                
                CORNER_RADIUS_BUTTON = 6
                CORNER_RADIUS_ENTRY = 6
                CORNER_RADIUS_FRAME = 0 
                CORNER_RADIUS_TABLE_HEADER = 6
            
            global styles # Allow mocking global styles for test
            _original_styles = styles
            styles = MockStyles()

            class MockMember:
                def __init__(self, member_id, member_name, phone):
                    self.member_id = member_id
                    self.member_name = member_name
                    self.phone = phone
            
            class MockLibrary:
                MemberNotFoundError = type('MemberNotFoundError', (Exception,), {}) # Mock exception

                def __init__(self):
                    self.members = {
                        "M001": MockMember("M001", "张三", "13800138000"),
                        "M002": MockMember("M002", "李四", "13900139000"),
                        "M003": MockMember("M003", "王五", "13700137000")
                    }
                def find_member_by_id(self, member_id):
                    member = self.members.get(member_id)
                    if not member:
                        raise self.MemberNotFoundError(f"Member {member_id} not found")
                    return member
                def find_members_by_name(self, name_keyword):
                    return [m for m in self.members.values() if name_keyword.lower() in m.member_name.lower()]
                def find_members_by_phone(self, phone_keyword):
                    return [m for m in self.members.values() if phone_keyword in m.phone]


            self.library_instance = MockLibrary()
            
            self.member_list_view = MemberListView(self, library_instance=self.library_instance, master_app=self)
            self.member_list_view.pack(fill="both", expand=True, padx=10, pady=10)
            
            self.member_list_view.populate_table(list(self.library_instance.members.values()))

            styles = _original_styles # Restore original styles


        def open_edit_member_dialog(self, member_id):
            print(f"Master app: Request to edit member with ID: {member_id}")
        def confirm_delete_member(self, member_id):
            print(f"Master app: Request to delete member with ID: {member_id}")
        def update_status(self, message, success=True): # Mock for testing
            print(f"Status Update: {message} (Success: {success})")

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
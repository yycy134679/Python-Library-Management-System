import customtkinter as ctk
from tkinter import messagebox
from src.core_logic.library_member import LibraryMember
from src.core_logic import exceptions
from . import styles # 新增

class AddMemberDialog(ctk.CTkToplevel):
    def __init__(self, master, library_instance):
        super().__init__(master)
        self.master_app = master 
        self.library_instance = library_instance

        self.title("添加新会员")
        self.geometry("450x360") # 修改: 调整尺寸
        self.resizable(False, False)
        self.grab_set() 

        self.grid_columnconfigure(0, weight=1) # Make content_frame expand
        self.grid_rowconfigure(0, weight=1)    # Make content_frame expand

        # 为内容区域添加统一边距
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=styles.PAD_X_LARGE, pady=styles.PAD_Y_LARGE)
        content_frame.grid_columnconfigure(1, weight=1)

        # --- Input Fields ---
        row_num = 0
        ctk.CTkLabel(content_frame, text="会员ID:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.member_id_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.member_id_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")
        self.member_id_entry.focus()

        row_num += 1
        ctk.CTkLabel(content_frame, text="姓名:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.name_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.name_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")

        row_num += 1
        ctk.CTkLabel(content_frame, text="电话:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.phone_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.phone_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")
        
        # --- Error Label ---
        row_num += 1
        self.error_label = ctk.CTkLabel(
            content_frame, 
            text="", 
            font=styles.FONT_ERROR_TEXT,
            text_color=styles.DANGER_COLOR,
            fg_color=(styles.ERROR_BG_LIGHT, styles.ERROR_BG_DARK),
            corner_radius=styles.CORNER_RADIUS_ERROR_LABEL,
            wraplength=380
        )
        self.error_label.grid(row=row_num, column=0, columnspan=2, pady=(styles.PAD_Y_SMALL, styles.PAD_Y_MEDIUM), padx=0, sticky="ew")
        self.error_label.grid_remove() # Initially hidden

        # --- Buttons ---
        row_num += 1
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.grid(row=row_num, column=0, columnspan=2, pady=(styles.PAD_Y_MEDIUM, 0), sticky="e")

        confirm_button = ctk.CTkButton(
            button_frame, 
            text="确认添加", 
            command=self.confirm_add,
            height=styles.HEIGHT_BUTTON,
            corner_radius=styles.CORNER_RADIUS_BUTTON,
            font=styles.FONT_BUTTON,
            fg_color=styles.PRIMARY_COLOR,
            hover_color=styles.PRIMARY_COLOR_HOVER
        )
        confirm_button.pack(side="right", padx=(styles.PAD_X_SMALL, 0))

        cancel_button = ctk.CTkButton(
            button_frame, 
            text="取消", 
            command=self.destroy, 
            height=styles.HEIGHT_BUTTON,
            corner_radius=styles.CORNER_RADIUS_BUTTON,
            font=styles.FONT_BUTTON,
            fg_color=styles.SECONDARY_COLOR,
            hover_color=styles.SECONDARY_COLOR_HOVER
        )
        cancel_button.pack(side="right", padx=(0, styles.PAD_X_SMALL))

    def _show_error(self, message):
        self.error_label.configure(text=message)
        self.error_label.grid()

    def _clear_error(self):
        self.error_label.grid_remove()
        self.error_label.configure(text="")

    def confirm_add(self):
        self._clear_error()
        member_id = self.member_id_entry.get().strip()
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()

        if not all([member_id, name, phone]):
            self._show_error("错误：会员ID、姓名和电话均为必填项。")
            return
        
        try:
            new_member = LibraryMember(member_id=member_id, member_name=name, phone=phone)
            self.library_instance.add_member(new_member)
            self.library_instance.save_members_to_csv("data/members.csv") 
            
            self.master_app.update_status(f"会员 '{name}' (ID: {member_id}) 添加成功并已保存。", success=True)
            if hasattr(self.master_app, 'switch_view') and callable(getattr(self.master_app, 'switch_view')):
                self.master_app.switch_view("all_members") 
            self.destroy() 

        except exceptions.MemberAlreadyExistsError:
            self._show_error(f"错误：会员ID '{member_id}' 已存在。")
        except Exception as e:
            self._show_error(f"添加会员时发生未知错误: {e}")
            print(f"Error adding member: {e}")

# if __name__ == '__main__':
    # ... (Test code removed for brevity, but should be updated if used)

class EditMemberDialog(ctk.CTkToplevel):
    def __init__(self, master, library_instance, member_id_to_edit):
        super().__init__(master)
        self.master_app = master
        self.library_instance = library_instance
        self.member_id_to_edit = member_id_to_edit
        
        try:
            self.member_to_edit = self.library_instance.find_member_by_id(self.member_id_to_edit)
            if not self.member_to_edit:
                 raise exceptions.MemberNotFoundError(f"未找到会员ID为 {self.member_id_to_edit} 的会员。")
        except exceptions.MemberNotFoundError as e:
            messagebox.showerror("错误", str(e), parent=self)
            self.after(100, self.destroy)
            return

        self.title("修改会员信息")
        self.geometry("450x390") # 修改: 调整尺寸
        self.resizable(False, False)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(0, weight=1)   

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=styles.PAD_X_LARGE, pady=styles.PAD_Y_LARGE)
        content_frame.grid_columnconfigure(1, weight=1)

        # --- Input Fields ---
        row_num = 0
        ctk.CTkLabel(content_frame, text="会员ID:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.member_id_label = ctk.CTkLabel(content_frame, text=self.member_to_edit.member_id, font=styles.FONT_NORMAL)
        self.member_id_label.grid(row=row_num, column=1, padx=0, pady=styles.PAD_Y_MEDIUM, sticky="ew")

        row_num += 1
        ctk.CTkLabel(content_frame, text="姓名:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.name_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.name_entry.insert(0, self.member_to_edit.member_name)
        self.name_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")
        self.name_entry.focus()

        row_num += 1
        ctk.CTkLabel(content_frame, text="电话:", font=styles.FONT_ENTRY_LABEL).grid(row=row_num, column=0, padx=(0, styles.PAD_X_MEDIUM), pady=styles.PAD_Y_MEDIUM, sticky="w")
        self.phone_entry = ctk.CTkEntry(content_frame, height=styles.HEIGHT_ENTRY, corner_radius=styles.CORNER_RADIUS_ENTRY, font=styles.FONT_NORMAL)
        self.phone_entry.insert(0, self.member_to_edit.phone)
        self.phone_entry.grid(row=row_num, column=1, pady=styles.PAD_Y_MEDIUM, sticky="ew")
        
        # --- Error Label ---
        row_num += 1
        self.error_label = ctk.CTkLabel(
            content_frame, 
            text="", 
            font=styles.FONT_ERROR_TEXT,
            text_color=styles.DANGER_COLOR,
            fg_color=(styles.ERROR_BG_LIGHT, styles.ERROR_BG_DARK),
            corner_radius=styles.CORNER_RADIUS_ERROR_LABEL,
            wraplength=380
        )
        self.error_label.grid(row=row_num, column=0, columnspan=2, pady=(styles.PAD_Y_SMALL, styles.PAD_Y_MEDIUM), padx=0, sticky="ew")
        self.error_label.grid_remove() 

        # --- Buttons ---
        row_num += 1
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.grid(row=row_num, column=0, columnspan=2, pady=(styles.PAD_Y_MEDIUM, 0), sticky="e")

        confirm_button = ctk.CTkButton(
            button_frame, 
            text="确认修改", 
            command=self.confirm_edit,
            height=styles.HEIGHT_BUTTON,
            corner_radius=styles.CORNER_RADIUS_BUTTON,
            font=styles.FONT_BUTTON,
            fg_color=styles.PRIMARY_COLOR,
            hover_color=styles.PRIMARY_COLOR_HOVER
        )
        confirm_button.pack(side="right", padx=(styles.PAD_X_SMALL, 0))

        cancel_button = ctk.CTkButton(
            button_frame, 
            text="取消", 
            command=self.destroy,
            height=styles.HEIGHT_BUTTON,
            corner_radius=styles.CORNER_RADIUS_BUTTON,
            font=styles.FONT_BUTTON,
            fg_color=styles.SECONDARY_COLOR,
            hover_color=styles.SECONDARY_COLOR_HOVER
        )
        cancel_button.pack(side="right", padx=(0, styles.PAD_X_SMALL))

    def _show_error(self, message):
        self.error_label.configure(text=message)
        self.error_label.grid()

    def _clear_error(self):
        self.error_label.grid_remove()
        self.error_label.configure(text="")

    def confirm_edit(self):
        self._clear_error()
        new_name = self.name_entry.get().strip()
        new_phone = self.phone_entry.get().strip()

        if not all([new_name, new_phone]):
            self._show_error("错误：姓名和电话不能为空。")
            return

        try:
            self.library_instance.modify_member_details(
                member_id=self.member_id_to_edit,
                name=new_name,
                phone=new_phone
            )
            self.library_instance.save_members_to_csv("data/members.csv") 
            
            self.master_app.update_status(f"会员 '{new_name}' (ID: {self.member_id_to_edit}) 修改成功并已保存。", success=True)
            if hasattr(self.master_app, 'switch_view') and callable(getattr(self.master_app, 'switch_view')):
                self.master_app.switch_view("all_members") 
            self.destroy()

        except exceptions.MemberNotFoundError: 
            self._show_error(f"错误：尝试修改时未找到会员ID '{self.member_id_to_edit}'。")
        except Exception as e:
            self._show_error(f"修改会员时发生未知错误: {e}")
            print(f"Error editing member: {e}")

if __name__ == '__main__': # Minimal test setup
    class MockMasterApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Member Dialog Test App")
            # Mock library and styles for testing
            class MockMember:
                def __init__(self, member_id, member_name, phone):
                    self.member_id, self.member_name, self.phone = member_id, member_name, phone
            class MockLibrary:
                MemberNotFoundError = exceptions.MemberNotFoundError
                MemberAlreadyExistsError = exceptions.MemberAlreadyExistsError
                def __init__(self): self.members = {"M123": MockMember("M123", "Old Name", "12345")}
                def add_member(self, member):
                    if member.member_id in self.members: raise self.MemberAlreadyExistsError()
                    self.members[member.member_id] = member
                def find_member_by_id(self, member_id):
                    m = self.members.get(member_id)
                    if not m: raise self.MemberNotFoundError()
                    return m
                def modify_member_details(self, member_id, name, phone):
                    member = self.find_member_by_id(member_id)
                    member.member_name, member.phone = name, phone
                def save_members_to_csv(self, _path): print("Mock save members")

            self.library_instance = MockLibrary()
            ctk.CTkButton(self, text="Open Add Member", command=lambda: AddMemberDialog(self, self.library_instance)).pack(pady=10)
            ctk.CTkButton(self, text="Open Edit Member (M123)", command=lambda: EditMemberDialog(self, self.library_instance, "M123")).pack(pady=10)

        def update_status(self, msg, success): print(f"Status: {msg} (Success: {success})")
        def switch_view(self, view): print(f"Switch to: {view}")
    
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = MockMasterApp()
    app.mainloop()
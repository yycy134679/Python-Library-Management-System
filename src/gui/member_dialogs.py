import customtkinter as ctk
from tkinter import messagebox
from src.core_logic.library_member import LibraryMember
from src.core_logic import exceptions

class AddMemberDialog(ctk.CTkToplevel):
    def __init__(self, master, library_instance):
        super().__init__(master)
        self.master_app = master # Reference to the main LibraryApp instance
        self.library_instance = library_instance

        self.title("添加新会员")
        self.geometry("400x300") 
        self.resizable(False, False)
        self.grab_set() # Make dialog modal

        self.grid_columnconfigure(1, weight=1)

        # --- Input Fields ---
        row_num = 0
        ctk.CTkLabel(self, text="会员ID:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.member_id_entry = ctk.CTkEntry(self, width=200)
        self.member_id_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")
        self.member_id_entry.focus()

        row_num += 1
        ctk.CTkLabel(self, text="姓名:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.name_entry = ctk.CTkEntry(self, width=200)
        self.name_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")

        row_num += 1
        ctk.CTkLabel(self, text="电话:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.phone_entry = ctk.CTkEntry(self, width=200)
        self.phone_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")
        
        # --- Error Label ---
        row_num += 1
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.grid(row=row_num, column=0, columnspan=2, padx=10, pady=(0,5), sticky="ew")

        # --- Buttons ---
        row_num += 1
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=row_num, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        button_frame.grid_columnconfigure((0,1), weight=1)

        confirm_button = ctk.CTkButton(button_frame, text="确认添加", command=self.confirm_add)
        confirm_button.grid(row=0, column=0, padx=(0,5), pady=5, sticky="e")

        cancel_button = ctk.CTkButton(button_frame, text="取消", command=self.destroy, fg_color="gray")
        cancel_button.grid(row=0, column=1, padx=(5,0), pady=5, sticky="w")

    def confirm_add(self):
        self.error_label.configure(text="") # Clear previous errors
        member_id = self.member_id_entry.get().strip()
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()

        # --- Frontend Validation ---
        if not all([member_id, name, phone]):
            self.error_label.configure(text="错误：会员ID、姓名和电话均为必填项。")
            return
        
        # Basic phone validation (e.g., digits only, length) can be added here if needed.

        try:
            new_member = LibraryMember(member_id=member_id, member_name=name, phone=phone)
            self.library_instance.add_member(new_member)
            self.library_instance.save_members_to_csv("data/members.csv") # Save after adding
            
            self.master_app.update_status(f"会员 '{name}' (ID: {member_id}) 添加成功并已保存。", success=True)
            self.master_app.switch_view("all_members") # Refresh the member list
            self.destroy() # Close dialog

        except exceptions.MemberAlreadyExistsError:
            self.error_label.configure(text=f"错误：会员ID '{member_id}' 已存在。")
        except Exception as e:
            self.error_label.configure(text=f"添加会员时发生未知错误: {e}")
            print(f"Error adding member: {e}")

# Example Usage (for testing AddMemberDialog independently)
if __name__ == '__main__':
    class MockLibraryApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Member Dialog Test Host")
            self.geometry("300x200")

            class MockLibrary:
                def __init__(self):
                    self.members = {}
                def add_member(self, member):
                    if member.member_id in self.members:
                        raise exceptions.MemberAlreadyExistsError(f"ID {member.member_id} already exists.")
                    self.members[member.member_id] = member
                    print(f"MockLibrary: Member '{member.member_name}' added.")
                def save_members_to_csv(self, filename):
                    print(f"MockLibrary: Pretending to save members to {filename}")
                def get_all_members(self): # Not directly used by dialog but for host app
                    return list(self.members.values())

            self.library_instance = MockLibrary()
            
            button = ctk.CTkButton(self, text="Open Add Member Dialog", command=self.open_dialog)
            button.pack(pady=20)

        def open_dialog(self):
            dialog = AddMemberDialog(self, self.library_instance)

        def update_status(self, message, success=True):
            print(f"Host Status: {message} (Success: {success})")

        def switch_view(self, view_name):
            print(f"Host: Switch to view '{view_name}' requested.")

    app = MockLibraryApp()
    app.mainloop()


class EditMemberDialog(ctk.CTkToplevel):
    def __init__(self, master, library_instance, member_id_to_edit):
        super().__init__(master)
        self.master_app = master
        self.library_instance = library_instance
        self.member_id_to_edit = member_id_to_edit
        self.member_to_edit = self.library_instance.find_member_by_id(self.member_id_to_edit)

        self.title("修改会员信息")
        self.geometry("400x330")
        self.resizable(False, False)
        self.grab_set()

        if not self.member_to_edit:
            messagebox.showerror("错误", f"未找到会员ID为 {self.member_id_to_edit} 的会员。", parent=self)
            self.after(100, self.destroy)
            return

        self.grid_columnconfigure(1, weight=1)

        # --- Input Fields ---
        row_num = 0
        ctk.CTkLabel(self, text="会员ID:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.member_id_label = ctk.CTkLabel(self, text=self.member_to_edit.member_id)
        self.member_id_label.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")

        row_num += 1
        ctk.CTkLabel(self, text="姓名:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.name_entry = ctk.CTkEntry(self, width=200)
        self.name_entry.insert(0, self.member_to_edit.member_name)
        self.name_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")
        self.name_entry.focus()

        row_num += 1
        ctk.CTkLabel(self, text="电话:").grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        self.phone_entry = ctk.CTkEntry(self, width=200)
        self.phone_entry.insert(0, self.member_to_edit.phone)
        self.phone_entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")
        
        # --- Error Label ---
        row_num += 1
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.grid(row=row_num, column=0, columnspan=2, padx=10, pady=(0,5), sticky="ew")

        # --- Buttons ---
        row_num += 1
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=row_num, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        button_frame.grid_columnconfigure((0,1), weight=1)

        confirm_button = ctk.CTkButton(button_frame, text="确认修改", command=self.confirm_edit)
        confirm_button.grid(row=0, column=0, padx=(0,5), pady=5, sticky="e")

        cancel_button = ctk.CTkButton(button_frame, text="取消", command=self.destroy, fg_color="gray")
        cancel_button.grid(row=0, column=1, padx=(5,0), pady=5, sticky="w")

    def confirm_edit(self):
        self.error_label.configure(text="")
        new_name = self.name_entry.get().strip()
        new_phone = self.phone_entry.get().strip()

        if not all([new_name, new_phone]):
            self.error_label.configure(text="错误：姓名和电话不能为空。")
            return

        try:
            self.library_instance.modify_member_details(
                member_id=self.member_id_to_edit,
                name=new_name,
                phone=new_phone
            )
            self.library_instance.save_members_to_csv("data/members.csv") # Save after modifying
            
            self.master_app.update_status(f"会员 '{new_name}' (ID: {self.member_id_to_edit}) 修改成功并已保存。", success=True)
            self.master_app.switch_view("all_members") # Refresh list
            self.destroy()

        except exceptions.MemberNotFoundError: # Should be caught by initial check, but good practice
            self.error_label.configure(text=f"错误：尝试修改时未找到会员ID '{self.member_id_to_edit}'。")
        except Exception as e:
            self.error_label.configure(text=f"修改会员时发生未知错误: {e}")
            print(f"Error editing member: {e}")
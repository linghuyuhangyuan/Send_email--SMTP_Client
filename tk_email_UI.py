import tkinter as tk
from tkinter import simpledialog, messagebox
from client import Client
import base64
from socket import *
from email.base64mime import body_encode
from typing import Tuple

class EmailClientUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("邮件客户端")
        self.msg = "new test!"
        self.CRLF = "\r\n"
        self.endMsg = "\r\n.\r\n"
        self.mailServer = "smtp.163.com"
        self.serverPort = 25
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.clientSocket.connect((self.mailServer, self.serverPort))
        self.client = Client(self.clientSocket)

        self.username = ""
        self.password = ""

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="用户名：").grid(row=0, column=0, sticky="e")
        tk.Label(self.root, text="授权码：").grid(row=1, column=0, sticky="e")

        self.username_entry = tk.Entry(self.root)
        self.password_entry = tk.Entry(self.root, show="*")

        self.username_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.root, text="登录", command=self.login).grid(row=2, column=1, pady=10)

    def login(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        
        self.client.hello()
        if self.client.auth_login(self.username, self.password) == False:
            messagebox.showerror("错误", "请填写正确的用户名和授权码。")
        else:
            # 隐藏登录窗口，显示主菜单
            self.root.withdraw()
            self.show_main_menu()

    def show_login_page(self):
        # Show login page
        self.root.deiconify()
        self.root.title("邮件客户端")
        self.username_entry.delete(0, tk.END)  # Clear the username entry
        self.password_entry.delete(0, tk.END)  # Clear the password entry

    def show_main_menu(self):
        
        self.main_menu = tk.Toplevel(self.root)
        self.main_menu.title("主菜单")

        # Welcome message at the top
        welcome_label = tk.Label(self.main_menu, text=f"欢迎您，{self.username}")
        welcome_label.pack(pady=10)

        choices = [
            "发送邮件",
            "更换账号",
            "查看已发送邮件",
            "编辑邮件",
            "查看草稿箱",
            "添加联系人",
            "查看联系人",
            "退出"
        ]

        for i, choice in enumerate(choices):
            tk.Button(self.main_menu, text=choice, command=lambda c=i: self.handle_menu_choice(c)).pack(pady=5)
        
        # if current_window is not None:
        #     current_window.destroy()
        
    def close_window(self, window):
        window.destroy()

    def save_draft(self, title, content):
        self.client.store_in_drafts(title, content)
        messagebox.showinfo("保存成功", "邮件保存成功！")
    
    def save_contact(self, name, address):
        self.client.add_contact(name, address)
        messagebox.showinfo("保存成功", "联系人信息保存成功！")
        
    def send_email_window(self):
        # 创建一个新窗口用于编辑邮件
        compose_mail_window = tk.Toplevel(self.root)
        compose_mail_window.title("编辑邮件")

        # 输入框和标签：收件人邮箱、邮件标题、邮件内容
        to_label = tk.Label(compose_mail_window, text="收件人邮箱:")
        to_label.pack(pady=5)
        to_entry = tk.Entry(compose_mail_window)
        to_entry.pack(pady=5)

        subject_label = tk.Label(compose_mail_window, text="邮件标题:")
        subject_label.pack(pady=5)
        subject_entry = tk.Entry(compose_mail_window)
        subject_entry.pack(pady=5)

        content_label = tk.Label(compose_mail_window, text="邮件内容:")
        content_label.pack(pady=5)
        content_text = tk.Text(compose_mail_window, height=10, width=50)
        content_text.pack(pady=5)

        # 按钮：导入草稿箱、导入联系人、发送邮件
        import_draft_button = tk.Button(compose_mail_window, text="从草稿箱导入", command=lambda: self.import_from_draft(compose_mail_window, subject_entry, content_text))
        import_draft_button.pack(pady=5)

        import_contact_button = tk.Button(compose_mail_window, text="从联系人信息导入", command=lambda: self.import_from_contact(compose_mail_window, to_entry))
        import_contact_button.pack(pady=5)

        send_button = tk.Button(compose_mail_window, text="发送邮件", command=lambda: self.send_mail(self.username, to_entry.get(), subject_entry.get(), content_text.get("1.0", "end-1c")))
        send_button.pack(pady=10)

        # 返回主菜单按钮
        return_button = tk.Button(compose_mail_window, text="返回主菜单", command=lambda: [self.show_main_menu(), self.close_window(compose_mail_window)])
        return_button.pack(pady=10)
        
    def send_mail(self, fromAddress, toAddresses, sub, content):
        to_list = [addr.strip() for addr in toAddresses.split(';')]
        print(to_list)
        for toAddress in to_list:
            if toAddress != "":
                self.client.send_mail(fromAddress, toAddress, sub, content)
        messagebox.showinfo("提示", "邮件发送成功")
        
    def import_from_draft(self, window, subject_entry, content_text):
        draft_mails_window = tk.Toplevel(self.root)
        draft_mails_window.title("草稿箱邮件")
        
        # 添加一个文本框用于选择联系人编号
        select_label = tk.Label(draft_mails_window, text="请输入邮件编号:")
        select_label.pack(pady=5)
        select_entry = tk.Entry(draft_mails_window)
        select_entry.pack(pady=5)
            
        # 显示草稿箱的邮件
        for i, draft_mail in enumerate(self.client.get_drafts()):
            mail_title_label = tk.Label(draft_mails_window, text=f"mail{i} 标题: {draft_mail['sub']}")
            mail_title_label.pack(pady=5)
                
            mail_content_label = tk.Label(draft_mails_window, text=f"内容: {draft_mail['msg']}")
            mail_content_label.pack(pady=5)
            
        # 添加一个按钮返回主菜单
        back_button = tk.Button(draft_mails_window, text="导入", command=lambda: [self.write_entry_draft(subject_entry, content_text, select_entry), self.close_window(draft_mails_window)])
        back_button.pack(pady=10)
    
    def write_entry_draft(self, subject_entry, content_text, no_entry):
        try:
            selected_index = int(no_entry.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的草稿箱邮件编号。")
        
        print(selected_index)
        if self.client.get_draft(selected_index) is None:
            messagebox.showerror("错误", "请输入有效的草稿箱邮件编号。")
        else:
            (sub, msg) = self.client.get_draft(selected_index)
        subject_entry.delete(0, tk.END)
        content_text.delete("1.0", tk.END)
        subject_entry.insert(0, sub)
        content_text.insert("1.0", msg)

    def import_from_contact(self, window, to_entry):
        contacts_window = tk.Toplevel(self.root)
        contacts_window.title("联系人列表")
        
        # 添加一个文本框用于选择联系人编号
        select_label = tk.Label(contacts_window, text="请输入联系人名字:")
        select_label.pack(pady=5)
        select_entry = tk.Entry(contacts_window)
        select_entry.pack(pady=5)
            
        # 显示联系人
        for i, (name, addr) in enumerate(self.client.get_contacts().items()):
            contact_label = tk.Label(contacts_window, text=f"联系人{i}:\n姓名: {name}\n邮件地址: {addr}")
            contact_label.pack(pady=5)

        # 添加一个按钮返回主菜单
        back_button = tk.Button(contacts_window, text="导入", command=lambda: [self.write_entry_contact(to_entry, select_entry), self.close_window(contacts_window)])
        back_button.pack(pady=10)
        
    def write_entry_contact(self, to_entry, no_entry):
        try:
            selected_name = no_entry.get()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的联系人名字。")
        address = self.client.get_contact(selected_name)
        if address is None:
            messagebox.showerror("错误", "没有找到该联系人。")
        to_entry.insert(tk.END, address+";")

    def edit_mail_window(self):
        # Create a new window for editing emails
        edit_window = tk.Toplevel(self.root)
        edit_window.title("编辑邮件")

        # Entry for mail title
        title_label = tk.Label(edit_window, text="邮件标题:")
        title_label.pack(pady=5)
        title_entry = tk.Entry(edit_window)
        title_entry.pack(pady=5)

        # Text area for mail content
        content_label = tk.Label(edit_window, text="邮件内容:")
        content_label.pack(pady=5)
        content_text = tk.Text(edit_window, height=10, width=40)
        content_text.pack(pady=5)

        # Button to save and return
        save_button = tk.Button(edit_window, text="保存到草稿箱", command=lambda: self.save_draft(title_entry.get(), content_text.get("1.0", tk.END)))
        save_button.pack(pady=10)

        return_button = tk.Button(edit_window, text="返回主菜单", command=lambda: [self.show_main_menu(), self.close_window(edit_window)])
        return_button.pack(pady=10)
        
    def show_contact_window(self):
        # 创建一个新窗口显示联系人
        contacts_window = tk.Toplevel(self.root)
        contacts_window.title("联系人列表")
            
        # 显示联系人
        for i, (name, addr) in enumerate(self.client.get_contacts().items()):
            contact_label = tk.Label(contacts_window, text=f"联系人{i}:\n姓名: {name}\n邮件地址: {addr}")
            contact_label.pack(pady=5)
            
        # 添加一个按钮返回主菜单
        back_button = tk.Button(contacts_window, text="返回主菜单", command=lambda: [self.show_main_menu(), self.close_window(contacts_window)])
        back_button.pack(pady=10)
    
    def show_sent_emails(self):
        # Create a new window for displaying sent emails
        sent_mails_window = tk.Toplevel(self.root)
        sent_mails_window.title("已发送邮件")
            
        # Display sent emails
        for i, sent_mail in enumerate(self.client.get_sent_mails()):
            mail_label = tk.Label(sent_mails_window, text=f"mail{i}:\n{sent_mail['cont']}")
            mail_label.pack(pady=5)
                
        # Add a button to go back to the main menu
        back_button = tk.Button(sent_mails_window, text="返回主菜单", command=lambda: [self.show_main_menu(), self.close_window(sent_mails_window)])
        back_button.pack(pady=10)
        
    def show_draft_mails(self):
        # 创建一个新窗口显示草稿箱的邮件
        draft_mails_window = tk.Toplevel(self.root)
        draft_mails_window.title("草稿箱邮件")
            
        # 显示草稿箱的邮件
        for i, draft_mail in enumerate(self.client.get_drafts()):
            mail_title_label = tk.Label(draft_mails_window, text=f"mail{i} 标题: {draft_mail['sub']}")
            mail_title_label.pack(pady=5)
                
            mail_content_label = tk.Label(draft_mails_window, text=f"内容: {draft_mail['msg']}")
            mail_content_label.pack(pady=5)
            
        # 添加一个按钮返回主菜单
        back_button = tk.Button(draft_mails_window, text="返回主菜单", command=lambda: [self.show_main_menu(), self.close_window(draft_mails_window)])
        back_button.pack(pady=10)
            
    def add_contact_window(self):
        # 创建一个新窗口用于添加联系人
        add_contact_window = tk.Toplevel(self.root)
        add_contact_window.title("添加联系人")

        # 输入联系人姓名和地址
        name_label = tk.Label(add_contact_window, text="姓名:")
        name_label.pack(pady=5)
        name_entry = tk.Entry(add_contact_window)
        name_entry.pack(pady=5)

        address_label = tk.Label(add_contact_window, text="邮件地址:")
        address_label.pack(pady=5)
        address_entry = tk.Entry(add_contact_window)
        address_entry.pack(pady=5)

        # 添加按钮保存联系人并返回主菜单
        save_button = tk.Button(add_contact_window, text="保存联系人", command=lambda: self.save_contact(name_entry.get(), address_entry.get()))
        save_button.pack(pady=10)

        return_button = tk.Button(add_contact_window, text="返回主菜单", command=lambda: [self.show_main_menu(), self.close_window(add_contact_window)])
        return_button.pack(pady=10)
        
    def handle_menu_choice(self, choice):
        if choice == 0:
            print("用户选择发送邮件")
            self.main_menu.destroy()
            self.send_email_window()
            
        elif choice == 1:
            print("用户选择更换账号")
            self.main_menu.destroy()
            self.client.quit()
            self.client.close_connect()
            self.__init__()
            
        elif choice == 2:
            print("用户选择查看已发送邮件")
            self.main_menu.destroy()
            self.show_sent_emails()
            
        elif choice == 3:
            print("用户选择编辑邮件")
            self.main_menu.destroy()
            self.edit_mail_window()
        
        elif choice == 4:
            print("用户选择查看草稿箱邮件")
            self.main_menu.destroy()
            self.show_draft_mails()
            
        elif choice == 5:
            print("用户选择添加联系人")
            self.main_menu.destroy()
            self.add_contact_window()
            
        elif choice == 6:
            print("用户选择查看联系人")
            self.main_menu.destroy()
            self.show_contact_window()
            
        elif choice == 7:
            print("用户选择退出")
            self.client.quit()
            self.client.close_connect()
            self.root.deiconify()  
            self.root.destroy()
            exit(0)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    email_client_ui = EmailClientUI()
    email_client_ui.run()

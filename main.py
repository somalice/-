#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网商园图片下载 - tkinter版本
"""
import sys
import os

# 直接使用tkinter版本
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

import logging
from datetime import datetime
import subprocess
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.downloader import WSYDownloader
from src.logger import setup_logger

# Chrome配置
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_PROFILE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chrome_profile")
DEBUG_PORT = 9222
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "downloads")

os.makedirs(CHROME_PROFILE_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# tkinter版本
class TextRedirector:
    def __init__(self, widget):
        self.widget = widget
    
    def write(self, text):
        self.widget.insert(tk.END, text)
        self.widget.see(tk.END)
        self.widget.update()
    
    def flush(self):
        pass

class TkinterLogHandler(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.widget = widget

    def emit(self, record):
        try:
            msg = self.format(record) + '\n'
            self.widget.insert(tk.END, msg)
            self.widget.see(tk.END)
            self.widget.update()
        except Exception:
            self.widget.insert(tk.END, '日志输出错误\n')
            self.widget.see(tk.END)
            self.widget.update()

class DownloadGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("网商园图片下载")
        self.root.geometry("1050x720")
        self.root.minsize(950, 650)
        self.root.configure(bg="#f0f2f5")
        
        self.is_running = False
        self.should_stop = False
        self.downloader = WSYDownloader(DOWNLOAD_DIR)
        self.setup_ui()
        self.setup_logger()
    
    def setup_ui(self):
        main_container = tk.Frame(self.root, bg="#f0f2f5")
        main_container.pack(fill="both", expand=True, padx=25, pady=25)
        
        header = tk.Frame(main_container, bg="#f0f2f5")
        header.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(header, text="网商园图片下载", 
                               font=("Microsoft YaHei UI", 22, "bold"), 
                               fg="#1a1a1a", bg="#f0f2f5")
        title_label.pack()
        
        subtitle = tk.Label(header, text="一键下载，轻松使用", 
                           font=("Microsoft YaHei UI", 12), 
                           fg="#666", bg="#f0f2f5")
        subtitle.pack(pady=(5, 0))
        
        content_container = tk.Frame(main_container, bg="#f0f2f5")
        content_container.pack(fill="both", expand=True)
        
        left_frame = tk.Frame(content_container, bg="#f0f2f5")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_frame = tk.Frame(content_container, bg="#ffffff", 
                               relief=tk.FLAT, borderwidth=1)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        tk.Label(right_frame, text="操作日志", 
                font=("Microsoft YaHei UI", 11, "bold"), 
                fg="#4a5568", bg="#ffffff").pack(pady=(12, 0), anchor="w", padx=15)
        
        tk.Frame(right_frame, height=1, bg="#e2e8f0").pack(fill="x", pady=10, padx=10)
        
        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)
        
        self.log("程序已启动！")
        self.log("\n请按以下步骤操作：")
        self.log("1. 点击「启动 Chrome」")
        self.log("2. 在 Chrome 中登录网商园")
        self.log("3. 填入店铺链接")
        self.log("4. 点击「开始下载」")
    
    def setup_left_panel(self, parent):
        card1 = tk.Frame(parent, bg="#ffffff", relief=tk.FLAT, borderwidth=1)
        card1.pack(fill="x", pady=8)
        
        card1_header = tk.Frame(card1, bg="#3b82f6")
        card1_header.pack(fill="x")
        tk.Label(card1_header, text="启动浏览器", 
                font=("Microsoft YaHei UI", 11, "bold"), 
                fg="white", bg="#3b82f6", 
                padx=15, pady=10).pack(anchor="w")
        
        tk.Button(card1, text="🚀 启动 Chrome", 
                 command=self.launch_chrome,
                 font=("Microsoft YaHei UI", 11, "bold"),
                 bg="#3b82f6", fg="white",
                 activebackground="#2563eb", activeforeground="white",
                 relief=tk.FLAT,
                 padx=35, pady=14,
                 cursor="hand2").pack(pady=18)
        
        card2 = tk.Frame(parent, bg="#ffffff", relief=tk.FLAT, borderwidth=1)
        card2.pack(fill="both", expand=True, pady=8)
        
        card2_header = tk.Frame(card2, bg="#6366f1")
        card2_header.pack(fill="x")
        tk.Label(card2_header, text="店铺链接", 
                font=("Microsoft YaHei UI", 11, "bold"), 
                fg="white", bg="#6366f1", 
                padx=15, pady=10).pack(anchor="w")
        
        tk.Label(card2, text="每行填入一个店铺链接", 
                font=("Microsoft YaHei UI", 10), 
                fg="#6b7280", bg="#ffffff").pack(pady=(12, 8), anchor="w", padx=15)
        
        input_container = tk.Frame(card2, bg="#ffffff")
        input_container.pack(fill="both", expand=True, padx=15, pady=(0, 8))
        
        self.text_input = scrolledtext.ScrolledText(input_container, height=5, 
                                                     font=("Consolas", 10),
                                                     bg="#f9fafb", 
                                                     fg="#1f2937",
                                                     relief=tk.FLAT,
                                                     borderwidth=1,
                                                     padx=8, pady=8)
        self.text_input.pack(fill="both", expand=True)
        
        btn_frame2 = tk.Frame(card2, bg="#ffffff")
        btn_frame2.pack(fill="x", padx=15, pady=(0, 15))
        
        tk.Button(btn_frame2, text="填示例链接", 
                 command=self.fill_example,
                 font=("Microsoft YaHei UI", 10),
                 bg="#e0e7ff", fg="#4f46e5",
                 activebackground="#c7d2fe", activeforeground="#3730a3",
                 relief=tk.FLAT,
                 padx=18, pady=8,
                 cursor="hand2").pack(side="left", padx=4)
        
        tk.Button(btn_frame2, text="清空", 
                 command=self.clear_input,
                 font=("Microsoft YaHei UI", 10),
                 bg="#fee2e2", fg="#dc2626",
                 activebackground="#fecaca", activeforeground="#b91c1c",
                 relief=tk.FLAT,
                 padx=18, pady=8,
                 cursor="hand2").pack(side="left", padx=4)
        
        card3 = tk.Frame(parent, bg="#ffffff", relief=tk.FLAT, borderwidth=1)
        card3.pack(fill="x", pady=8)
        
        card3_header = tk.Frame(card3, bg="#10b981")
        card3_header.pack(fill="x")
        tk.Label(card3_header, text="开始下载", 
                font=("Microsoft YaHei UI", 11, "bold"), 
                fg="white", bg="#10b981", 
                padx=15, pady=10).pack(anchor="w")
        
        btn_container = tk.Frame(card3, bg="#ffffff")
        btn_container.pack(pady=18)
        
        self.start_btn = tk.Button(btn_container, text="开始下载", 
                                    command=self.start_download,
                                    font=("Microsoft YaHei UI", 13, "bold"),
                                    bg="#10b981", fg="white",
                                    activebackground="#059669", activeforeground="white",
                                    relief=tk.FLAT,
                                    padx=45, pady=14,
                                    cursor="hand2")
        self.start_btn.pack(side="left", padx=6)
        
        self.stop_btn = tk.Button(btn_container, text="停止", 
                                  command=self.stop_download,
                                  font=("Microsoft YaHei UI", 12, "bold"),
                                  bg="#ef4444", fg="white",
                                  activebackground="#dc2626", activeforeground="white",
                                  relief=tk.FLAT,
                                  padx=30, pady=12,
                                  state="disabled",
                                  cursor="hand2")
        self.stop_btn.pack(side="left", padx=6)
        
        self.status_label = tk.Label(parent, text="就绪", 
                                    font=("Microsoft YaHei UI", 12, "bold"), 
                                    fg="#10b981", bg="#f0f2f5")
        self.status_label.pack(pady=15)
    
    def setup_right_panel(self, parent):
        self.log_text = scrolledtext.ScrolledText(parent, font=("Consolas", 10),
                                                   bg="#f9fafb",
                                                   fg="#1f2937",
                                                   relief=tk.FLAT,
                                                   borderwidth=0,
                                                   padx=10, pady=10)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)
    
    def setup_logger(self):
        self.logger = setup_logger(DOWNLOAD_DIR)
        self.downloader.set_logger(self.logger)
        
        for handler in self.logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                self.logger.removeHandler(handler)
        
        tk_handler = TkinterLogHandler(self.log_text)
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
        tk_handler.setFormatter(formatter)
        self.logger.addHandler(tk_handler)
    
    def fill_example(self):
        self.log("正在填入示例链接...")
        example = "https://cs.wsy.com/1109067\nhttps://cs.wsy.com/1108199"
        self.text_input.delete(1.0, tk.END)
        self.text_input.insert(tk.END, example)
        self.log("✓ 示例链接已填入！")
    
    def clear_input(self):
        self.log("正在清空...")
        self.text_input.delete(1.0, tk.END)
        self.log("✓ 已清空！")
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def update_status(self, text):
        self.status_label.config(text=text)
        self.root.update()
    
    def launch_chrome(self):
        self.log("正在启动 Chrome...")
        
        if not os.path.exists(CHROME_PATH):
            self.log("✗ 找不到 Chrome！")
            messagebox.showerror("错误", f"找不到 Chrome：\n{CHROME_PATH}")
            return
        
        if not os.path.exists(CHROME_PROFILE_DIR):
            os.makedirs(CHROME_PROFILE_DIR)
        
        try:
            subprocess.Popen([
                CHROME_PATH,
                "--remote-debugging-port=9222",
                "--start-maximized",
                f"--user-data-dir={CHROME_PROFILE_DIR}",
                "https://www.wsy.com/new/goldStall"
            ])
            self.log("✓ Chrome 已启动！")
            self.log("请在 Chrome 中登录网商园")
            self.log("登录后点击「开始下载」")
            messagebox.showinfo("提示", "Chrome 已启动！\n\n请在 Chrome 中登录网商园\n登录后点击「开始下载」！")
        except Exception as e:
            self.log(f"✗ 启动失败: {e}")
            messagebox.showerror("错误", f"启动失败：\n{e}")
    
    def start_download(self):
        if self.is_running:
            self.log("✗ 程序正在运行！")
            return
        
        content = self.text_input.get(1.0, tk.END).strip()
        if not content:
            self.log("✗ 请输入店铺链接！")
            messagebox.showwarning("提示", "请输入店铺链接！")
            return
        
        shop_links = [line.strip().strip('`').strip() for line in content.split("\n") if line.strip()]
        if not shop_links:
            self.log("✗ 请输入有效的链接！")
            messagebox.showwarning("提示", "请输入有效的链接！")
            return
        
        self.log(f"\n共 {len(shop_links)} 个店铺链接")
        
        self.is_running = True
        self.should_stop = False
        self.start_btn.config(state="disabled", text="正在运行...")
        self.stop_btn.config(state="normal")
        self.update_status("正在连接...")
        self.log("\n开始运行...")
        
        thread = threading.Thread(target=self.run_download, args=(shop_links,))
        thread.daemon = True
        thread.start()
    
    def stop_download(self):
        self.log("\n正在停止...")
        self.should_stop = True
        self.stop_btn.config(state="disabled", text="正在停止...")
    
    def run_download(self, shop_links):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        try:
            sys.stdout = TextRedirector(self.log_text)
            sys.stderr = TextRedirector(self.log_text)
            
            self.update_status("开始下载...")
            
            for idx, shop_link in enumerate(shop_links, 1):
                if self.should_stop:
                    self.log("检测到停止，结束任务！")
                    break
                
                self.update_status(f"正在处理 {idx}/{len(shop_links)}")
                self.log(f"\n--- 正在处理第 {idx} 个店铺 ---")
                
                if not self.downloader.start_download(shop_link):
                    self.log(f"✗ 处理失败")
                
                time.sleep(2)
            
            self.log("\n✅ 全部完成！")
            self.update_status("完成！")
            
        except Exception as e:
            self.log(f"\n✗ 出错了: {e}")
            import traceback
            self.log(traceback.format_exc())
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self.is_running = False
            self.root.after(0, self.enable_button)
    
    def enable_button(self):
        self.start_btn.config(state="normal", text="开始下载")
        self.stop_btn.config(state="disabled", text="停止")
        self.update_status("就绪")

def main():
    root = tk.Tk()
    app = DownloadGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

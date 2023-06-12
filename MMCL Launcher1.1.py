import tkinter as tk
import subprocess
import requests
import os
import traceback
from tkinter import messagebox
from tkinter import filedialog

root = tk.Tk()
root.title("Minecraft启动器")

# 设置窗口大小和位置
window_width = 600
window_height = 400
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width - window_width) / 2)
y = int((screen_height - window_height) / 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# 设置背景颜色和字体
bg_color = "#f5f5f5"
font = ("微软雅黑", 12)

# 获取版本列表
def get_versions():
    try:
        response = requests.get("https://bmclapi2.bangbang93.com/mc/game/version_manifest.json")
        response.raise_for_status()
        versions_json = response.json()["versions"]
    except requests.exceptions.RequestException as e:
        traceback.print_exc()
        versions_json = []
    return versions_json

# 创建输入框和标签
path_label = tk.Label(root, text="Minecraft路径：", bg=bg_color, font=font)
path_label.place(x=50, y=50)
path_entry = tk.Entry(root, width=50, font=font)
path_entry.place(x=200, y=50)

args_label = tk.Label(root, text="启动参数：", bg=bg_color, font=font)
args_label.place(x=50, y=100)
args_entry = tk.Entry(root, width=50, font=font)
args_entry.place(x=200, y=100)

# 自动识别Minecraft路径
minecraft_path = os.getenv('APPDATA') + "\\.minecraft"
if os.path.exists(minecraft_path):
    path_entry.insert(0, minecraft_path)

# 自动识别Java参数
java_args = "-Xmx2G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC"
args_entry.insert(0, java_args)

versions_json = get_versions()
if versions_json:
    # 创建版本选择框和变量
    version_var = tk.StringVar()
    version_var.set(versions_json[0]["id"])
    versions_menu = tk.OptionMenu(root, version_var, *list(version["id"] for version in versions_json))
    versions_menu.config(bg=bg_color, font=font, width=10)
    versions_menu.place(x=50, y=150)

# 创建启动按钮
def start_minecraft():
    path = path_entry.get().strip()
    args = args_entry.get().strip()

    if not path:
        messagebox.showerror("错误", "Minecraft路径不能为空")
        return
    if not args:
        messagebox.showwarning("警告", "启动参数为空")

    selected_version = version_var.get()
    version_url = next(version["url"] for version in versions_json if version["id"] == selected_version)
    download_url = f"https://bmclapi2.bangbang93.com{version_url}"
    version_path = f"versions/{selected_version}/{selected_version}.jar"

    if not os.path.exists(version_path):
        download_window.deiconify()
        return

    # 启动Minecraft，显示等待动画
    wait_window = tk.Toplevel(root)
    wait_window.title("启动中")
    wait_window.geometry("200x100")
    wait_label = tk.Label(wait_window, text="正在启动，请稍候...", font=font)
    wait_label.pack(pady=20)
    wait_window.update()

    subprocess.Popen(["java", args, "-jar", version_path], cwd=path)

    wait_window.destroy()

start_button = tk.Button(root, text="启动", bg="#4CAF50", fg="white", font=font, command=start_minecraft)
start_button.place(x=50, y=200)

# 创建下载中心界面
download_window = tk.Toplevel(root)
download_window.title("下载中心")
download_window.geometry("400x300")

if versions_json:
    # 创建版本列表
    versions_listbox = tk.Listbox(download_window, width=40, font=font)
    for version in versions_json:
        versions_listbox.insert(tk.END, version["id"])
    versions_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

    # 创建下载按钮
    def download_version():
        selected_version = versions_listbox.get(tk.ACTIVE)
        version_url = next(version["url"] for version in versions_json if version["id"] == selected_version)
        download_url = f"https://bmclapi2.bangbang93.com{version_url}"
        download_path = f"versions/{selected_version}/{selected_version}.jar"

        if not os.path.exists(os.path.dirname(download_path)):
            os.makedirs(os.path.dirname(download_path))

        try:
            response = requests.get(download_url)
            response.raise_for_status()
            with open(download_path, "wb") as f:
                f.write(response.content)
            messagebox.showinfo("提示", "下载成功")
        except requests.exceptions.RequestException:
            messagebox.showerror("错误", "下载失败")

    download_button = tk.Button(download_window, text="下载", bg="#4CAF50", fg="white", font=font, command=download_version)
    download_button.pack(side=tk.RIGHT)
    download_button.config(state=tk.DISABLED)

    # 下载完成后启用下载按钮
    def enable_download_button(event):
        download_button.config(state=tk.NORMAL)

    download_window.bind("<Map>", enable_download_button)

# 创建启动器界面的下载中心按钮
if versions_json:
    download_button = tk.Button(root, text="下载中心", bg="#2196F3", fg="white", font=font, command=download_window.deiconify)
    download_button.place(x=150, y=200)

# 创建浏览按钮
def browse():
    path = filedialog.askdirectory()
    if path:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, path)

browse_button = tk.Button(root, text="浏览", bg="#2196F3", fg="white", font=font, command=browse)
browse_button.place(x=450, y=50)

# 创建清除缓存按钮
def clear_cache():
    for version in versions_json:
        version_path = f"versions/{version['id']}/{version['id']}.jar"
        if os.path.exists(version_path):
            os.remove(version_path)
    messagebox.showinfo("提示", "缓存已清除")

clear_button = tk.Button(root, text="清除缓存", bg="#FF5722", fg="white", font=font, command=clear_cache)
clear_button.place(x=450, y=100)

root.mainloop()

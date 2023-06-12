import tkinter as tk
import subprocess
import requests
import os

root = tk.Tk()
root.title("Minecraft启动器")

# 创建输入框和标签
path_label = tk.Label(root, text="Minecraft路径：")
path_label.grid(row=0, column=0)
path_entry = tk.Entry(root, width=50)
path_entry.grid(row=0, column=1)

args_label = tk.Label(root, text="启动参数：")
args_label.grid(row=1, column=0)
args_entry = tk.Entry(root, width=50)
args_entry.grid(row=1, column=1)

# 创建版本列表和变量
version_var = tk.StringVar()
version_var.set("1.16.5")
versions_url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
versions_json = requests.get(versions_url).json()
versions_menu = tk.OptionMenu(root, version_var, *list(version["id"] for version in versions_json["versions"]))
versions_menu.grid(row=2, column=1)

# 创建启动按钮
def start_minecraft():
    path = path_entry.get()
    args = args_entry.get()
    selected_version = version_var.get()
    version_path = f"versions/{selected_version}/{selected_version}.jar"
    if not os.path.exists(version_path):
        download_window.deiconify()
        return
    subprocess.Popen(["java", "-jar", version_path] + args.split())

start_button = tk.Button(root, text="启动", command=start_minecraft)
start_button.grid(row=2, column=0)

# 创建下载中心界面
download_window = tk.Toplevel(root)
download_window.title("下载中心")
download_window.geometry("400x300")

# 创建版本列表
versions_listbox = tk.Listbox(download_window, width=40)
for version in versions_json["versions"]:
    versions_listbox.insert(tk.END, version["id"])
versions_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

# 创建下载按钮
def download_version():
    selected_version = versions_listbox.get(tk.ACTIVE)
    version_url = next(version["url"] for version in versions_json["versions"] if version["id"] == selected_version)
    version_json = requests.get(version_url).json()
    download_url = next(asset["url"] for asset in version_json["assets"] if asset["name"] == version_json["downloads"]["client"]["sha1"] + ".jar")
    download_path = f"versions/{selected_version}/{selected_version}.jar"
    with open(download_path, "wb") as f:
        f.write(requests.get(download_url).content)

download_button = tk.Button(download_window, text="下载", command=download_version)
download_button.pack(side=tk.RIGHT)

# 创建启动器界面的下载中心按钮
download_button = tk.Button(root, text="下载中心", command=download_window.deiconify)
download_button.grid(row=2, column=2)

root.mainloop()

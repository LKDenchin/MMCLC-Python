import tkinter as tk
import subprocess
import requests
import os
import traceback
from tkinter import messagebox
from tkinter import filedialog
from tkinter import Toplevel
from tkinter import font
from tkinter import ttk




#下载模块链接

BMCLAPI = """http://launchermeta.mojang.com/mc/game/version_manifest.json -> https://bmclapi2.bangbang93.com/mc/game/version_manifest.json
http://launchermeta.mojang.com/mc/game/version_manifest_v2.json -> https://bmclapi2.bangbang93.com/mc/game/version_manifest_v2.json
https://launchermeta.mojang.com -> https://bmclapi2.bangbang93.com
https://launcher.mojang.com -> https://bmclapi2.bangbang93.com
http://resources.download.minecraft.net -> https://bmclapi2.bangbang93.com/assets
https://libraries.minecraft.net -> https://bmclapi2.bangbang93.com/maven
https://launchermeta.mojang.com/v1/products/java-runtime/2ec0cc96c44e5a76b9c8b7c39df7210883d12871/all.json -> https://bmclapi2.bangbang93.com/v1/products/java-runtime/2ec0cc96c44e5a76b9c8b7c39df7210883d12871/all.json
https://files.minecraftforge.net/maven -> https://bmclapi2.bangbang93.com/maven
http://dl.liteloader.com/versions/versions.json -> https://bmclapi.bangbang93.com/maven/com/mumfrey/liteloader/versions.json
https://authlib-injector.yushi.moe -> https://bmclapi2.bangbang93.com/mirrors/authlib-injector
https://meta.fabricmc.net -> https://bmclapi2.bangbang93.com/fabric-meta
https://meta.fabricmc.net -> https://bmclapi2.bangbang93.com/fabric-meta"""
MCBBS = BMCLAPI + "\nhttps://bmclapi2.bangbang93.com -> https://download.mcbbs.net"

#镜像源地址快速修改，用诸如"a -> b\n c -> d"的格式定义要替换的地址，然后用inject函数替换url，返回值为替换镜像源后的url

class MirrorInjector(object):
    def __init__(self, mirrorProperties):
        mirrorPropertiesObj = {}
        for i in str(mirrorProperties).replace(' ', '').split():
            j = i.split("->", 1)
            mirrorPropertiesObj[j[0]] = j[1]
        self.__mirrorPropertiesObj = mirrorPropertiesObj
        
    def inject(self, url):
        urlb = str(url)
        for key,value in self.__mirrorPropertiesObj.items():
            urlb = urlb.replace(key, value)
        return urlb

def get_versions():
    try:
        injector = MirrorInjector(BMCLAPI)
        response = requests.get(injector.inject("http://launchermeta.mojang.com/mc/game/version_manifest.json"))
        response.raise_for_status()
        versions_json = response.json()["versions"]
    except requests.exceptions.RequestException as e:
        traceback.print_exc()
        versions_json = []
    return versions_json


root = tk.Tk()
root.title("MMCL启动器")
root.geometry("600x400")
root.configure(bg="#212121")

# 创建标签样式
label_font = font.Font(family="微软雅黑", size=12, weight="bold")
entry_font = font.Font(family="微软雅黑", size=10)
button_font = font.Font(family="微软雅黑", size=12, weight="bold")

# 创建标题标签
title_label = tk.Label(root, text="MMCL启动器", fg="white", bg="#212121", font=font.Font(family="微软雅黑", size=18, weight="bold"))
title_label.place(x=250, y=20)

# 创建输入框和标签
path_label = tk.Label(root, text="Minecraft路径：", fg="white", bg="#212121", font=label_font)
path_label.place(x=50, y=100)
path_entry = tk.Entry(root, width=50, font=entry_font)
path_entry.place(x=200, y=100)

args_label = tk.Label(root, text="启动参数：", fg="white", bg="#212121", font=label_font)
args_label.place(x=50, y=150)
args_entry = tk.Entry(root, width=50, font=entry_font)
args_entry.place(x=200, y=150)

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
    versions_menu = ttk.Combobox(root, textvariable=version_var, values=list(version["id"] for version in versions_json), font=entry_font, state="readonly", width=10)
    versions_menu.place(x=50, y=200)

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
        # 如果版本没有下载，则弹出下载窗口并等待下载完成
        download_window = tk.Toplevel(root)
        download_window.title("下载中...")
        download_window.geometry("300x100")
        download_window.configure(bg="#212121")
        download_window.deiconify()

        download_thread = threading.Thread(target=download_version, args=(download_url, version_path, download_window))
        download_thread.start()

        return

    # 如果版本已经下载，则直接启动游戏
    wait_window = tk.Toplevel(root)
    wait_window.title("启动中")
    wait_window.geometry("200x100")
    wait_window.configure(bg="#212121")
    wait_label = tk.Label(wait_window, text="正在启动，请稍候...", fg="white", bg="#212121", font=label_font)
    wait_label.pack(pady=20)
    wait_window.update()

    subprocess.Popen(["java", args, "-jar", version_path], cwd=path)

    wait_window.destroy()

start_button = tk.Button(root, text="启动", bg="#4CAF50", fg="white", font=button_font, command=start_minecraft)
start_button.place(x=50, y=250)

# 创建下载中心界面
download_window = tk.Toplevel(root)
download_window.title("下载中心")
download_window.geometry("400x300")
download_window.configure(bg="#212121")

if versions_json:
    # 创建版本列表
    versions_listbox = tk.Listbox(download_window, width=40, font=entry_font)
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

    # 设置下载按钮为不可用状态
    download_button.config(state=tk.DISABLED)

    try:
        response = requests.get(download_url)
        response.raise_for_status()
        with open(download_path, "wb") as f:
            f.write(response.content)
        messagebox.showinfo("提示", "下载成功")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("错误", f"下载失败：{e}")

    # 重新启用下载按钮
    download_button.config(state=tk.NORMAL)

# 创建下载按钮
download_button = tk.Button(download_window, text="下载", bg="#4CAF50", fg="white", font=button_font, command=download_version)
download_button.pack(side=tk.RIGHT)
download_button.config(state=tk.DISABLED)

# 下载完成后启用下载按钮
def enable_download_button(event):
    download_button.config(state=tk.NORMAL)

download_window.bind("<Map>", enable_download_button)

# 创建启动器界面的下载中心按钮
if versions_json:
    download_button = tk.Button(root, text="下载中心", bg="#2196F3", fg="white", font=button_font, command=download_window.deiconify)
    download_button.place(x=150, y=250)

# 创建浏览按钮
def browse():
    path = filedialog.askdirectory()
    if path:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, path)

browse_button = tk.Button(root, text="浏览", bg="#2196F3", fg="white", font=button_font, command=browse)
browse_button.place(x=500, y=100)

# 创建清除缓存按钮
def clear_cache():
    for version in versions_json:
        version_path = f"versions/{version['id']}/{version['id']}.jar"
        if os.path.exists(version_path):
            os.remove(version_path)
    messagebox.showinfo("提示", "缓存已清除")

clear_button = tk.Button(root, text="清除缓存", bg="#FF5722", fg="white", font=button_font, command=clear_cache)
clear_button.place(x=500, y=150)

root.mainloop()
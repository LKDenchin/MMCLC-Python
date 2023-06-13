import requests

client_id = "967b69c8-6c47-4dc6-894c-6aef6a2ca010" # 请替换为自己的client_id
client_secret = "eeab3455-b6c9-403e-a987-afecc0af6aa1" # 请替换为自己的client_secret
xbox_api_key = "https://graph.microsoft.com/User.Read" # 请替换为自己的Xbox API Key

# 获取access_token
def get_access_token(code):
    response = requests.post("https://login.live.com/oauth20_token.srf", data={
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
        "scope": "XboxLive.signin XboxLive.offline_access"
    })

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None

# 获取用户的Xbox Live ID
def get_xbox_live_id(access_token):
    response = requests.post("https://user.auth.xboxlive.com/user/authenticate", headers={
        "Authorization": f"Bearer {access_token}"
    })

    if response.status_code == 200:
        return response.json()["DisplayClaims"]["xui"][0]["xid"]
    else:
        return None

# 判断用户是否拥有Minecraft正版游戏
def has_minecraft(access_token):
    xbox_live_id = get_xbox_live_id(access_token)

    if xbox_live_id:
        response = requests.get(f"https://xboxapi.com/v2/xuid/{xbox_live_id}/xboxonegames", headers={
            "X-Authorization": xbox_api_key
        })

        if response.status_code == 200:
            games = response.json()["titles"]
            for game in games:
                if game["name"] == "Minecraft":
                    return True

    return False

# 登录
def login():
    # 获取登录授权码
    response = requests.get("https://login.live.com/oauth20_authorize.srf", params={
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
        "scope": "XboxLive.signin"
    })

    if response.status_code == 200:
        # 打开浏览器让用户授权
        import webbrowser
        webbrowser.open(response.url)

        # 获取access_token
        code = input("请输入授权码：")
        access_token = get_access_token(code)

        if access_token:
            # 判断用户是否拥有Minecraft正版游戏
            if has_minecraft(access_token):
                # 获取用户名
                response = requests.get("https://apis.live.net/v5.0/me", headers={
                    "Authorization": f"Bearer {access_token}"
                })

                if response.status_code == 200:
                    username = response.json()["name"]
                    print("欢迎进入游戏，", username)
                else:
                    print("获取用户信息失败")
            else:
                print("您的账户没有Minecraft正版游戏")
        else:
            print("获取access_token失败")
    else:
        print("获取授权码失败")

login()

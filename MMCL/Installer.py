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

#Test method
#if __name__ == '__main__':
#    injector = MirrorInjector("a -> b\nc -> d")
#    print(injector.inject("apkpopkpkpkc"))
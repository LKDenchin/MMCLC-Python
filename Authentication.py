from abc import ABC, abstractmethod
import uuid
import json
import requests

class AuthError(Exception):
    def __init__(self, arg):
        self.args = arg

class Profile(object):
    def __init__(self, accessToken, UUID, username, userType):
        self.accessToken = accessToken
        self.UUID = UUID
        self.username = username
        self.userType = userType

class Account(ABC):
    def __init__(self, accessToken, profiles):
        self.accessToken = accessToken
        self.profiles = profiles

    @abstractmethod
    def getSelectedProfile(self) -> Profile:
        pass

class AccountFactory(ABC):
    @abstractmethod
    def fromStorage(self, minecraftDir) -> Account:
        pass
    @abstractmethod
    def create(self, arg1, arg2) -> Account:
        pass

class OfflineAccount(Account):
    def __init__(self, username, uuid = None):
        
        super().__init__(self, "0", [{'id': (uuid.UUID("OfflinePlayer:" + username) if uuid == None else uuid), 'name': username}])
    
    def getSelectedProfile(self) -> Profile:
        profile = self.profiles[0]
        return Profile(self.accessToken, profile['id'], profile['name'], "legacy")

class YggdrasilAccount(Account):
    def __init__(self, responseBody):
        super().__init__(self, responseBody['accessToken'], responseBody)

    def selectProfile(self, profileUUID):
        for p in self.profiles['availableProfiles']:
            if p['id'] == profileUUID:
                self.profiles['selectedProfile'] = p
        
    def refreshAccount(self):
        payload = dict(filter(lambda x: x[0] in ['clientToken', 'accessToken', 'selectedProfile'], self.profiles.items()))
        requestJson = json.dumps(payload)
        authserver = self.profiles['authserver'] + "/refresh"
        response = requests.post(authserver, json = requestJson, headers = {'Content-Type': 'application/json'})
        if response.status_code >= 300 or response.status_code < 200:
            raise AuthError(str(response.status_code) + response.text)
        responseJson = json.load(response.text)
        responseJson['authserver'] = authserver
        self.profiles = responseJson
        
    def validate(self) -> bool:
        payload = dict(filter(lambda x: x[0] in ['clientToken', 'accessToken'], self.profiles.items()))
        requestJson = json.dumps(payload)
        authserver = self.profiles['authserver'] + "/validate"
        response = requests.post(authserver, json = requestJson, headers = {'Content-Type': 'application/json'})
        return response.status_code == 204
        
        
    def getSelectedProfile(self) -> Profile:
        prof = self.profiles['selectedProfile']
        return Profile(self.profiles['accessToken'], prof['id'], prof['name'], "mojang")

class YggdrasilAccountFactory(AccountFactory):
    def __init__(self, authserver):
        self.authserver = authserver

    def fromStorage(self, minecraftDir) -> Account:
        pass

    def create(self, username, password) -> Account:
        clientToken = uuid.uuid4()
        request = {
            'agent': {                              
                'name': 'Minecraft',                
                'version': 1                        
            },
            'username': username,      
            'password': password,
            'clientToken': str(clientToken),     
            'requestUser': true                     
        }
        requestJson = json.dumps(request)
        response = requests.post(self.authserver + "/authenticate", json = requestJson, headers = {'Content-Type': 'application/json'})
        if response.status_code >= 300 or response.status_code < 200:
            raise AuthError(str(response.status_code) + response.text)
        responseJson = json.load(response.text)
        responseJson['authserver'] = self.authserver
        return YggdrasilAccount(responseJson)
        

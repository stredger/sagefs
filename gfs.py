
import swiftclient


class SwiftFS():

    def __init__(self, authurl, user, key):
        self.authurl = authurl
        self.user = user
        self.key = key
        self.localfiles = {}
        
    def get_storage_token(self):
        url, token = swiftclient.get_auth(self.authurl, self.user, self.key)
        self.storeurl = url
        self.storetoken = token


    def fopen(self, path):
        resp, f = swiftclient.get_object(self.storeurl, self.storetoken, self.user)
        print resp
        # download local file if it exists
        #   throw file not found if not
        #  
        # open it as a SwiftFile and return
        #   the object!



# file like as it is well... a file!
class SwiftFile(file):

    def __init__(self, swiftname, localname, fs):
        self.swiftname = swiftname
        self.localname = localname
        self.fs = fs

    def read():
        pass

    def write():
        pass
        

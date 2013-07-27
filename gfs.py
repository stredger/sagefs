
import swiftclient
import StringIO


class GFSFileNotFoundException(Exception):
    pass
    # def __init__(self, message):
    #     self.message = message
    # def __str__(self):
    #     return message


class SwiftFS():

    def __init__(self, authurl, group, user, key):
        self.authurl = authurl
        self.group = group
        self.user = user
        self.key = key
        self.container = user
        self.localfiles = {}
        self.get_storage_token()

    def get_account_str(self):
        return "%s:%s" % (self.group, self.user)
    
    def get_storage_token(self):
        account = self.get_account_str()
        url, token = swiftclient.get_auth(self.authurl, account, self.key)
        self.storeurl = url
        self.storetoken = token

    def download(self, path):
        return swiftclient.get_object(self.storeurl, self.storetoken, 
                                      self.container, path)

    def upload(self, path, data):
        return swiftclient.put_object(self.storeurl, self.storetoken, 
                                      self.container, path, data)

    def open(self, path, create=False):
        try:
            resp, data = self.download(path)
        except swiftclient.client.ClientException as e:
            print e.http_status
            # we should check what the ClientException actually means
            #  we can get more than a 404 here!!
            raise GFSFileNotFoundException('File Not Found: requested %s at %s' %
                                           (path, self.storeurl))
        sf = SwiftFile(data, path, self)
        self.localfiles[path] = sf
        return sf


# Eventaully have InMem and OnDisk filesystems!
# class SwiftInMemFS(SwiftFS):

#     def fopen(self, path, create=False):
#         data = SwiftFS.fopen(self, path, create)
#         sf = SwiftFile(data, path, self)
#         self.localfiles[path] = sf
#         return sf



class SwiftFile(StringIO.StringIO):

    def __init__(self, data, swiftname, fs):
        self.swiftname = swiftname
        self.fs = fs # this should have upload and download functions!
        StringIO.StringIO.__init__(self, data)

    def sync(self):
        fptr = self.tell()
        self.seek(0)
        self.fs.upload(self.swiftname, self)
        self.seek(fptr)


    def flush(self):
        self.sync()

    def write(self, arg, sync=True):
        StringIO.StringIO.write(self, arg)
        if sync: self.sync()

    def writelines(self, arg, sync=True):
        StringIO.StringIO.writelines(self, arg)
        if sync: self.sync()

    def close(self):
        self.sync()
        StringIO.StringIO.close(self)
        

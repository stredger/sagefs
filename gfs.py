
import swiftclient
import StringIO
import tempfile


class GFSException(Exception):
    pass

class GFSFileNotFoundException(GFSException):
    pass



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

    def delete(self, path):
        return swiftclient.delete_object(self.storeurl, self.storetoken,
                                         self.container, path)


    def open(self, path, create=False, inmem=True):
        try: resp, data = self.download(path)
        except swiftclient.client.ClientException as e:
            if e.http_status == 404: 
                if create: data = ''
                else: raise GFSFileNotFoundException('File %s/%s not found.' 
                                                     % (self.storeurl, path))
            else: raise GFSException('HTTP Error: %s - %s' 
                                     % (e.http_status, e.http_reason))
        if inmem: fd = SwiftMemFile(data, path, self)
        else: fd = SwiftDiskFile(data, path, self)
        self.localfiles[path] = fd
        return fd

    def remove(self, path):
        try: self.delete(path)
        except swiftclient.client.ClientException as e:
            if e.http_status == 404: pass # maybe throw an exception?
            else: raise GFSException('HTTP Error: %s - %s' 
                                     % (e.http_status, e.http_reason))

    def move(self, oldpath, newpath, overwrite=True):
        local = True
        if not overwrite:
            pass # stat new path to see if there is something there!

        # get the fd for the file like object to move
        if oldpath not in self.localfiles:
            local = False
            self.open(oldpath)
        fd = self.localfiles[oldpath]

        # upload under new name
        fd.swiftname = newpath
        fd.sync()
        self.localfiles[newpath] = fd

        # remove the old object
        self.remove(oldpath)
        self.localfiles.pop(oldpath)

        if not local: fd.close()
        
    def list():
        pass



class SwiftFile():
    
    def __init__(self, swiftname, fs, fileclass):
        self.swiftname = swiftname
        self.fs = fs
        self.fileclass = fileclass
        



class SwiftMemFile(StringIO.StringIO):

    def __init__(self, data, swiftname, fs):
        self.swiftname = swiftname
        self.fs = fs # this should have upload and download functions!
        #SwiftFile.__init__(self, swiftname, fs)
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
        self.fs.localfiles.pop(self.swiftname)
        

        
class SwiftDiskFile(tempfile._TemporaryFileWrapper):

    def __init__(self, data, swiftname, fs):
        self.swiftname = swiftname
        self.fs = fs
        fd = tempfile.NamedTemporaryFile()
        fd.write(data)
        return fd

    def sync(self):
        fptr = self.tell()
        self.seek(0)
        self.fs.upload(self.swiftname, self)
        self.seek(fptr)


    def flush(self):
        self.sync()

    def write(self, arg, sync=True):
        tempfile._TemporaryFileWrapper.write(self, arg)
        if sync: self.sync()

    def writelines(self, arg, sync=True):
        tempfile._TemporaryFileWrapper.writelines(self, arg)
        if sync: self.sync()

    def close(self):
        self.sync()
        tempfile._TemporaryFileWrapper.close(self)
        self.fs.localfiles.pop(self.swiftname)

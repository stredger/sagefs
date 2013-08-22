
import swiftclient
import StringIO
import tempfile
import os



#TODO's
# - support for different users per fs?
# - re authenticate if token craps out, what error do we get?
# - better exception handling stuff
# - docs
# - containers must exist before we upload it seems
# - make directories and such to fake fs structure

class GFSException(Exception): pass
class GFSInvalidPathException(GFSException): pass
class GFSInvalidFilesystemException(GFSException): pass
class GFSFileNotFoundException(GFSException): pass
class GFSFileExistsException(GFSException): pass
class GFSPermissionDenied(GFSException): pass



swiftrepos = {'uvic' : 'grack01.uvic.trans-cloud.net',
              #'local' : 'localhost',
              'savi' : '142.104.64.68',
              'gpo' : 'gc-1.stephen.ch-geni-net.instageni.gpolab.bbn.com',
              'kentucky' : 'gc-1.stephen.ch-geni-net.lan.sdn.uky.edu',
              'utah' : 'gc-1.stephen.ch-geni-net.utah.geniracks.net'}

def site_to_host(site):
    """ Find and return the hostname for the provided site.
        If no hostname matches a GFSException is raised """
    try: return swiftrepos[site]
    except KeyError:
        raise GFSException('No host matches site %s' % (site))

def get_authv1_url(host, port=8080):
    """ Given a host will generate the auth url required by swift """
    return 'http://%s:%s/auth/v1.0' % (host, port)

def swift_to_gfs_exception(e, **kwargs):
    # check if we are a swiftclient.client exception
    # then parse on http_status
    # raise the appropreate exception
    pass



class GFS():

    def __init__(self, group, user, key, sites=swiftrepos.keys()):
        self.filesystems = {}
        self.group = group
        self.user = user
        self.key = key
        for s in sites:
            authurl = get_authv1_url( site_to_host(s) )
            fs = SwiftFS(authurl, self.group, self.user, self.key)
            self.filesystems[s] = fs

    def split_location_from_path(self, path):
        """ A path looks like /location/path, split and return location, /path """
        if path[0] != '/': 
            raise GFSInvalidPathException('%s - must start with /' % (path))
        try: splitindex = path.index('/', 1)
        except ValueError: 
            raise GFSInvalidPathException('%s - must contain a valid '
                                          'swift repository name' % (path))
        location = path[1:splitindex]
        resource = path[splitindex+1:]
        return location, resource

    def get_filesystem(self, location):
        """ Find and return the hostname as a string for the provided location.
        If no hostname matches a GFSInvalidFilesystemException is raised """
        try: return self.filesystems[location]
        except KeyError:
            raise GFSInvalidFilesystemException('Filesystem - %s - was not found' 
                                                % (location))


    def open(self, path, *args, **kwargs):
        location, resource = self.split_location_from_path(path)
        fs = self.get_filesystem(location)
        return fs.open(resource, *args, **kwargs)

    def remove(self, path):
        location, resource = self.split_location_from_path(path)
        fs = self.get_filesystem(location)
        fs.remove(resource)

    def list(self, path=None):
        if not path: return ['/%s/' % (k) for k in self.filesystems.keys()]
        location, resource = self.split_location_from_path(path)
        fs = self.get_filesystem(location)
        return fs.list(resource)

    def stat(self, path=None):
        if not path:
            resp = {}
            for location in self.filesystems.keys():
                fs = self.get_filesystem(location)
                resp[location] = fs.stat()
            return resp
        location, resource = self.split_location_from_path(path)
        fs = self.get_filesystem(location)
        return fs.stat(resource)

    def copy(self, origpath, newpath, overwrite=False):
        if origpath == newpath: return
        origlocation, origresource = self.split_location_from_path(origpath)
        newlocation, newresource = self.split_location_from_path(newpath)
        origfs = self.get_filesystem(origlocation)
        if origlocation == newlocation:
            # if both resources use the same fs use the fs's copy
            origfs.copy(origresource, newresource)
            return
        newfs = self.get_filesystem(newlocation)
        # check to see if we are overwriting anything
        if not overwrite and newfs.file_exists(newresource):
            raise GFSFileExistsException('File %s already exists' % (newpath))
        local = True
        if origresource not in origfs.localfiles:
            # make sure the orig file is local to its fs
            local = False
            origfs.open(origresource)
        origfd = origfs.localfiles[origresource]
        # upload as a new resource
        try: newfs.upload(newresource, origfd)
        except swiftclient.client.ClientException as e:
            raise GFSException('HTTP Error: %s - %s' 
                               % (e.http_status, e.http_reason))
        if not local: origfd.close() 

    def move(self, origpath, newpath, overwrite=False):
        self.copy(origpath, newpath, overwrite)
        self.remove(origpath)

    def upload(self, localpath, swiftpath, overwrite=False):
        location, resource = self.split_location_from_path(swiftpath)
        if not resource: resource = localpath
        fs = self.get_filesystem(location)
        if not overwrite and fs.file_exists(swiftpath):
            raise GFSFileExistsException('File %s already exists' % (swiftpath))
        fptr = open(localpath)
        try: fs.upload(resource, fptr)
        except swiftclient.client.ClientException as e:
            raise GFSException('HTTP Error: %s - %s' 
                               % (e.http_status, e.http_reason))
        fptr.close()



class SwiftFS():

    def __init__(self, authurl, group, user, key):
        self.authurl = authurl
        self.group = group
        self.user = user
        self.key = key
        self.container = user
        self.localfiles = {}
        self.get_storage_token()
        self.init_container()

    def get_account_str(self):
        return "%s:%s" % (self.group, self.user)

    def get_storage_token(self):
        account = self.get_account_str()
        try:
            url, token = swiftclient.get_auth(self.authurl, account, self.key)
        except swiftclient.client.ClientException as e:
            raise GFSException('HTTP Error: %s - %s' 
                               % (e.http_status, e.http_reason))
        self.storeurl = url
        self.storetoken = token

    def init_container(self):
        if not self.container_exists(self.container):
            try: self.create_container(self.container)
            except swiftclient.client.ClientException as e:
                raise GFSException('HTTP Error: %s - %s' 
                                   % (e.http_status, e.http_reason))
                                   

    def download(self, path):
        return swiftclient.get_object(self.storeurl, self.storetoken, 
                                      self.container, path)

    def upload(self, path, data):
        return swiftclient.put_object(self.storeurl, self.storetoken, 
                                      self.container, path, data)

    def delete(self, path):
        return swiftclient.delete_object(self.storeurl, self.storetoken,
                                         self.container, path)

    def head(self, path=None):
        if not path: 
            return swiftclient.head_account(self.storeurl, self.storetoken)
        return swiftclient.head_object(self.storeurl, self.storetoken, 
                                       self.container, path)


    def head_container(self, container):
        return swiftclient.head_container(self.storeurl, self.storetoken,
                                          container)

    def list_container(self, path):
        # TODO: use paths so we can query like ls /path/
        return swiftclient.get_container(self.storeurl, self.storetoken, 
                                         self.container)

    def create_container(self, container):
        return swiftclient.put_container(self.storeurl, self.storetoken,
                                         container)

    def file_exists(self, path):
        """ Return True if a file exists at 'path', False otherwise """
        try: self.stat(path)     
        except GFSFileNotFoundException: return False
        return True

    def container_exists(self, container):
        """ Return True container exists, False otherwise """
        try: self.head_container(container)
        except swiftclient.client.ClientException as e:
            if e.http_status == 404: 
                return False
            else: raise GFSException('HTTP Error: %s - %s'
                                     % (e.http_status, e.http_reason))
        return True


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
        if create: fd.sync()
        return fd

    def remove(self, path):
        try: self.delete(path)
        except swiftclient.client.ClientException as e:
            if e.http_status == 404:                 
                raise GFSFileNotFoundException('Resource %s not found' 
                                               % (path))
            else: raise GFSException('HTTP Error: %s - %s' 
                                     % (e.http_status, e.http_reason))

    def list(self, path=None):
        try: resp, objects = self.list_container(path)
        except swiftclient.client.ClientException as e:
            raise GFSException('HTTP Error: %s - %s' 
                               % (e.http_status, e.http_reason))
        return objects

    def stat(self, path=None):
        try: resp = self.head(path)
        except swiftclient.client.ClientException as e:
            if e.http_status == 404: 
                raise GFSFileNotFoundException('Resource %s not found' 
                                               % (path))
            else: raise GFSException('HTTP Error: %s - %s'
                                     % (e.http_status, e.http_reason))
        return resp

    def copy(self, frompath, topath, overwrite=False):
        if frompath == topath: return
        local = True
        if not overwrite and self.file_exists(topath):
            raise GFSFileExistsException('File %s already exists' % (topath))
        # get the fd for the file like object to move
        if frompath not in self.localfiles:
            local = False
            self.open(frompath)
        fd = self.localfiles[frompath]
        if overwrite:
            # if we are overwriting and the file is local close it
            tofd = self.localfiles.get(frompath, None)
            if tofd: todf.close()
        # upload under new name
        fd.swiftname = topath
        fd.sync()
        fd.swiftname = frompath
        if not local: fd.close()

    def move(self, oldpath, newpath, overwrite=False):
        if oldpath == newpath: return
        self.copy(oldpath, newpath, overwrite)
        self.remove(oldpath)




class SwiftFile():
    
    def __init__(self, swiftname, fs, fileclass):
        self.swiftname = swiftname
        self.fs = fs
        self.fileclass = fileclass
        
    def sync(self):
        """ Calls the filesystems upload command to 
        write the files data to swift """
        fptr = self.fileclass.tell(self)
        self.fileclass.seek(self, 0)
        self.fs.upload(self.swiftname, self)
        self.fileclass.seek(self, fptr)


    def flush(self):
        """ Syncs the file to swift"""
        self.sync()

    def write(self, arg, sync=True):
        """ Calls the underlying write function for the file.
        Will sync with swift by default, will not if sync is False """
        self.fileclass.write(self, arg)
        if sync: self.sync()

    def writelines(self, arg, sync=True):
        """ Calls the underlying writelines function for the file.
        Will sync with swift by default, will not if sync is False """
        self.fileclass.writelines(self, arg)
        if sync: self.sync()

    def close(self):
        """ Close the file and sync it with swift """
        self.sync()
        self.fileclass.close(self)
        self.fs.localfiles.pop(self.swiftname)

    def todisk(self, path, overwrite=False):
        """ Writes the file to disk at path. If a file exists
        at path we will not overwrite unless specified """
        if not overwrite and os.path.exists(path):
            raise IOError('%s already exists' % (path))
        diskf = open(path, 'w+b')
        fptr = self.fileclass.tell(self)
        self.fileclass.seek(self, 0)
        data = self.read()
        diskf.write(data)
        diskf.close()
        self.fileclass.seek(self, fptr)        



class SwiftMemFile(SwiftFile, StringIO.StringIO):
    """ A string buffer that is used exactly like a regular file 
    but resides in memory """

    def __init__(self, data, swiftname, fs):
        SwiftFile.__init__(self, swiftname, fs, StringIO.StringIO)
        StringIO.StringIO.__init__(self, data)


     
class SwiftDiskFile(SwiftFile, file):
    """ A temp file that resides on disk """

    def __init__(self, data, swiftname, fs):
        fd, name = tempfile.mkstemp()
        # Close this fd as the file constructor makes
        #  a file like object we use instead
        os.close(fd)
        self.diskname = name
        SwiftFile.__init__(self, swiftname, fs, file)
        file.__init__(self, name, 'rw+b')
        file.write(self, data)
        file.seek(self, 0)


    def close(self):
        SwiftFile.close(self)
        os.unlink(self.diskname)

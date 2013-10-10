""" 
Author: Stephen Tredger, 2013

Copyright (c) 2013 University of Victoria

See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
for the full license
"""

"""
GFS implementation. The GFS is a distributed store with a filesystem like api.
The only object that needs to be instantiated is the GFS object. The filesystem
is interacted with through this object. (see README for info on users and accounts)
>>> fs = gfs.GFS(accountname, username, key)
>>> fs.move('/repo1/file', '/repo2/file')

Files are also opened throiugh a GFS object but can then be used like
regular python file objects. 
>>> f = fs.open('/repo/hi.txt')
>>> print f.read()
>>> f.write('appended!')
>>> f.close()
All files are opened in 'rw+b', and can only be opened once. If a file is opened
twice, the already opened file object is returned!
>>> f1 = fs.open('/repo/file')
>>> f2 = fs.open('/repo/file')
>>> f1 == f2
>>> True

There are two types of file objects gfs.open() can return, a purely in memory 
file (the default), or a tempfile on disk. Set the open arg 'inmem' to False for
a file on disk. The files behave the same way regardless of type.
"""


import swiftclient
import StringIO
import tempfile
import os
import hosts


#TODO's
# - better exception handling stuff
# - handle path querying in list command

class GFSException(Exception): pass
class GFSInvalidPathException(GFSException): pass
class GFSInvalidFilesystemException(GFSException): pass
class GFSFileNotFoundException(GFSException): pass
class GFSFileExistsException(GFSException): pass
class GFSPermissionDenied(GFSException): pass


# this is our super important dict of swiftrepos!
swiftrepos = hosts.proxies


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

def can_retry_error_status(status):
    """ Return True if the http status is something a retry may solve """
    if status == 503 or status == 401: 
        return True
    return False



class GFS():
    """ The main geni filesystem object. Takes a user group and key, and 
    establishes connections to Swift repos. Connections are only established
    when they are used the first time. The GFS object is designed to be the
    only object that must be explicitly created to use the GFS. """

    def __init__(self, group, user, key, sites=swiftrepos.keys()):
        self.filesystems = {}
        self.group = group
        self.user = user
        self.key = key

    def connect_to_filesystem(self, site):
        """ Creates a SwiftFS object, if we correctly connected 
        and aquired an auth token """
        authurl = get_authv1_url( site_to_host(site) )
        fs = SwiftFS(authurl, self.group, self.user, self.key)
        self.filesystems[site] = fs

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
            if location not in swiftrepos.keys():
                raise GFSInvalidFilesystemException('Filesystem - %s - was not found' 
                                                    % (location))
            

    def open(self, path, *args, **kwargs):
        """ Opens a file at path, calls the underlying SwiftFS's open.
        The desired SwiftFS, must be the root of the path """
        location, resource = self.split_location_from_path(path)
        fs = self.get_filesystem(location)
        return fs.open(resource, *args, **kwargs)

    def remove(self, path):
        """ Removes a resourse by calling the holding SwiftFS's remove.
        The SwiftFS must be the root of the path. """
        location, resource = self.split_location_from_path(path)
        fs = self.get_filesystem(location)
        fs.remove(resource)

    def list(self, path=None):
        """ Lists all Files in the filesystem specified at 'path'. If 'path' 
        is none, returns all the filesystem names in the GFS """
        if not path: return ['/%s/' % (k) for k in self.filesystems.keys()]
        location, resource = self.split_location_from_path(path)
        fs = self.get_filesystem(location)
        return fs.list(resource)

    def stat(self, path=None):
        """ Gets stats for a file if 'path' is not None,
        else gets stats for all filesystems """
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
        """ Copy a file from 'origpath' to 'newpath'.
        Will not overwrite unless specified """
        if origpath == newpath: return
        origlocation, origresource = self.split_location_from_path(origpath)
        newlocation, newresource = self.split_location_from_path(newpath)
        origfs = self.get_filesystem(origlocation)
        if origlocation == newlocation:
            # if both resources use the same fs use the fs's copy
            origfs.copy(origresource, newresource, overwrite)
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
        """ Move a file from origpath to newpath, will not
        overwrite unless specified """
        self.copy(origpath, newpath, overwrite)
        self.remove(origpath)

    def upload(self, localpath, swiftpath, overwrite=False):
        """ Upload a file into Swift from the local machine at 'localpath' 
        to 'swiftpath'. Will not overwrite unless specified """
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
    """ Interface between file objects and the actual Swift repository.
    'authurl' should be the url to authenticate with the desired swift cluster
    while the other parameters should be user specific authentication params.
    The user must already exist as a user in the Swift repo. """

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
        """ Generate account string required for swift authentication """
        return "%s:%s" % (self.group, self.user)

    def get_storage_token(self):
        """ Get a storage token for the swift cluster """
        account = self.get_account_str()
        try:
            url, token = swiftclient.get_auth(self.authurl, account, self.key)
        except swiftclient.client.ClientException as e:
            raise GFSException('HTTP Error: %s - %s' 
                               % (e.http_status, e.http_reason))
        self.storeurl = url
        self.storetoken = token

    def init_container(self):
        """ Make sure we have an account container """
        if not self.container_exists(self.container):
            try: self.create_container(self.container)
            except swiftclient.client.ClientException as e:
                raise GFSException('HTTP Error: %s - %s' 
                                   % (e.http_status, e.http_reason))
                                   
    def swift_command(self, cmd, args, retry):
        """ Do a swift command from the swiftclient module.
        If retry is True then retry the command once on error """
        try: return cmd(*args)
        except swiftclient.client.ClientException as e:
            if retry and can_retry_error_status(e.http_status):
                if e.http_status == 401: 
                    # error 401 may mean our storage token has expired
                    self.get_storage_token()
                    # reset the storage token already in args
                    args[1] = self.storetoken
                # retry the command but dont catch any exceptions
                return cmd(*args) 
            else: raise e

    def download(self, path, retry=True):
        """ Download an object at 'path' from Swift """
        cmd = swiftclient.get_object
        args = [self.storeurl, self.storetoken, self.container, path]
        return self.swift_command(cmd, args, retry)

    def upload(self, path, data, retry=True):
        """ Upload an object to 'path' in Swift """
        cmd = swiftclient.put_object
        args = [self.storeurl, self.storetoken, self.container, path, data]
        return self.swift_command(cmd, args, retry)

    def delete(self, path, retry=True):
        """ Remove an object at 'path' from Swift """
        cmd = swiftclient.delete_object
        args = [self.storeurl, self.storetoken, self.container, path]
        return self.swift_command(cmd, args, retry)

    def head(self, path=None, retry=True):
        """ Get stats (size, date, etc) from Swift for an object if 'path'
        is specified, or for the entire account if path is None """
        if path:
            cmd = swiftclient.head_object
            args = [self.storeurl, self.storetoken, self.container, path]
        else:
            cmd = swiftclient.head_account
            args = [self.storeurl, self.storetoken]
        return self.swift_command(cmd, args, retry)

    def head_container(self, container, retry=True):
        """ Get stats for a container from Swift """
        cmd = swiftclient.head_container
        args = [self.storeurl, self.storetoken, container]
        return self.swift_command(cmd, args, retry)
    
    def list_container(self, path, retry=True):
        """ List all files contained within the users container """
        # TODO: use paths so we can query like ls /path/
        cmd = swiftclient.get_container
        args = [self.storeurl, self.storetoken, self.container] #path
        return self.swift_command(cmd, args, retry)
    
    def create_container(self, container, retry=True):
        """ Creates a swift container """
        cmd = swiftclient.put_container
        args = [self.storeurl, self.storetoken, container]
        return self.swift_command(cmd, args, retry)

    def file_exists(self, path):
        """ Return True if a file exists at 'path', False otherwise """
        try: self.stat(path)     
        except GFSFileNotFoundException: return False
        return True

    def container_exists(self, container):
        """ Return True container exists, False otherwise. Throws a 
        GFSException if an HTTP error is encoutered """
        try: self.head_container(container)
        except swiftclient.client.ClientException as e:
            if e.http_status == 404: 
                return False
            else: raise GFSException('HTTP Error: %s - %s'
                                     % (e.http_status, e.http_reason))
        return True


    def open(self, path, create=False, inmem=True):
        """ Opens a file from SwiftFS. For consistency issues, a file may only
        be opened once. If a file is opened twice the opened fd gets returned.
        If the 'create' flag is True then the file will be created in the SwiftFS
        if not present already. Two file like objects can be returned, one that
        exists purely in memory, 'inmem'=True, and one that exists as a temp file
        'inmem'=False. Throws a GFSFileNotFoundException if the file doesn't
        exists and we are not creating one, and GFSException for HTTP errors """
        fd = self.localfiles.get(path, None)
        # if the file is already open, just return the fd.
        #  We could raise an exception, should not try to open a file twice
        if fd: return fd
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
        """ Removes a respourse at 'path' in the SwiftFS. Throws GFSException
        if an HTTP error occurs and GFSFileNotFoundException if the resource
        doesn't exist """
        try: self.delete(path)
        except swiftclient.client.ClientException as e:
            if e.http_status == 404:                 
                raise GFSFileNotFoundException('Resource %s not found' 
                                               % (path))
            else: raise GFSException('HTTP Error: %s - %s' 
                                     % (e.http_status, e.http_reason))

    def list(self, path=None):
        """ Lists all files present in the SwiftFS. Throws a
        GFSException if an HTTP error occurs. """
        try: resp, objects = self.list_container(path)
        except swiftclient.client.ClientException as e:
            raise GFSException('HTTP Error: %s - %s' 
                               % (e.http_status, e.http_reason))
        return objects

    def stat(self, path=None):
        """ Gets the stats of a file by heading it in Swift. Throws
        a GFSException if an HTTP error is encoutered, and a 
        GFSFileNotFoundException if the file doesn't exists """
        try: resp = self.head(path)
        except swiftclient.client.ClientException as e:
            if e.http_status == 404: 
                raise GFSFileNotFoundException('Resource %s not found' 
                                               % (path))
            else: raise GFSException('HTTP Error: %s - %s'
                                     % (e.http_status, e.http_reason))
        return resp

    def copy(self, frompath, topath, overwrite=False):
        """ Copies a file at frompath to topath within the SwiftFS.
        Will not overwrite a file at topath unless 'overwrite'=True """
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
            tofd = self.localfiles.get(topath, None)
            if tofd: tofd.close()
        # upload under new name
        fd.swiftname = topath
        fd.sync()
        fd.swiftname = frompath
        if not local: fd.close()

    def move(self, oldpath, newpath, overwrite=False):
        """ Moves a file within the SwiftFS from oldpath to newpath.
        Will not overwrite a file at newpath unless 'overwrite'=True """
        if oldpath == newpath: return
        self.copy(oldpath, newpath, overwrite)
        self.remove(oldpath)



class SwiftFile():
    """ A file like class, to be used as more of an abstract class.
    'fileclass' should be a file like class as well """
    
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
    """ A string buffer that is used exactly like a regular file, 
    but resides in memory """

    def __init__(self, data, swiftname, fs):
        SwiftFile.__init__(self, swiftname, fs, StringIO.StringIO)
        StringIO.StringIO.__init__(self, data)


     
class SwiftDiskFile(SwiftFile, file):
    """ A temp file like object that resides on disk """

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

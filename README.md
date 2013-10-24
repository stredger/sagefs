
sagefs.py, python module for interaction with the SageFS, a distributed filesystem.


1. Configuration

  a. Swift Repositories
  	The SageFS uses Swift repositories which should be set up accordingly.
  	(See swift-setup for more details, https://github.com/stredger/swift-setup)
  	We assume that all repos use swauth for authentication, tempauth has not been tested.
  	The repositories should be listed in hosts.py in a dict called 'proxies'.
  	The dict should contain 'name':'hostname' entries, where the name is how the SageFS
  	will address the specific swift repository.

  b. Users
  	Users of the SageFS must be set up in each Swift repo with the same account, username,
  	and key. (swift-setup has functions to do this)


2. Usage

	The sagefs is a python module imported to access a distributed persistent store.
	Files are mapped to locations based on their supplied path. To access a file
	stored at repo, myrepo, the path must have the root /myrepo/. ie. /myrepo/hello.txt.
	Each user gets their own space so files will not conflict with eachother, and each
	repo has its own space as well. ie. /repo1/hello.txt /repo2/hello.txt are separate.

	The SageFS object is created with an account name, username, and key.
	>>> fs = sagefs.SageFS(accountname, username, key)
	Filesystem operations are performed with the sagefs object like:
	>>> fs.copy('/repo1/file', '/repo2/file')
	Files are opened through the sagefs, but are then used exactly like normal
	python files.
	>>> f = fs.open('/repo/hello.txt')
	>>> f.write('hello!')
	>>> f.close()
	Files are automatically synced with Swift. Read the SwiftFS open() function
	in sagefs.py for more information on files, and each function in sagefs.py for more
	information on how it!

	For more in depth examples see sagefstest.py in the test directory!
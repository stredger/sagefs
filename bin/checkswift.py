
import subprocess
import sys
import os

def checkswift(host='localhost', user='admin', group='system', key='sagefs'):
  print '------ checkswift ------'
  command = 'swift -A http://%s:8080/auth/v1.0 -U %s:%s -K %s stat' % (host, group, user, key)
  print command
  p = subprocess.Popen(command.split())
  p.communicate()
  print ''


def checkupload(host='localhost', user='admin', group='system', key='sagefs'):
  print '------ checkupload ------'
  fname = os.path.join(os.getcwd(), 'checkswift.py')
  command = 'swift -A http://%s:8080/auth/v1.0 -U %s:%s -K %s upload __checktest__ %s' % (host, group, user, key, fname)
  print command
  p = subprocess.Popen(command.split())
  p.communicate()
  print ''


def checkdelete(host='localhost', user='admin', group='system', key='sagefs'):
  print '------ checkdelete ------'
  command = 'swift -A http://%s:8080/auth/v1.0 -U %s:%s -K %s delete __checktest__' % (host, group, user, key)
  print command
  p = subprocess.Popen(command.split())
  p.communicate()
  print ''


if __name__ == '__main__':

  checkall = False
  if len(sys.argv) > 1 and sys.argv[1] == 'all':
    checkall = True
    sys.argv = [''] + sys.argv[2:]
  checkswift(*sys.argv[1:])
  if checkall:
    checkupload(*sys.argv[1:])
    checkdelete(*sys.argv[1:])
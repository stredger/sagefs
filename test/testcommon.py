
class termcolours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def testpassed(testname):
  print ''.join([termcolours.OKGREEN, 'PASSED',  termcolours.ENDC, ' - %s: ' % testname]),

def testfailed(testname):
  print ''.join([termcolours.FAIL, 'FAILED',  termcolours.ENDC, '- %s: ' % testname]),
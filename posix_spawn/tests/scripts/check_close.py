import os
import sys
import errno

try:
    os.fstat(0)
except OSError as e:
    if e.errno == errno.EBADF:
        open(sys.argv[1], 'w').write('is closed')

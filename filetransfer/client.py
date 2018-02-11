#!/usr/bin/env python

import socket                   # Import socket module
import re
import os
import sys
import hashlib

def md5sum(fname):
    '''
    Calculate the file(fname)'s md5 value
    '''

    def read_chunks(fh):
        fh.seek(0)
        chunk = fh.read(8096)
        while chunk:
            yield chunk
            chunk = fh.read(8096)
        else:
            fh.seek(0)

    m = hashlib.md5()
    if isinstance(fname, basestring) and os.path.exists(fname):
        with open(fname, 'rb') as fh:
            for chunk in read_chunks(fh):
                m.update(chunk)
    elif fname.__class__.__name__ in ['StringIO', 'StringO'] \
            or isinstance(fname, file):
        for chunk in read_chunks(fname):
            m.update(chunk)
    else:
        return ''

    return m.hexdigest()

def progress_bar(num, total):
    rate_num = int(num * 100 / total)
    r = '\r[%s%s]%d%%'%('='*rate_num, ' '*(100-rate_num), rate_num)
    sys.stdout.write(r)
    if not rate_num == 100:
        sys.stdout.flush()
    else:
        sys.stdout.write('\n')

if __name__  == '__main__':
    port = 60001                    # Reserve a port for your service.
    host = socket.gethostname()     # Get local machine name
    print host

    s = socket.socket()
    s.connect((host, port))

    data = s.recv(1024)
    split_data = re.split(':', data)
    print split_data
    rev_fname = '_' + split_data[0]
    filesize = int(split_data[1])
    right_md5 = split_data[2]


    #sys.exit()
    count = 0
    with open(rev_fname, 'wb') as f:
        while True:
            try:
                data = s.recv(1024)
                count += len(data)
                #print 'data:' + repr(data)
                if not data:
                    break
                f.write(data)         # write data to a file
                progress_bar(count, filesize)
            except KeyboardInterrupt:
                print 'canceled by keyboard'
                break
        f.close()


    print 'Successfully get the file'
    print 'md5sum:' + md5sum(rev_fname)
    s.close()
    print 'connection closed'

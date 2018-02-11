#!/usr/bin/env python

import socket                   # Import socket module
import os
import sys
from time import sleep, time, ctime
import hashlib
import getopt


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


def send_prepare(fname):
    file_md5 = md5sum(fname)
    print 'file_md5: ' + file_md5
    conn.send(os.path.basename(fname) + ':' + repr(filesize) + ':' + file_md5)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'please choose a file to send'
        sys.exit()

    if sys.argv[1]:
        if not os.path.exists(sys.argv[1]):
            print 'file:' + sys.argv[1] + ' not exist'
            sys.exit()

    port = 60001                    # Reserve a port for your service.
    host = socket.gethostname()     # Get local machine name
    print host

    s = socket.socket()             # Create a socket object
    s.bind((host, port))            # Bind to the port
    s.listen(5)                     # Now wait for client connection.

    conn, addr = s.accept()         # Establish connection with client.
    print 'Got connection from' + repr(addr)

    filename = sys.argv[1]

    #sys.exit()

    filesize = os.path.getsize(filename)
    send_prepare(filename)
    sleep(1)

    start_time = time()
    count = 0
    with open(filename, 'rb') as f:
        chunk = f.read(1024)
        while chunk:
            try:
                conn.send(chunk)
                count += len(chunk)
                progress_bar(count, filesize)
                #print 'Sent: ' + repr(chunk)
                chunk = f.read(1024)
            except KeyboardInterrupt, errno:
                print 'transfer canceled by keyboard'
                print errno
                break
        f.close()

    end_time = time()
    elapse_time = end_time - start_time
    print 'average rate: %db/s'%(int(filesize/elapse_time))
    print 'end_time = %f'%end_time
    print 'start_time = %f'%start_time
    print 'send file over, used time: %fs'%elapse_time
    print 'now time:' + ctime()

    #conn.send('Thank you for connecting')
    conn.close()
    s.close()

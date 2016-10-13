__author__ = 'su530201'
import zlib
import gzip

# http://stackoverflow.com/questions/2423866/python-decompressing-gzip-chunk-by-chunk
# http://stackoverflow.com/questions/3122145/zlib-error-error-3-while-decompressing-incorrect-header-check/22310760


def read_corrupted_file(filename, CHUNKSIZE=1024, START=0, N=-1):
    i = N
    offset = START
    status = True
    d = zlib.decompressobj(zlib.MAX_WBITS | 32)
    with open(filename, 'rb') as f:
        result_str = b''
        f.seek(START)
        buffer = f.read(CHUNKSIZE)
        try:
            while buffer and i != 0:
                result_str += d.decompress(buffer)
                offset += CHUNKSIZE
                buffer = f.read(CHUNKSIZE)
                i -= 1
        except Exception as e:
            print('Error: %s : %d - %d -> %s' % (filename, offset, CHUNKSIZE, e))
            status = False
        return result_str, status, offset

if __name__=='__main__':
    in_file = '/home/su530201/PycharmProjects/bdas_project/raw_20160427_112704.dat.gz'
    out_file = '/home/su530201/PycharmProjects/bdas_project/raw_20160427_112704_recovered.dat.gz'
    of = gzip.open(out_file, "ab+")
    default_chunck = 2
    chunck_size = default_chunck
    the_offset = 0
    the_status = False
    while not the_status:
        the_s, the_status, the_new_offset = read_corrupted_file(in_file, chunck_size, the_offset, 32)
        if the_offset == the_new_offset:
            # bad block
            chunck_size = max(1, chunck_size // 2)
            print('bad block : %s', the_offset)
        else:
            chunck_size = default_chunck
            print('offset : %d - new offset : %d' %(the_offset, the_new_offset))
            the_offset = the_new_offset
            of.write(the_s)
    of.close()
    print('Done.')
#!/usr/bin/env python
#encoding:utf-8
import sys, os

import shutil
from Crypto.Cipher import AES

def parse_m3u8_file(m3u8_file):
    with open(m3u8_file, 'rb') as fp:
        current_line = fp.readline().rstrip('\n')
        while (current_line):
            if current_line.startswith('#EXT-X-KEY'):
                comps = current_line.split(',')
                URI = comps[1][5:-1]
                IV = comps[2][5:].rstrip('\n')
                with open(URI, 'rb') as urifp:
                    KEY = urifp.readline().rstrip('\n')
                fp.readline()
                ts_file = fp.readline().rstrip('\n')
                yield (IV, KEY, ts_file)
            current_line = fp.readline()

def decrypt(ciphertext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    return plaintext.rstrip(b"\0")

def decrypt_aes_128_ts_file(iv, key, ts_file):
    print(iv, key, ts_file)
    out = ts_file[:-2]+'.tsd'
    if os.path.exists(out):
        return out
    with open(ts_file, 'rb') as fo:
        ciphertext = fo.read()
    dec = decrypt(ciphertext, key, iv.decode('hex'))
    with open(out, 'wb') as fo:
        fo.write(dec)
    return out

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python %s m3u8_file' % sys.argv[0])
        sys.exit(1)

    m3u8 = sys.argv[1]
    if not os.path.exists(m3u8) or not m3u8.endswith('.m3u8'):
        print('Input file should be a m3u8 file.')
        sys.exit(1)
    os.system('sed -i "s/file:\/\/\/storage\/emulated\/0\/QQBrowser\/视频\///g" %s' % m3u8)

    tsd_files = []
    for (iv, key, ts_file) in parse_m3u8_file(m3u8):
        tsd_files.append(decrypt_aes_128_ts_file(iv, key, ts_file))

    with open(m3u8[:-4]+'ts', 'wb') as merged:
        for ts_file in tsd_files:
            with open(ts_file, 'rb') as mergefile:
                shutil.copyfileobj(mergefile, merged)

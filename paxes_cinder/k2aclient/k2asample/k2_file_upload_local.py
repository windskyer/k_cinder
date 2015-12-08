#
#
# =================================================================
# =================================================================

from __future__ import print_function
import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient import client
import logging

from tempfile import NamedTemporaryFile

from paxes_cinder.k2aclient.v1.k2web import File

import os
import hashlib


def _sha256sum(filename):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * sha256.block_size), b''):
            sha256.update(chunk)
        return sha256.hexdigest()


def sample_upload(cs, fspec):

    (k2fspec, _) = os.path.splitext(os.path.split(fspec)[1])
    k2fspec = k2fspec.replace("-", "_")

    # create the k2 web file
    webfile = File()
    webfile.filename = k2fspec
    webfile.internet_media_type = 'application/octet-stream'
    webfile.sha256 = _sha256sum(fspec)
    webfile.expected_file_size_in_bytes = os.path.getsize(fspec)
    print (webfile.expected_file_size_in_bytes)
    webfile.file_enum_type = 'LOCAL_FILE'

    webfile = cs.web_file.create(webfile)

    # Upload file
    with open(fspec, 'rb') as f:
        webfile.upload(f)

    return webfile

if __name__ == '__main__':

    k2acfg = k2asample.getk2acfg()
    k2asample.configure_logging(logging.getLevelName(k2acfg['loglevel']))
    cs = client.Client(k2acfg['api_version'],
                       k2acfg['k2_url'],
                       k2acfg['k2_username'],
                       k2acfg['k2_password'],
                       k2_auditmemento=k2acfg['k2_auditmemento'],
                       k2_certpath=k2acfg['k2_certpath'],
                       retries=k2acfg['retries'],
                       timeout=k2acfg['timeout'],
                       excdir=k2acfg['excdir'])

    try:
        f = NamedTemporaryFile(dir="/tmp", delete=False)
        f.write("Hello World!\n")
        f.close()

        # upload
        webfile = sample_upload(cs, f.name)
        print ("uploaded")

        # delete
        cs.web_file.delete(webfile)
        print ("deleted")

        os.unlink(f.name)

#         dfname = f.name + ".compare"
#         sample_download(cs, f.name, dfname)
#         k2resp = oper.read('File/contents', fileid, service='web')
#         with open(filename + '.compare', 'wb') as f2:
#             f2.write(k2resp.body)

    except Exception as e:
        logging.exception(e)

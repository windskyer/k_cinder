# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# =================================================================
# =================================================================

import httplib
import json
import logging
import sys
import requests
import os
import hashlib
import urlparse


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

XFER_TYPE = enum('URL', 'FILE')


def _extract_catalog(data, ip):
    """
    Create the service catalog based on the given response object from
    the authentication request.
    :param data: The response from the authentication request
    :return dict: A dict of services and their respective URLs
    """
    interface = 'public'
    catalog = data['token']['catalog']
    service_map = {}
    for service in catalog:
        service_endpoint = None
        for endpoint in service['endpoints']:
            if endpoint['interface'] == interface:
                service_endpoint = endpoint['url']
                break
        if service_endpoint:
            x = list(urlparse.urlsplit(service_endpoint))
            x[1] = ip
            service_endpoint = urlparse.urlunsplit(tuple(x))
            service_map[service['type']] = service_endpoint
#     LOG.debug('Service catalog: %s' % service_map)
    return service_map


def runtest():
    """
    Test file upload
    """

    # setup logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    debug_stream = logging.StreamHandler()
    logger.addHandler(debug_stream)

    ##############################################################
    # INPUT

    #####
    # PowerVC IP
    paxes_ip = "9.5.126.255"  # Sadek
#     paxes_ip = "9.114.251.9"  # Harish
#     paxes_ip = "9.5.127.146"  # Harish Old

    #####
    # PowerVC hmc_id
#     hmc_id = '2fa9da84-12d1-3256-af87-1b1b1c0134a8'  # Sadek hmc3
    hmc_id = 'c01d3d17-d951-336c-8233-a50de0ee031c'  # Sadek hmc5
#     hmc_id = "07247992-444c-3e08-9820-3b5c426174ca"  # Harish

    ####
    # Cinder volume

    # to create a volume:
    #     paxes-devcli cinder volume-create json billsco001 42
    #     use "id", eg  "id": "b769d931-0346-4265-a7a4-5bfe9ae22e4f",

    x_imgupload_cinder_volume_id = \
        "78ec5b63-893a-4274-ac33-6ef3257bc9d2"  # billsco001 on Sadek
#     x_imgupload_cinder_volume_id = \
#         "ce65ed8d-0486-4376-a748-4df2763a001e"  # billsco001 on Harish

#         "83a167d6-3d9e-4f14-bdcc-5f87e2361cee"  # Bill 1
#     x_imgupload_cinder_volume_id = \
#         "5b4d33c0-b2fb-414c-bfbf-5023add3ad99"  # Sadek 2
#     x_imgupload_cinder_volume_id = \
#       "81107edc-06c9-4c8b-9706-214809ea97d7"  # Harish

    vios = "2B74BDF1-7CC8-439E-A7D7-15C2B5864DA8"  # Sadek  # N23
#     vios = "1BC0CB5E-15BF-492A-8D06-25B69833B54E"  # Sadek  # N24
#     vios = None  # Harish

    # set xfer type
#     xfer_type = XFER_TYPE.FILE
    xfer_type = XFER_TYPE.URL

    # set xfer test
    xfer_test = "2MB"
    number_of_uploads = 1
    ##############################################################
    ##############################################################
    ##############################################################
    ##############################################################
    # START

    ##############################################################
    # Pick a file based on xfer_test
    sha256 = {}
    if xfer_type == XFER_TYPE.URL:
        url = "http://9.47.161.56:8080/SHA256SUM"
        r = requests.get(url)
        for line in r.content.strip().split("\n"):
            print line
            ws = line.split()
            sha256[ws[0]] = ws[1]
    elif xfer_type == XFER_TYPE.FILE:
        with open("/tmp/SHA256SUM", "r") as f:
            content = f.readlines()
        for line in content:
            ws = line.split()
            sha256[ws[0]] = ws[1]
    else:
        raise Exception("Programming error")

    image_file = {}
    image_size = {}  # for image_file only
    copy_from = {}

    # 2MB
    image_file["2MB"] = "/tmp/testfile2MB.txt"
    image_size["2MB"] = os.path.getsize(image_file["2MB"])
    copy_from["2MB"] = 'http://9.47.161.56:8080/testfile2MB.txt'
#     checksum = \
#         'e025e4f9d3ccf1a9b25202304d4a3d4822cd6e76843a51b803623f740bc03e66'

    # 1GB
    image_file["1GB"] = "/tmp/testfile1GB.txt"
    image_size["1GB"] = os.path.getsize(image_file["1GB"])
    copy_from["1GB"] = 'http://9.47.161.56:8080/testfile1GB.txt'
#     checksum = \
#         '6e86684bdba30e8f1997a652dcb2ba5a199880c44c2c9110b325cd4ca5f48152'

    # 2GB
    image_file["2GB"] = "/tmp/testfile2GB.txt"
    image_size["2GB"] = os.path.getsize(image_file["2GB"])
    copy_from["2GB"] = 'http://9.47.161.56:8080/testfile2GB.txt'
#     checksum = \
#         '067002c822d7b7f0a826c6bbd53d30b70b13048f25f10be2e9aacc8056bbc4cc'

    # PAVEL
    image_file["PAVEL"] = "/tmp/testfilePAVEL.txt"
    image_size["PAVEL"] = os.path.getsize(image_file["PAVEL"])
    copy_from["PAVEL"] = 'http://9.47.161.56:8080/testfilePAVEL.txt'
#     checksum = \
#         'b8bbde7ba106d0f6e6cd1c6e033bfa4e6e11d5b4b944aa3e6d08b5a7d3a4252e'

    # 3GB
    image_file["3GB"] = "/tmp/testfile3GB.txt"
    image_size["3GB"] = os.path.getsize(image_file["3GB"])
    copy_from["3GB"] = 'http://9.47.161.56:8080/testfile3GB.txt'
#     checksum = \
#         '18c0f13594702add11573ad72ed9baa42facad5ba5fe9a7194465a246a31e000'

    # 32GB
    image_file["32GB"] = "/tmp/testfile32GB.txt"
#     image_size["32GB"] = os.path.getsize(image_file["32GB"])
    image_size["32GB"] = 34359738368
    copy_from["32GB"] = 'http://9.47.161.56:8080/testfile32GB.txt'
#     checksum = \
#         'a3e5e6f1008d0745ae560160e1fccf162a31224c3fe97c1395b86a516d5a8d2e'

    ##############################################################
    # Authenticate
    print "authenticate"

    apiurl = ('https://%s/paxes/openstack/admin/v3/auth/tokens' %
              (paxes_ip, ))
    headers = {'Content-Type': 'application/json',
               'Vary': 'X-Auth-Token,X-Subject-Token',
               'Accept': 'application/json'}

    user_domain_name = "Default"
    user_name = "root"
    user_password = "passw0rd"
    project_domain_name = "Default"
    project_name = "ibm-default"

    data = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "domain": {
                            "name": user_domain_name
                        },
                        "name": user_name,
                        "password": user_password
                    }
                }
            },
            "scope": {
                "project": {
                    "domain": {
                        "name": project_domain_name
                    },
                    "name": project_name
                }
            }
        }
    }

    print apiurl
    resp = requests.request("POST",
                            apiurl,
                            headers=headers,
                            data=json.dumps(data),
                            verify=False)

    if resp.text:
        try:
            body = json.loads(resp.text)
        except ValueError:
            raise Exception("Can't jsonize: >%s<" % (resp.text,))
    else:
        raise Exception("No response")

    if resp.status_code >= 400:
        raise Exception("status_code: >%s<" % (resp.status_code,))

    catalog = _extract_catalog(body, paxes_ip)
    # hack to fix dns issue
    catalog['volume'] = catalog['volume']
    x_auth_token = resp.headers['x-subject-token']

    ##############################################################
    # test cinder w/ simple get
    print "test cinder w/ simple GET"

    apiurl = ('%s/types' %
              (catalog['volume'], ))
    print apiurl
    headers = {'X-Auth-Project-Id': 'demo',
               'Accept': 'application/json',
               'X-Auth-Token': x_auth_token}
    resp = requests.request("GET",
                            apiurl,
                            headers=headers,
                            verify=False)
    if resp.text:
        try:
            body = json.loads(resp.text)
        except ValueError:
            raise Exception("Can't jsonize: >%s<" % (resp.text,))
    else:
        raise Exception("No response")

    if resp.status_code >= 400:
        raise Exception("status_code: >%s<" % (resp.status_code,))

    print body

    ##############################################################
    # headers for image upload

    headers = {'X-Auth-Token': x_auth_token,
               'Content-Type': 'application/octet-stream',
               'x-imgupload-cinder-volume-id': x_imgupload_cinder_volume_id,
               'x-imgupload-hmc-id': hmc_id}

    # add vios header
    if vios is not None:
        print "VIOS specified: >%s<" % (vios,)
        headers['x-imgupload-vios-id'] = vios

    if xfer_type == XFER_TYPE.FILE:
        headers['x-imgupload-file-size'] = image_size[xfer_test]
        headers['Transfer-Encoding'] = 'chunked'

    if xfer_type == XFER_TYPE.FILE:
        k = image_file[xfer_test].rsplit("/")[-1]
    elif xfer_type == XFER_TYPE.URL:
        k = copy_from[xfer_test].rsplit("/")[-1]
    else:
        raise Exception("Programming error")

    headers['x-imgupload-file-checksum'] = sha256[k]

    ##############################################################
    # request

    apiurl = ('%s/imgupload' %
              (catalog['volume'], ))

    for i in range(number_of_uploads):

        print "Try number: >%d<" % (i,)

        if xfer_type == XFER_TYPE.URL:
            # url specific headers
            headers['x-imgupload-copy-from'] = copy_from[xfer_test]

            print "Upload w/ URL"
            resp = requests.request("POST",
                                    apiurl,
                                    headers=headers,
                                    verify=False)
            if resp.text:
                try:
                    body = json.loads(resp.text)
                except ValueError:
                    pass
                    body = None
            else:
                body = None
            print resp
            if resp.status_code >= 400:
                print resp.json()
                raise Exception("status._code: >%s<, reason: >%s<" %
                                (resp.status_code, resp.reason))

            print body

        elif xfer_type == XFER_TYPE.FILE:
            # local file specific headers
            print "Upload file"
            print paxes_ip
            cinder_conn = httplib.HTTPSConnection(paxes_ip, '443')

            print apiurl

            cinder_conn.putrequest("POST", apiurl)

            print "POST"
            for header, value in headers.items():
                cinder_conn.putheader(header, value)
            cinder_conn.endheaders()

            CHUNKSIZE = 1024 * 64  # 64kB
            f = open(image_file[xfer_test])
            chunk = f.read(CHUNKSIZE)
            # Chunk it, baby...
            while chunk:
                cinder_conn.send('%x\r\n%s\r\n' % (len(chunk), chunk))
                chunk = f.read(CHUNKSIZE)
            cinder_conn.send('0\r\n\r\n')
            f.close()

            print "RESPONSE"
            response = cinder_conn.getresponse()
            response_read = response.read()

            print response
            if response.status != httplib.OK:
                logger.error(("from cinder, unexpected response.status: >%s<,"
                              " response.read: >%s<, post for new image from "
                              "file failed, quitting ..."),
                             response.status, response_read)

            if response.status == httplib.OK:  # 200
                datajson = json.loads(response_read)
                print datajson

            cinder_conn.close()
        else:
            raise ValueError("bad type")

        logger.info("all done")


########
# upload stuff
def _sha256sum(filename):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * sha256.block_size), b''):
            sha256.update(chunk)
        return sha256.hexdigest()


def _createtestfile(fspec='/tmp/testfile.txt',
                    size=1024 * 1024 * 1024 * 3):

    start = "start"
    end = "end"
    with open(fspec, 'wb') as f:
        f.write(start)
        f.seek(size - len(start) + 2)
        f.write(end)

    f.close()

    size = os.path.getsize(fspec)
    sha256 = _sha256sum(fspec)
    print ("Created: >%s<, with size: >%d<, with sha256: >%s<" % (fspec,
                                                                  size,
                                                                  sha256))

    return (fspec, size, sha256)


def createtestfiles():

    # 2 MB
    f2mb = _createtestfile(fspec='/tmp/testfile2MB.txt',
                           size=1024 * 1024 * 2)
    d2mb = ("dd if=/dev/hdisk6 of=/UPLOAD-TESTS/testfile2MB.txt."
            "2MB bs=1048576 count=2")

    # 1 GB
    f1gb = _createtestfile(fspec='/tmp/testfile1GB.txt',
                           size=1024 * 1024 * 1024 * 1)
    d1gb = ("dd if=/dev/hdiskx of=/UPLOAD-TESTS/testfile1GB.txt."
            "1GB bs=1048576 count=1024")

    # 2 GB
    f2gb = _createtestfile(fspec='/tmp/testfile2GB.txt',
                           size=1024 * 1024 * 1024 * 2)
    d2gb = ("dd if=/dev/hdiskx of=/UPLOAD-TESTS/testfile2GB.txt."
            "2GB bs=1048576 count=2048")

    # Pavel's number
    fpavel = _createtestfile(fspec='/tmp/testfilePAVEL.txt',
                             size=1024 * 1024 * 2052)
    dpavel = ("dd if=/dev/hdiskx of=/UPLOAD-TESTS/testfilePAVEL.txt."
              "PAVEL bs=1048576 count=2051")

    # 3 GB
    f3gb = _createtestfile(fspec='/tmp/testfile3GB.txt',
                           size=1024 * 1024 * 1024 * 3)
    d3gb = ("dd if=/dev/hdiskx of=/UPLOAD-TESTS/testfile3GB.txt."
            "3GB bs=1048576 count=3072")

    # 32 GB
    f32gb = _createtestfile(fspec='/tmp/testfile32GB.txt',
                            size=1024 * 1024 * 1024 * 32)
    d32gb = ("dd if=/dev/hdiskx of=/UPLOAD-TESTS/testfile32GB.txt."
             "3GB bs=1048576 count=32768")

    kfspec = "/tmp/SHA256SUM"
    with open(kfspec, "w") as f:
        for i in [f2mb, f1gb, f2gb, fpavel, f3gb, f32gb]:
            (fspec, size, sha256) = i
            fspec = fspec.rsplit("/")[-1]
            f.write("%s %s\n" % (fspec, sha256))
    print "Output sha256 keys: >%s<" % (kfspec,)

    for i in [d2mb, d1gb, d2gb, dpavel, d3gb, d32gb]:
        print i

    with open("/tmp/SHA256SUM", "r") as f:
        content = f.readlines()

    for line in content:
        ws = line.split()
        print ws[0], ws[1]

if __name__ == '__main__':

    # to generate test files
#     sys.exit(createtestfiles())

    # to runtest
    sys.exit(runtest())

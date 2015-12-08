#
#
# =================================================================
# =================================================================

import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient import client
import logging
import textwrap
import os

_tw = textwrap.TextWrapper()
_targetdir = "/home/openstack/janus-paxes-trunk-sandbox/" +\
    "paxes-cinder/tests/k2aclient/v1/k2_mock"""

_mock_head = '''# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# =================================================================
# =================================================================

k2resp = """'''

_mock_tail = '''"""
'''


def gen_mock(cs, uom, fn):
    k2resp = cs.uom.get(uom)

    targetfn = os.path.join(_targetdir, fn)

    body = k2resp.body
# for option 1 and 2
#     body = body.replace("\n", "")

##### Option 1 has collapsed blanks
#     lines = [""]
#     lno = 0
#     for i in xrange(len(body)):
#         if (i % 70) == 0:
#             lno += 1
#             lines.append("")
#         lines[lno] += body[i]
#
#     # now output
#     with open(targetfn, 'w') as f:
#         f.write(_mock_head)
#         for line in lines:
#             f.write(line.rstrip() + "\n")
#         f.write(_mock_tail)

##### Option 2 has collapsed blank problem
#     # now output
#     with open(targetfn, 'w') as f:
#         f.write(_mock_head)
#         for i in xrange(len(body)):
#             if (i % 70) == 0:
#                 f.write("\n")
#             f.write(body[i])
#         f.write(_mock_tail)

##### Option 3 just output and exempt from pep8
    with open(targetfn, 'w') as f:
        f.write(_mock_head)
        f.write(body)
        f.write(_mock_tail)


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

    gen_mock(cs, "/Cluster",
             "mock_cluster_list.py")
    gen_mock(cs, "/SharedStoragePool/e9b6b0fa-62c1-3d35-806b-63be1ff10b00",
             "mock_ssp_get.py")
    gen_mock(cs, "/Cluster/a9dbe07f-30c4-3788-8f6f-659aa1d66502",
             "mock_cluster_get.py")

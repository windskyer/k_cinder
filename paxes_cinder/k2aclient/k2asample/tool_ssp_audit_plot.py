#
#
# =================================================================
# =================================================================


import eventlet
from itertools import repeat
from collections import deque
import time
import pickle
from paxes_cinder.k2aclient.k2asample.tool_ssp_simulation import MockLu, \
    ImagePool

import re
import time
from sets import Set

import matplotlib.pyplot as plt
import numpy as np

markers = [
    (".", "point"),
    (",", "pixel"),
    ("o", "circle"),
    ("v", "triangle_down"),
    ("^", "triangle_up"),
    ("<", "triangle_left"),
    (">", "triangle_right"),
    ("1", "tri_down"),
    ("2", "tri_up"),
    ("3", "tri_left"),
    ("4", "tri_right"),
    ("8", "octagon"),
    ("s", "square"),
    ("p", "pentagon"),
    ("*", "star"),
    ("h", "hexagon1"),
    ("H", "hexagon2"),
    ("+", "plus"),
    ("x", "x"),
    ("D", "diamond"),
    ("d", "thin_diamond")
]

colors = [
    ("b", "blue"),
    ("g", "green"),
    ("r", "red"),
    ("c", "cyan"),
    ("m", "magenta"),
    ("y", "yellow"),
    ("k", "black"),  # ("w", "white")
]

from paxes_cinder.k2aclient.k2asample.tool_ssp_simulation import \
    OperationType, \
    Simulation, \
    Operation


def plotD(s):
    x = s.total_number_of_image_deploys + s.total_number_of_snapshot_deploys
    plt.figure("SSP: Instances: %s" % (x,))
    plt.xlabel('Time')
    plt.ylabel('Instances')
    plt.title('SSP: Instances vs. Elapsed Time')
    plt.grid(True)

    leno = len(s.operations)
    DAO = s.deploys_at_oper
    SAO = s.snapshots_at_oper
    TIME = []
    for i, (o, e, t, x) in enumerate(s.operations):
        if i == 0:
            x0 = x
        TIME.append((x - x0) / 60.)
#     pDAO, = plt.plot(xrange(leno), DAO, 'bo')
#     pSAO, = plt.plot(xrange(leno), SAO, 'bv')
    pDAO, = plt.plot(TIME, DAO)
    pSAO, = plt.plot(TIME, SAO)

#     ymax = max([max(DFIa),max(DFIb),max(DFSa),max(DFSb)])
    plt.legend([pDAO, pSAO],
               ["Deploys", "Snapshots"],
               loc=4,
               prop={'size': 8})
    ymax = max([max(DAO), max(SAO)])
    plt.axis([0, TIME[-1], 0, ymax * 1.25])
    plt.show()


def plotB(s):
    x = s.total_number_of_image_deploys + s.total_number_of_snapshot_deploys
    plt.figure("SSP: Instances: %s" % (x,))
    plt.xlabel('Operation number')
    plt.ylabel('Instances')
    plt.title('SSP: Instances vs. Operation number')
    plt.grid(True)

    leno = len(s.operations)
    DAO = s.deploys_at_oper
    SAO = s.snapshots_at_oper
#     pDAO, = plt.plot(xrange(leno), DAO, 'bo')
#     pSAO, = plt.plot(xrange(leno), SAO, 'bv')
    pDAO, = plt.plot(xrange(leno), DAO)
    pSAO, = plt.plot(xrange(leno), SAO)

#     ymax = max([max(DFIa),max(DFIb),max(DFSa),max(DFSb)])
    plt.legend([pDAO, pSAO],
               ["Deploys", "Snapshots"],
               loc=4,
               prop={'size': 8})
    ymax = max([max(DAO), max(SAO)])
    plt.axis([0, leno - 1, 0, ymax * 1.25])
    plt.show()


def plotA(data, datafilter, jobs, jobsfilter):

    PLS = []

    datafilter_filter = []
    datafilter_display = []
    for (df, dd) in datafilter:
        datafilter_filter.append(df)
        datafilter_display.append(dd)

    jobsfilter_filter = []
    jobsfilter_display = []
    for (df, dd) in jobsfilter:
        jobsfilter_filter.append(df)
        jobsfilter_display.append(dd)

    # data
    num_ops = 0
    for k, dps in data.iteritems():
        if k in datafilter_filter:
            display = datafilter_display[datafilter_filter.index(k)]
            PLSt = []
            PLSv = []
            for (t, v) in dps:
                num_ops += 1
                PLSt.append(t / 3600.0)
                PLSv.append(v)
            PLS.append((display, PLSt, PLSv))

    # tjobs
    num_jobs = 0
    for k, dps in jobs.iteritems():
        if k in jobsfilter_filter:
            display = jobsfilter_display[jobsfilter_filter.index(k)]
            PLSt = []
            PLSv = []
            for (t, v) in dps:
                num_jobs += 1
                PLSt.append(t / 3600.0)
                PLSv.append(v)
            PLS.append((display, PLSt, PLSv))

#         print dps
#         for (t,v) in dps:
#             PLSt.append(t)
#             PLSv.append(v)
#         PLS.append(("JOB", PLSt, PLSv))

    plt.figure("SSP: Deploy of %d ops and  %d jobs" %
               (num_ops, num_jobs))
    msg = ("Operations: %d\n"
           "Jobs = %d\n")
    msg = msg % (num_ops,
                 num_jobs,)
#     plt.text(1, 1.0, 'Total number of deploys = %s\nfoo' % (x,), fontsize=8)

#     plt.text(400, 22.0, msg, fontsize=8)
    plt.text(.2, 7.0, msg, fontsize=8)

    legplot = []
    leglabl = []
    xmaxa = []
    ymaxa = []
    for i, plot in enumerate(PLS):
        display, PLSt, PLSv = plot
        ci = i % len(colors)
        xmaxa.append(max(PLSt))
        ymaxa.append(max(PLSv))
#         print colors[ci][0]
        legplot.append(plt.plot(PLSt, PLSv, colors[ci][0] + "o")[0])
        leglabl.append(display)

#     DFIi = PLSt
#     DFIa = PLSv
#
#     pDFIa, = plt.plot(DFIi, DFIa, 'bo')
    plt.legend(legplot,
               leglabl,
               loc=2,
               prop={'size': 8})
    xmax = max(xmaxa)
    ymax = max(ymaxa)
#
#     ymax = max([max(DFIa)])
#     xmax = max([max(DFIi)])
    plt.axis([0, xmax, 0, ymax * 1.25])
    plt.xlabel('Elapsed time (hrs)')
    plt.ylabel('Operation time (sec)')
    plt.title('Operation time vs. Elapsed time')  # message
    title = "NO TITLE"
    if hasattr(s, "title"):
        title = s.title
    msg = ("Deploy an LU:\n"
           "    .... -> (POST LU -> LULinkedClone -> GET LU) -> ...")
    plt.text(1, 40.0, msg, fontsize=14)
    plt.grid(True)
    plt.show()

    # lines
#     pDFIa, = plt.plot(DFIi, DFIa, 'bo')
#     pDFIb, = plt.plot(DFIi, DFIb, 'bv')
#     pDFIx, = plt.plot(DFIi, DFIx, 'bx')
#     pDFSa, = plt.plot(DFSi, DFSa, 'ko')
#     pDFSb, = plt.plot(DFSi, DFSb, 'kv')
#     pSADa, = plt.plot(SADi, SADa, 'co')
#     pSADb, = plt.plot(SADi, SADb, 'cv')
#     pDASa, = plt.plot(DASi, DASa, 'mo')
#     pDADa, = plt.plot(DADi, DADa, 'yo')
#     pEEEa, = plt.plot(EEEi, EEEa, 'ro')

#     plt.legend([pDFIa, pDFIb, pDFIx,
#                 pDFSa, pDFSb, pSADa, pSADb, pDASa, pDADa, pEEEa],
#                ["DeployFromImage-Create", "DeployFromImage-Clone",
#                 "DeployFromImage-Total",
#                 "DeployFromSnap-Create", "DeployFromSnap-Clone",
#                 "SnapaDeploy-Create", "SnapaDeploy-Clone",
#                 "DelaSnap",
#                 "DelaDeploy",
#                 "Exception"],
#                loc=2,
#                prop={'size': 8})
#     ymax = max([max(DFIa), max(DFIb), max(DFIx)])
#     plt.axis([0, len(s.operations) - 1, 0, ymax * 1.25])
#     plt.show()

    return

    msg = "total_number_of_image_deploys >%d<"
    print msg % (s.total_number_of_image_deploys,)
    msg = "total_number_of_snapshot_deploys >%d<"
    print msg % (s.total_number_of_snapshot_deploys,)
    msg = "total_number_of_snapshots >%d<"
    print msg % (s.total_number_of_snapshots,)

#         # the histogram of the data
#         n, bins, patches = plt.hist(len(s.operations), 50, normed=1,
#                                     facecolor='g', alpha=0.75)
#
#         plt.xlabel('Smarts')
#         plt.ylabel('Probability')
#         plt.title('Histogram of IQ')
#         plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
#         plt.axis([40, 160, 0, 0.03])
#         plt.grid(True)
#         plt.show()

#     x = s.total_number_of_image_deploys + s.total_number_of_snapshot_deploys
#     plt.figure("SSP: Deploy: %s" % (x,))
#     plt.xlabel('Operation number')
#     plt.ylabel('Operation time (sec)')
#     plt.title('SSP: Operation time vs. Operation number')
#     plt.grid(True)
#     for (d, o) in s.deploy_inflections:
#         print d
#         if d == "D2I":
#             plt.axvline(x=o, linewidth=1, color='r')
#         else:
#             plt.axvline(x=o, linewidth=1, color='r', linestyle="dashed")
#     for (d, o) in s.snapshot_inflections:
#         print d
#         if d == "D2I":
#             plt.axvline(x=o, linewidth=1, color='b')
#         else:
#             plt.axvline(x=o, linewidth=1, color='b', linestyle="dashed")

#     # message
#     title = "NO TITLE"
#     if hasattr(s, "title"):
#         title = s.title
#     msg = ("Title: >%s<\n"
#            "Total number of deploys = %s\n"
#            "Deploys: min: %d, max: %d\n"
#            "Snapshots: min: %d, max: %d\n"
#            "Image pool size: %d\n"
#            "Threads: %d")
#     msg = msg % (x,
#                  title,
#                  s.min_deploys, s.max_deploys,
#                  s.min_snapshots, s.max_snapshots,
#                  s.image_pool_size,
#                  s.num_threads)
# #     plt.text(1, 1.0, 'Total number of deploys = %s\nfoo' % (x,),
# #              fontsize=8)
#     plt.text(10, 75.0, msg, fontsize=8)

    # lines
#     pDFIa, = plt.plot(DFIi, DFIa, 'bo')
#     pDFIb, = plt.plot(DFIi, DFIb, 'bv')
#     pDFIx, = plt.plot(DFIi, DFIx, 'bx')
#     pDFSa, = plt.plot(DFSi, DFSa, 'ko')
#     pDFSb, = plt.plot(DFSi, DFSb, 'kv')
#     pSADa, = plt.plot(SADi, SADa, 'co')
#     pSADb, = plt.plot(SADi, SADb, 'cv')
#     pDASa, = plt.plot(DASi, DASa, 'mo')
#     pDADa, = plt.plot(DADi, DADa, 'yo')
#     pEEEa, = plt.plot(EEEi, EEEa, 'ro')

# #     ymax = max([max(DFIa),max(DFIb),max(DFSa),max(DFSb)])
#     plt.legend([pDFIa, pDFIb, pDFIx,
#                 pDFSa, pDFSb, pSADa, pSADb, pDASa, pDADa, pEEEa],
#                ["DeployFromImage-Create", "DeployFromImage-Clone",
#                 "DeployFromImage-Total",
#                 "DeployFromSnap-Create", "DeployFromSnap-Clone",
#                 "SnapaDeploy-Create", "SnapaDeploy-Clone",
#                 "DelaSnap",
#                 "DelaDeploy",
#                 "Exception"],
#                loc=2,
#                prop={'size': 8})
#     ymax = max([max(DFIa), max(DFIb), max(DFIx)])
#     plt.axis([0, len(s.operations) - 1, 0, ymax * 1.25])
    plt.show()

if __name__ == '__main__':

#     ("POST",
#      "/rest/api/uom/SharedStoragePool/39cc86f0-bc1a-33a8-8d22-20c4b4f3a8d3",
#      "200")
#     ("POST",
#      "/rest/api/uom/SharedStoragePool/39cc86f0-bc1a-33a8-8d22-20c4b4f3a8d3",
#      "412")
#     ("POST",
#      "/rest/api/uom/SharedStoragePool/39cc86f0-bc1a-33a8-8d22-20c4b4f3a8d3",
#      "412")
#
#     ("GET",
#      "/rest/api/uom/Cluster/c43fbdcd-95f2-3b4a-b643-234ff00eded4",
#      "200")
#     ("")

    p = re.compile(r'^<\d+>\d+ (?P<minute>\d\d\d\d-\d\d-\d\dT\d\d:\d\d):'
                   '(?P<second>.*)Z '
                   '.* REST - PMCA\d\d\d\d \['
                   '(?P<params>.*)\](?P<remain>.*)')

    # >  Job START: Operation="ClusterLULinkedClone"; JobID="1394637525237".<
    js = re.compile(r'^  Job START: Operation="(?P<oper>.*)";'
                    ' JobID="(?P<jobid>.*)"\.')

    # >  Job  END : Operation="ClusterLULinkedClone"; JobID="1394637525241";
    #   Status="COMPLETED_OK".<
    je = re.compile(r'^  Job  END : Operation="(?P<oper>.*)";'
                    ' JobID="(?P<jobid>.*)"; Status="(?P<status>.*)"\.')
#     p = re.compile(r'<\d+>\d+ \d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\dZ.*')

    start = "2014-03-14T11:21:56.780Z"
    start = "2014-03-14T12:37:07.202Z"
    start = "2014-03-14T12:37:22.769Z"
    start = "2014-03-18T07:00:02.910Z"
    stop = "2014-03-15T00:22:16.485Z"
    # OLD
    datafilter = [("GET%/rest/api/uom/SharedStoragePool/"
                   "39cc86f0-bc1a-33a8-8d22-20c4b4f3a8d3", "GET LU"),
                  ("POST%/rest/api/uom/SharedStoragePool/"
                   "39cc86f0-bc1a-33a8-8d22-20c4b4f3a8d3", "POST LU")]
    jobsfilter = [("ClusterLULinkedClone", "LULinkedClone")]
    auditlog = 'my_audit_REJY_0314A'
    auditlog = 'my_audit_REJY_0318A'

    datafilter = []
    jobsfilter = [("ClusterLULinkedClone", "LULinkedClone"),
                  ("ClusterCreateLogicalUnit", "CreateLogicalUnit")]

#     auditlog = 'my_audit_REJY_0321A'
#     start = "2014-03-22T05:00:56.780Z"

#     auditlog = 'my_audit_REJY_0321B'
#     start = "2014-03-22T11:03:30.631Z"

    auditlog = 'my_audit_REJY_0323A'
    start = "2014-03-24T00:52:42.593Z"

    datafilter = [("GET%/rest/api/uom/SharedStoragePool/"
                   "29915d6b-86af-3fdd-8a8d-fea6cab1dc91"
                   "%200", "GET LU 200"),
                  ("POST%/rest/api/uom/SharedStoragePool/"
                   "29915d6b-86af-3fdd-8a8d-fea6cab1dc91"
                   "%200", "POST LU 200"),
                  ("POST%/rest/api/uom/SharedStoragePool/"
                   "29915d6b-86af-3fdd-8a8d-fea6cab1dc91"
                   "%412", "POST LU 412")
                  ]
    jobsfilter = [("ClusterCreateLogicalUnit", "CreateLogicalUnit")]

    auditlog = 'my_audit/my_audit_N7_0404A'
    start = "2014-04-04T17:48:32.285Z"
    auditlog = 'my_audit/my_audit_N7_0406A'
    start = "2014-04-07T01:35:19.301Z"
    auditlog = 'my_audit/my_audit_N7_0407A'
    start = "2014-04-07T01:35:19.301Z"
    auditlog = 'my_audit/my_audit_N7_0407B'
    start = "2014-04-07T18:05:21.210Z"
    auditlog = 'my_audit/my_audit_N7_0407C'
    start = "2014-04-08T01:52:07.478Z"
    auditlog = 'my_audit/my_audit_N7_0408A'
    start = "2014-04-08T17:10:47.093Z"
    auditlog = 'my_audit/my_audit_N7_0409A'
    start = "2014-04-09T04:55:58.319Z"

    totals = {}
    data = {}
    tjobs = {}
    running_jobs = Set()
    started = False
    first = True
    count = 0
    with open(auditlog, 'r') as f:
#         s = f.readline()
        for s in f:
#
#             print s
            m = p.match(s)
            # 2014-03-14T11:21:52.497
            # 2014-03-14T11:21 minute
            # 52.497 second
            ms = m.group('minute')
#             print ms
            ss = m.group('second')
#             print ss
            fs = ms + ":" + ss + "Z"

#             print fs
            if not started and fs == start:
                started = True
            if not started:
                continue

#             print s

    #         print fs
            mt = time.strptime(ms, "%Y-%m-%dT%H:%M")
#             convert to seconds since epoch
            sse = time.mktime(mt) + float(ss)
            if first:
                sse0 = sse
                first = False
            sselapsed = sse - sse0
#             print (sse - sse0) / 3600.0
            # add seconds
#             mt.tm_sec = float(ss)
#             print mt
            ps = m.group('params')
            psas = ps.split(" ", 1)[1]
    #         print psas
            d = {}
            while len(psas) > 0:
                equal = psas.find("=")
                name = psas[:equal]
                psas = psas[equal + 2:]
                quote = psas.find('"')
                value = psas[:quote]
                d[name] = value
                psas = psas[quote + 2:]
#             print d
            if "HM" in d:
                key = d["HM"] + "%" + d["URI"] + "%" + d["HS"]
                # totals
                if key not in totals:
                    totals[key] = 0
                totals[key] += float(d["ET"])
                if d["HM"] == "POST" and d["HS"] == "200":
                    count += 1

                # data
                if key not in data:
                    data[key] = []
                d = (sselapsed, float(d["ET"]))
                data[key].append(d)
            else:
                rs = m.group('remain')
#                 print "rs: >%s<" % (rs,)

                jse = js.match(rs)
                if jse:
#                     print ("JOB START: oper: >%s<, jobid: >%s<" %
#                            (jse.group('oper'), jse.group('jobid')))
                    jobid = jse.group('jobid')
                    running_jobs.add(jobid)
                    d = sselapsed
                    tjobs[jobid] = d

                jee = je.match(rs)
                if jee:
                    jobid = jee.group('jobid')
                    oper = jee.group('oper')
                    if jobid in tjobs:
#                         print ("JOB END: oper: >%s<, jobid: >%s<,"
#                                " status: >%s<, sselapsed: >%f<,"
#                                " opertime: >%f<" %
#                                (jee.group('oper'),
#                                 jee.group('jobid'),
#                                 jee.group('status'),
#                                 sselapsed, sselapsed - tjobs[jobid]))
                        running_jobs.remove(jobid)
                        d = (oper, sselapsed, sselapsed - tjobs[jobid])
                        tjobs[jobid] = d

    if len(running_jobs) > 0:
        for rj in running_jobs:
            del tjobs[rj]

    jobs = {}
    for k, v in tjobs.iteritems():
        (oper, t, et) = v
        if oper not in jobs:
            jobs[oper] = []
        jobs[oper].append((t, et))

    print count
    print totals

#     raise Exception("quit")

#         print d
    #         value_end = psas[]
    #         print psas[equal+2:]
#             print "name: >%s<, value: >%s<" % (name, value)
#         d = {}
#         d["p0"] = psas[0]
#         for psa in psas:
#             equal = psa.find("=")
#             name = psa[:equal]
#
#             print psa.split("=")
#             value_start = psa[equal+2:]

#         print m.groups()

    plotA(data, datafilter, jobs, jobsfilter)
#     plotB(s)
#     plotD(s)

    # http://stackoverflow.com/questions/7733693/
    # matplotlib-overlay-plots-with-different-scales

# marker    description
# "."    point
# ","    pixel
# "o"    circle
# "v"    triangle_down
# "^"    triangle_up
# "<"    triangle_left
# ">"    triangle_right
# "1"    tri_down
# "2"    tri_up
# "3"    tri_left
# "4"    tri_right
# "8"    octagon
# "s"    square
# "p"    pentagon
# "*"    star
# "h"    hexagon1
# "H"    hexagon2
# "+"    plus
# "x"    x
# "D"    diamond
# "d"    thin_diamond
# "|"    vline
# "_"    hline
# TICKLEFT    tickleft
# TICKRIGHT    tickright
# TICKUP    tickup
# TICKDOWN    tickdown
# CARETLEFT    caretleft
# CARETRIGHT    caretright
# CARETUP    caretup
# CARETDOWN    caretdown
# "None"    nothing
# None    nothing
# " "    nothing
# ""    nothing
# '$...$'    render the string using mathtext.
# verts    a list of (x, y) pairs used for Path vertices.
# path    a Path instance.
# (numsides, style, angle)    see below

# The location of the legend can be specified by the keyword argument loc,
# either by string or a integer number.
#
# String    Number
# upper right    1
# upper left    2
# lower left    3
# lower right    4
# right    5
# center left    6
# center right    7
# lower center    8
# upper center    9
# center    10

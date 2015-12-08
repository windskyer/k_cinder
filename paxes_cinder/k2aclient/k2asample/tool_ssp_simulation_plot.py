#
#
# =================================================================
# =================================================================


import eventlet
from itertools import repeat
from collections import deque
import time
import datetime
import pickle
from paxes_cinder.k2aclient.k2asample.tool_ssp_simulation import MockLu, \
    ImagePool


import matplotlib.pyplot as plt
import numpy as np


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


def plotA(s):
    DFIi = []
    DFIa = []
    DFIb = []
    DFIx = []

    DFSi = []
    DFSa = []
    DFSb = []

    SADi = []
    SADa = []
    SADb = []

    DASi = []
    DASa = []

    DADi = []
    DADa = []

    EEEi = []
    EEEa = []

    for i, (o, e, t, x) in enumerate(s.operations):
        if e is not None:
#             EEEa.append(t[0])
            print "FIXME", i
            EEEa.append(1)
            EEEi.append(i)
        elif o == OperationType.DEPLOY_FROM_IMAGE:
            print "DEPLOY", t[0], i
            DFIa.append(t[0])
            DFIb.append(t[1])
            DFIx.append(t[0] + t[1])
            DFIi.append(i)
        elif o == OperationType.DEPLOY_FROM_SNAPSHOT:
            DFSa.append(t[0])
            DFSb.append(t[1])
            DFSi.append(i)
        elif o == OperationType.SNAPSHOT_A_DEPLOY:
            SADa.append(t[0])
            SADb.append(t[1])
            SADi.append(i)
        elif o == OperationType.DELETE_A_SNAPSHOT:
            DASa.append(t[0])
            DASi.append(i)
        elif o == OperationType.DELETE_A_DEPLOY:
            print "DELETE", t[0], i
            DADa.append(t[0])
            DADi.append(i)

# OperationType = _enum("DEPLOY_FROM_IMAGE",
#                       "DEPLOY_FROM_SNAPSHOT",
#                       "SNAPSHOT_A_DEPLOY",
#                       "DELETE_A_SNAPSHOT",
#                       "DELETE_A_DEPLOY")

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

    x = s.total_number_of_image_deploys + s.total_number_of_snapshot_deploys
    total_time = s.checkpoint_time - s.start_time
    plt.figure("SSP: Deploy: %s, ET: %s" %
               (x, datetime.timedelta(seconds=int(total_time))))
    plt.xlabel('Operation number')
    plt.ylabel('Operation time (sec)')
    plt.title('SSP: Operation time vs. Operation number')
    plt.grid(True)
    for (d, o) in s.deploy_inflections:
        print d
        if d == "D2I":
            plt.axvline(x=o, linewidth=1, color='r')
        else:
            plt.axvline(x=o, linewidth=1, color='r', linestyle="dashed")
    for (d, o) in s.snapshot_inflections:
        print d
        if d == "D2I":
            plt.axvline(x=o, linewidth=1, color='b')
        else:
            plt.axvline(x=o, linewidth=1, color='b', linestyle="dashed")

    # message
    title = "NO TITLE"
    if hasattr(s, "title"):
        title = s.title
    msg = ("Title: %s\n"
           "Total number of deploys = %s\n"
           "Deploys: min: %d, max: %d\n"
           "Snapshots: min: %d, max: %d\n"
           "Image pool size: %d\n"
           "Threads: %d\n"
           "Elapsed time: %s")
    et = datetime.timedelta(seconds=int(s.checkpoint_time - s.start_time))
    msg = msg % (title,
                 x,
                 s.min_deploys, s.max_deploys,
                 s.min_snapshots, s.max_snapshots,
                 s.image_pool_size,
                 s.num_threads,
                 et
                 )
#     plt.text(1, 1.0, 'Total number of deploys = %s\nfoo' % (x,), fontsize=8)

#     plt.text(400, 22.0, msg, fontsize=8)
    plt.text(10, 16.0, msg, fontsize=8)

    # lines
    two_step = False
    pDFIa, = plt.plot(DFIi, DFIa, 'bo')
    if two_step:
        pDFIb, = plt.plot(DFIi, DFIb, 'bv')
    pDFIx, = plt.plot(DFIi, DFIx, 'bx')
    pDFSa, = plt.plot(DFSi, DFSa, 'ko')
    if two_step:
        pDFSb, = plt.plot(DFSi, DFSb, 'kv')
    pSADa, = plt.plot(SADi, SADa, 'co')
    if two_step:
        pSADb, = plt.plot(SADi, SADb, 'cv')
    pDASa, = plt.plot(DASi, DASa, 'mo')
    pDADa, = plt.plot(DADi, DADa, 'yo')
    pEEEa, = plt.plot(EEEi, EEEa, 'ro')

#     ymax = max([max(DFIa),max(DFIb),max(DFSa),max(DFSb)])
    if not two_step:
        plt.legend([
            pDFIa,
            pDFSa,
            pSADa,
            pDASa,
            pDADa,
            pEEEa], [
                "DeployFromImage-Clone",
                "DeployFromSnap-Clone",
                "SnapaDeploy-Clone",
                "DelaSnap",
                "DelaDeploy",
                "Exception"],
            loc=2,
            prop={'size': 8})
        ymax = 0.0
        for m in [DFIa, DFSa, SADa, DASa, DADa, EEEa]:
            if len(m) > 0:
                ymax = max([max(m), ymax])
    else:
        plt.legend([
            pDFIa, pDFIb, pDFIx,
            pDFSa, pDFSb,
            pSADa, pSADb,
            pDASa, pDADa,
            pEEEa], [
                "DeployFromImage-Create", "DeployFromImage-Clone",
                "DeployFromImage-Total",
                "DeployFromSnap-Create", "DeployFromSnap-Clone",
                "SnapaDeploy-Create", "SnapaDeploy-Clone",
                "DelaSnap",
                "DelaDeploy",
                "Exception"],
            loc=2,
            prop={'size': 8})
        # broke ....
        ymax = max([max(DFIx),
                    max(DADa)])
    plt.axis([0, len(s.operations) - 1, 0, ymax * 1.25])
    plt.show()

if __name__ == '__main__':

#     with open('my_sim_001_1000_deploys_122813', 'r') as f:
#     with open('my_sim_001_1000_deploys_010814A', 'r') as f:
#     with open('my_sim_002_1000_N23N24', 'r') as f:
#     with open('my_sim_003_1000_deploys_N23N24_140123A', 'r') as f:
#     with open('my_sim_003_SW241507_N23N24_5threads', 'r') as f:
#     with open('my_sim_003_140124A_1007_deploys_N23N24_5threads', 'r') as f:
#     with open('my_sim_003_140124A_709_deploys_N23N24_1thread', 'r') as f:
#     with open(('my_sim_003_140124A_319_'
#                'deploys_N23N24_1thread_10Pool'), 'r') as f:
#     with open('my_sim_003', 'r') as f:
#     with open('my_sim_003_gerald_1thread_29', 'r') as f:
#     with open('my_sim_003_gerald', 'r') as f:
#     with open('my_sim_003_N8_810_1000_deploys', 'r') as f:
#     with open('my_sim_003_225_hmc5', 'r') as f:
#     with open('my_sim_003_225', 'r') as f:
#     with open('my_sim_003_N8', 'r') as f:
#     with open('my_sim_003_REJY_0221A_1003', 'r') as f:
#     with open('my_sim_003_N7_0225A_1003_deploys', 'r') as f:
#     with open('my_sim_003_N7_0226A_1003_deploys', 'r') as f:
#     with open('my_sim_003_N7', 'r') as f:
#     with open('my_sim_003_cluster_a_1003_140228A', 'r') as f:
#     with open('my_sim_003_cluster_a_1003_140228A_AFTER', 'r') as f:
#     with open('my_sim_003_cluster_a', 'r') as f:
#     with open('my_sim_003_gerald_168_1003_140303A', 'r') as f:
#     with open('my_sim_003_gerald_168', 'r') as f:
#     with open('my_sim_003_cluster_a', 'r') as f:
#     with open('my_sim_003_cluster_a_1003_140305A', 'r') as f:
#     with open('my_sim_003_cluster_a', 'r') as f:
#     with open('my_sim_003_cluster_a_1003_140306A', 'r') as f:
#     with open('my_sim_003_REJY', 'r') as f:
#     with open('my_sim_003_REJY_0314A_1003', 'r') as f:
#     with open('my_sim_003_REJY_0317A_288', 'r') as f:
#     with open('my_sim_003_REJY', 'r') as f:
#     with open('my_sim_003_REJY_0318A_1003', 'r') as f:
#     with open('my_sim_003', 'r') as f:
#     with open('my_sim_003_cluster_a', 'r') as f:
#     with open('my_sim_003_cluster_a_0321A_1003', 'r') as f:
#     with open('my_sim_003_REJY', 'r') as f:
#     with open('my_sim_003_REJY_0321B_1007_threads', 'r') as f:
#     with open('my_sim_003_REJY', 'r') as f:my_sim_003_N8_0327A_1K
#     with open('my_sims/my_sim_003_REJY_0323A_1003', 'r') as f:
#     with open('my_sim_003_N8_0327A_1K', 'r') as f:
#     with open('my_sim_003_N8_0327B_1K_5thread', 'r') as f:
#     with open('my_sim_003_N7_0407A_SIMPLERAMPS_2K_5thread', 'r') as f:
#     with open('my_sim_003_N7_0407C_SIMPLERAMPS_2K_5thread', 'r') as f:
    with open('my_sim_003_N7', 'r') as f:
        s = pickle.load(f)
    plotA(s)
    plotB(s)
    plotD(s)

    # http://stackoverflow.com/questions/7733693/
    # matplotlib-overlay-plots-with-different-scales

    # b:blue
    # g: green
    # r: red
    # c: cyan
    # m: magenta
    # y: yellow
    # k: black
    # w: white

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

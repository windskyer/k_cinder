#
#
# =================================================================
# =================================================================


from __future__ import print_function
import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient.k2asample import timer
from paxes_cinder.k2aclient import client
import paxes_cinder.k2aclient.v1.cluster_manager as cluster_manager
import logging
import eventlet
from os.path import expanduser


def _chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def _setup_image_pool_from_list(ssp, image_pool_lu_udids):
    numfound = 0
    lus = []
    lu_found = []
    for lu in ssp.logical_units.logical_unit:
        if lu.unique_device_id in image_pool_lu_udids:
            lus.append(lu)
            lu_found.append(lu.unique_device_id)
            numfound += 1
    if numfound < len(image_pool_lu_udids):
        lu_notfound = [udid for udid in image_pool_lu_udids
                       if udid not in lu_found]
        raise ValueError("Images not found: >%s<" % (",".join(lu_notfound),))

    return (lus, ssp)


def _setup_image_pool(ssp, num_images, image_size, thin):
    """Setup pool of image LUs"""
    images = [("P2Z-IMAGE-%d" % (i,),
               image_size, thin) for i in range(num_images)]
    return ssp.update_append_lus(images)


def _teardown_lu_pool(ssp, lu_pool):
    lu_pool_ids = [lu.unique_device_id for lu in lu_pool if lu is not None]
    return ssp.update_del_lus(lu_pool_ids)


def _establish_steady_state(num_green_threads,
                            cs,
                            cluster,
                            ssp_id,
                            image_lu_pool,
                            num_of_requested_deploys,
                            perform_clone):

    def clone(results,
              ssp_id,
              source_lu_udid,
              dest_lu_unit_name,
              perform_clone):

        if perform_clone:
            print ("start clone: >%s<" % (dest_lu_unit_name,))
            ssp = cs.sharedstoragepool.get(ssp_id)
            (status, dest_lu, _) = \
                cluster.lu_linked_clone_of_lu(ssp,
                                              source_lu_udid,
                                              dest_lu_unit_name)

            if status != "COMPLETED_OK":
                x = "issue for clone: >%s<, status: >%s<"
                print (x % (dest_lu_unit_name, status,))

            results.append((status, dest_lu))
            print ("stop clone: >%s<" % (dest_lu_unit_name,))
        else:
            print ("start pretend clone: >%s<" % (dest_lu_unit_name,))
            # just pretend and create target LU
            ssp = cs.sharedstoragepool.get(ssp_id)
            # since we are pretending use a thin LU
            (dest_lu, _) = ssp.update_append_lu(dest_lu_unit_name, 1, True)
            results.append(("COMPLETED_OK", dest_lu))
            print ("stop pretend clone: >%s<" % (dest_lu_unit_name,))

    pool = eventlet.GreenPool(num_green_threads)

    images_provisioned = 0
    results = []
    spawn = True
    while spawn:
        # round robin through image pool
        for lu in image_lu_pool:
            source_lu_udid = lu.unique_device_id
            dest_lu_unit_name = "P2Z-GUEST-%d" % (images_provisioned,)
            ######
            try:
                pool.spawn_n(clone, results, ssp_id, source_lu_udid,
                             dest_lu_unit_name, perform_clone)
            except (SystemExit, KeyboardInterrupt):  # TODO are these correct?
                break
            ######
            images_provisioned += 1

            if images_provisioned == num_of_requested_deploys:
                spawn = False
                break

    # wait until all clones complete before returning
    pool.waitall()

    return results


def stress_ssp(cs,
               cluster_id,
               image_pool_lu_udids,
               image_size,
               num_deploys_at_steady_state,
               perform_clone,
               thin,
               num_green_threads,
               cleanup):

    cluster = cs.cluster.get(cluster_id)
    ssp_id = cluster.sharedstoragepool_id()
    # the ssp associated with the cluster
    ssp = cs.sharedstoragepool.get(ssp_id)

    # setup timer
    laps = timer(None)

    # get a pool of images

    if False:
        # old way, create empty ones
        num_images = 10
        (image_lu_pool, ssp) = _setup_image_pool(ssp,
                                                 num_images,
                                                 image_size,
                                                 thin)

    else:
        (image_lu_pool, ssp) = _setup_image_pool_from_list(ssp,
                                                           image_pool_lu_udids)

    print ("Elapsed time for image pool setup: >%f<" %
           (timer(laps),))

    # establish steady state
    results = \
        _establish_steady_state(num_green_threads,
                                cs,
                                cluster,
                                ssp_id,
                                image_lu_pool,
                                num_deploys_at_steady_state,
                                perform_clone)
    elapsed = timer(laps)
    print ("Reached steady state,"
           " deploys: >%d<,"
           " elapsed time: >%f<,"
           " thats >%s< per deploy" %
           (num_deploys_at_steady_state,
            elapsed,
            elapsed / float(num_deploys_at_steady_state)))

    # extract deployed image pool from results
    deployed_image_pool = [lu for (_, lu) in results]

    # operate at steady state TBD

    # don't cleanup unless requested
    if not cleanup:
        print ("Cleanup not requested ...")
        return

    #########
    # tear down
    ssp = cs.sharedstoragepool.get(ssp_id)

    # tear down deploys
    print ("Tear down deploys")
    if len(deployed_image_pool) != num_deploys_at_steady_state:
        print ("deployed_image_pool accounting mismatch"
               " len(deployed_image_pool): >%d<,"
               " num_deploys_at_steady_state: >%d<" %
               (len(deployed_image_pool),
                num_deploys_at_steady_state))

    chunksize = 10
    for chunk in _chunks(deployed_image_pool, chunksize):
        print ("    delete chunk of: >%d<" % (len(chunk),))
        ssp = _teardown_lu_pool(ssp, chunk)
    print ("Elapsed time for deployed pool teardown: >%f<" %
           (timer(laps),))

    # tear down images
    if False:
        if len(image_lu_pool) != num_images:
            print ("deployed_image_pool accounting mismatch"
                   " len(image_lu_pool): >%d<,"
                   " len(image_lu_pool): >%d<" %
                   (len(deployed_image_pool),
                    num_images))
        ssp = _teardown_lu_pool(ssp, image_lu_pool)
        print ("Elapsed time for image pool teardown: >%f<" %
               (timer(laps),))


if __name__ == '__main__':

    eventlet.monkey_patch()

    k2acfg = k2asample.getk2acfg()
#     k2asample.configure_logging(logging.getLevelName(k2acfg['loglevel']))
    k2asample.configure_logging(logging.DEBUG,
                                k2_loglevel=logging.WARNING,
                                logdir=expanduser("~"))

    cs = client.Client(k2acfg['api_version'],
                       k2acfg['k2_url'],
                       k2acfg['k2_username'],
                       k2acfg['k2_password'],
                       k2_auditmemento=k2acfg['k2_auditmemento'],
                       k2_certpath=k2acfg['k2_certpath'],
                       retries=3,  # k2acfg['retries']
                       timeout=120,  # k2acfg['timeout']
                       excdir="/tmp/stress_ssp")  # k2acfg['excdir']

    try:
        cluster_id = "a9dbe07f-30c4-3788-8f6f-659aa1d66502"
        image_size = 1
        num_images = 1
        num_deploys_at_steady_state = 100
        perform_clone = True
        thin = True
        num_green_threads = 5
        num_green_threads = 1
        num_green_threads = 10
        num_green_threads = 5
        num_green_threads = 3
        num_green_threads = 5
        cleanup = True

        image_pool_lu_udids = ["27a8df0d7101512b05beecdccf44a53fc0",
                               "2766d53702e6275c72713b00d04a9a735c",
                               "2701269b89bf13da8c7c11ecbebbc19d58",
                               "27027b3d88fa947ac259d4080307b12291",
                               "27355d6b7b80500be8b2532fb3bc7e97db",
                               "27dcae9430fc0f9b0e016e37716e5337d8",
                               "2733d22a5c410f033ce41e8b45918bfaba",
                               "2773a8c1d31b63d9f89b54412e309c45b2",
                               "274b66cb516c6fd1a7fa8b4bba68688171",
                               "27ee238dcb99fe1e4fb06a3d8b8e6de6f9"]

        stress_ssp(cs,
                   cluster_id,
                   image_pool_lu_udids,
                   image_size,
                   num_deploys_at_steady_state,
                   perform_clone,
                   thin,
                   num_green_threads,
                   cleanup)

#         print ("Job status ticks:")
#         jobstatus_ticks = cluster_manager._jobstatus_ticks
#         for k in sorted(jobstatus_ticks.keys()):
#             print ("    %s: %s" % (k.ljust(25),
#                                    str(jobstatus_ticks[k]).rjust(10)))
    except Exception as e:
        logging.exception(e)
#         print ("ERROR: %s" % e, file=sys.stderr)
#         print (traceback.format_exc())

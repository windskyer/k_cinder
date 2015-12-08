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


def _setup_image_pool(ssp, num_images, image_size, thin):
    """Setup pool of image LUs"""
    images = [("P2Z-IMAGE-%d" % (i,),
               image_size, thin) for i in range(num_images)]
    return ssp.update_append_lus(images)


def _teardown_lu_pool(ssp, lu_pool):
    lu_pool_ids = [lu.unique_device_id for lu in lu_pool if lu is not None]
    return ssp.update_del_lus(lu_pool_ids)


def _perform_clone_set(num_green_threads,
                       cs,
                       cluster,
                       ssp_id,
                       source_lu_pool,
                       num_of_requested_clones,
                       perform_clone,
                       prefix):

    def clone(results,
              ssp_id,
              source_lu_udid,
              dest_lu_unit_name,
              perform_clone):

        if perform_clone:
            print ("start clone: >%s<" % (dest_lu_unit_name,))
            ssp = cs.sharedstoragepool.get(ssp_id)
            (status, dest_lu, x, job_id) = \
                cluster.lu_linked_clone_of_lu_bp(ssp,
                                                 source_lu_udid,
                                                 dest_lu_unit_name)

            if status != "COMPLETED_OK":
                x = "issue for clone: >%s<, job: >%s<, status: >%s<"
                print (x % (dest_lu_unit_name, job_id, status,))

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
        for lu in source_lu_pool:
            source_lu_udid = lu.unique_device_id
            dest_lu_unit_name = "P2Z-%s-%d" % (prefix, images_provisioned,)
            ######
            try:
                pool.spawn_n(clone, results, ssp_id, source_lu_udid,
                             dest_lu_unit_name, perform_clone)
            except (SystemExit, KeyboardInterrupt):  # TODO are these correct?
                break
            ######
            images_provisioned += 1

            if images_provisioned == num_of_requested_clones:
                spawn = False
                break

    # wait until all clones complete before returning
    pool.waitall()

    return results


def stress_ssp(cs,
               cluster_id,
               num_images,
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
#     (source_lu, ssp) = ssp.update_append_lu("SOURCE-DM", 10, thin=True)
    (image_lu_pool, ssp) = _setup_image_pool(ssp, num_images, image_size, thin)

    print ("Elapsed time for image pool setup: >%f<" %
           (timer(laps),))

    ##################
    # establish steady state
    results = \
        _perform_clone_set(num_green_threads,
                           cs,
                           cluster,
                           ssp_id,
                           image_lu_pool,
                           num_deploys_at_steady_state,
                           perform_clone,
                           "GUESTA")
    elapsed = timer(laps)
    print ("Initial clone from image,"
           " deploys: >%d<,"
           " elapsed time: >%f<,"
           " thats >%s< per deploy" %
           (num_deploys_at_steady_state,
            elapsed,
            elapsed / float(num_deploys_at_steady_state)))

    # extract deployed image pool from results
    deployed_image_pool = [lu for (_, lu) in results]

    ##################
    # clone step
    results = \
        _perform_clone_set(num_green_threads,
                           cs,
                           cluster,
                           ssp_id,
                           deployed_image_pool,
                           num_deploys_at_steady_state,
                           perform_clone,
                           "GUESTB")

    elapsed = timer(laps)
    print ("Clone from clones,"
           " deploys: >%d<,"
           " elapsed time: >%f<,"
           " thats >%s< per deploy" %
           (num_deploys_at_steady_state,
            elapsed,
            elapsed / float(num_deploys_at_steady_state)))
    # extract deployed image pool from results
    cloned_image_pool = [lu for (_, lu) in results]

    ##################
    # don't cleanup unless requested
    if not cleanup:
        print ("Cleanup not requested ...")
        return

    ##################
    # tear down
    ssp = cs.sharedstoragepool.get(ssp_id)

    #########
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

    #########
    # tear down clones
    print ("Tear down clones")
    if len(cloned_image_pool) != num_deploys_at_steady_state:
        print ("cloned_image_pool accounting mismatch"
               " len(cloned_image_pool): >%d<,"
               " num_deploys_at_steady_state: >%d<" %
               (len(cloned_image_pool),
                num_deploys_at_steady_state))

    chunksize = 10
    for chunk in _chunks(cloned_image_pool, chunksize):
        print ("    delete chunk of: >%d<" % (len(chunk),))
        ssp = _teardown_lu_pool(ssp, chunk)
    print ("Elapsed time for cloned pool teardown: >%f<" %
           (timer(laps),))

    #########
    # tear down images
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
                       "9.114.181.235",  # k2acfg['k2_url'],
                       k2acfg['k2_username'],
                       "Passw0rd",  # k2acfg['k2_password'],
                       k2_auditmemento=k2acfg['k2_auditmemento'],
                       k2_certpath=k2acfg['k2_certpath'],
                       retries=3,  # k2acfg['retries']
                       timeout=120,  # k2acfg['timeout']
                       excdir="/tmp/stress_ssp")  # k2acfg['excdir']

    try:
#         cluster_id = "a9dbe07f-30c4-3788-8f6f-659aa1d66502"
        cluster_id = "d5ddc649-dc7c-31b1-8a1a-b8ab9bc98153"
        image_size = 1
        num_images = 5
        num_deploys_at_steady_state = 5
        perform_clone = True
        thin = True
        thin = False
        thin = True
        num_green_threads = 3
        cleanup = True

        stress_ssp(cs,
                   cluster_id,
                   num_images,
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

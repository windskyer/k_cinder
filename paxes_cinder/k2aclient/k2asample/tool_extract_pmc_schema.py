#
#
# =================================================================
# =================================================================

import os
import sys
import zipfile
import shutil

#PMC_DIR = "/devstate/WS_SSP/PMC.REST.SDK.BASE_7.7.8.0_20130731T1253"
#PMC_DIR = "/devstate/INSTALL-PMC/PMC.REST.SDK.BASE_7.7.8.0_20130725T1652"
#PMC_DIR = "/devstate/RSA802-PMAN/PMC.REST.SDK.BASE_7.7.8.0_20130806T2059"
#PMC_DIR = "/devstate/RSA802-PMAN/PMC.REST.SDK.BASE_7.7.8.0_20130825T0453"
#PMC_DIR = "/devstate/RSA802-PMAN/PMC.REST.SDK.BASE_7.7.8.0_20130919T1502"
#PMC_DIR = "/devstate/RSA802-PMAN/PMC.REST.SDK.BASE_7.7.8.0_20131007T0752"
#PMC_DIR = "/devstate/RSA802-PMAN/PMC.REST.SDK.BASE_7.7.8.0_20131010T1007"
#PMC_DIR = "/devstate/RSA802-PMAN/PMC.REST.SDK.BASE_7.7.8.0_20131023T1821"
#PMC_DIR = "/devstate/RSA802-PMAN/PMC.REST.SDK.BASE_7.7.8.0_20131027T1109"
# PMC_DIR = "/devstate/RSA802-PMAN/PMC.REST.SDK.BASE_8.8.1.0_20140203T0750"
PMC_DIR = "/devstate/RSA802-PMAN/PMC.REST.SDK.BASE_8.8.1.0_20140217T1257"


def _process_jars(tobeunzipped_dir, tobeunzipped, prjtobeunzipped):
    for unz in zip(tobeunzipped, prjtobeunzipped):
        (zfilename, prjs) = unz
#        print ">%s<" % (zfilename)
        zfilename = os.path.join(tobeunzipped_dir, zfilename)
        zfile = zipfile.ZipFile(zfilename, "r")
        for info in zfile.infolist():
            #
            fname = info.filename
            # check if directory
            if fname.endswith("/"):
                continue
#            fcontent = zfile.read(info.filename)
#            print fname

            # check if schema
            fname = fname.replace("/", os.sep)
            basename, extension = os.path.splitext(fname)
            extension = extension.lower()
            if extension != ".xsd":
                continue

            parts = basename.split(os.sep)
            assert parts[0] == "schema"
            parts = parts[1:]

            for prj in prjs:
                print prj, parts[0]
                if prj == parts[0]:
                    print "    %s" % (parts,)
#            spec=os.path.split(fname)
#            print spec
#    name, extension = os.path.splitext(os.path.basename(output_fn))
#            fname = fname.replace("/",os.sep)
#            # decompress each file's data
##            print ">%s<" % (fname)
#            fname = "".join((zroot,os.sep,zarch,os.sep,fname))
#            # decompressed
#            #filename = 'unzipped_' + fname
#            dname = os.path.dirname(fname)
#
#            print ">%s< >%s< >%s<" % (len(fname),dname,fname)
#            if len(fname) > 256:
#                _LOGGER.error("length of expanded filename:"
#                              " >%s<, equals: >%s<, exceeds max of 256,
#                              continuig",fname,len(fname))
#            else:
#                if not os.path.isdir(dname):
#                    os.makedirs(dname)
#                fout = open(fname, "wb")
#                fout.write(data)
#                fout.close()


def _dump_jars(tobeunzipped_dir, tobeunzipped):
    for zfilename in tobeunzipped:
#        print ">%s<" % (zfilename)
        zfilename = os.path.join(tobeunzipped_dir, zfilename)
        zfile = zipfile.ZipFile(zfilename, "r")
        for info in zfile.infolist():
            #
            fname = info.filename
            # check if directory
            if fname.endswith("/"):
                continue
#            fcontent = zfile.read(info.filename)
#            print fname

            # check if schema
            fname = fname.replace("/", os.sep)
            basename, extension = os.path.splitext(fname)
            extension = extension.lower()
            if extension != ".xsd":
                continue

            parts = basename.split(os.sep)
            assert parts[0] == "schema"
            parts = parts[1:]
            print "    %s" % (parts,)

#def process_all():
#    tobeunzipped = ["pmc.schema.web-7.7.8.0.jar",
#                    "pmc.schema.templates-7.7.8.0.j
#                    "pmc.schema.uom-7.7.8.0.jar"]
#    prjtobeunzipped = [["common","ietf","w3c","web"],["templates"],["uom"]]
#
##    _dump_jars(tobeunzipped_dir,tobeunzipped)
#    _process_jars(TOBEUNZIPPED_DIR, tobeunzipped, prjtobeunzipped)


def extract_ods_zip(tobeunzipped_dir, target_dir, fname, fext, partition):
    targetdir = os.path.join(target_dir, partition)
#    if os.path.exists(targetdir):
#        shutil.rmtree(targetdir)
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)

    zfilename = fname
    zfilename = os.path.join(tobeunzipped_dir, zfilename)
    zfile = zipfile.ZipFile(zfilename, "r")
    for info in zfile.infolist():
        #
        fname = info.filename
        # check if directory
        if fname.endswith("/"):
            continue

        # check if schema
        fname = fname.replace("/", os.sep)
        basename, extension = os.path.splitext(fname)
        extension = extension.lower()
        if extension != fext:
            continue

#        parts = basename.split(os.sep)
#        assert parts[0]=="schema"
#
#        parts = parts[1:]
#
#        ptb = os.path.join(*parts)
#        fpath = os.path.join(targetdir,ptb) + fext
##        print fpath

        parts = basename.split(os.sep)
        ptb = os.path.join(*parts)
        fpath = os.path.join(targetdir, ptb) + fext
#        print fpath
#        sys.exit()
        fcontent = zfile.read(info.filename)

        dpath = os.path.dirname(fpath)
        if not os.path.exists(dpath):
            os.makedirs(dpath)
        fout = open(fpath, "wb")
        fout.write(fcontent)
        fout.close()


def process_uom(tobeunzipped_dir, target_dir):
    targetdir = os.path.join(target_dir, "uom")
    if os.path.exists(targetdir):
        shutil.rmtree(targetdir)
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)

#     zfilename = "pmc.schema.uom-7.7.8.0.jar"
    zfilename = "pmc.schema.uom-8.8.1.0.jar"
    zfilename = os.path.join(tobeunzipped_dir, zfilename)
    zfile = zipfile.ZipFile(zfilename, "r")
    for info in zfile.infolist():
        #
        fname = info.filename
        # check if directory
        if fname.endswith("/"):
            continue

        # check if schema
        fname = fname.replace("/", os.sep)
        basename, extension = os.path.splitext(fname)
        extension = extension.lower()
        if extension != ".xsd":
            continue

        parts = basename.split(os.sep)
        assert parts[0] == "schema"

        parts = parts[1:]

        ptb = os.path.join(*parts)
        fpath = os.path.join(targetdir, ptb) + ".xsd"
#        print fpath

        fcontent = zfile.read(info.filename)
        sch = "platform:/resource/PMC_REST_Schema_UOM/tmp/build/schema"
        fcontent = fcontent.replace(sch, ".")

        dpath = os.path.dirname(fpath)
        if not os.path.exists(dpath):
            os.makedirs(dpath)
        fout = open(fpath, "wb")
        fout.write(fcontent)
        fout.close()


def process_templates(tobeunzipped_dir, target_dir):
    targetdir = os.path.join(target_dir, "templates")
    if os.path.exists(targetdir):
        shutil.rmtree(targetdir)
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)

#     zfilename = "pmc.schema.templates-7.7.8.0.jar"
    zfilename = "pmc.schema.templates-8.8.1.0.jar"
    zfilename = os.path.join(tobeunzipped_dir, zfilename)
    zfile = zipfile.ZipFile(zfilename, "r")
    for info in zfile.infolist():
        #
        fname = info.filename
        # check if directory
        if fname.endswith("/"):
            continue

        # check if schema
        fname = fname.replace("/", os.sep)
        basename, extension = os.path.splitext(fname)
        extension = extension.lower()
        if extension != ".xsd":
            continue

        parts = basename.split(os.sep)
        assert parts[0] == "schema"

        parts = parts[1:]

        ptb = os.path.join(*parts)
        fpath = os.path.join(targetdir, ptb) + ".xsd"
#        print fpath

        fcontent = zfile.read(info.filename)

        dpath = os.path.dirname(fpath)
        if not os.path.exists(dpath):
            os.makedirs(dpath)
        fout = open(fpath, "wb")
        fout.write(fcontent)
        fout.close()


def process_web(tobeunzipped_dir, target_dir):
    targetdir = os.path.join(target_dir, "web")
    if os.path.exists(targetdir):
        shutil.rmtree(targetdir)
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)

#    zfilename = "pmc.schema.web-7.7.8.0.jar"
    zfilename = "pmc.schema.web-8.8.1.0.jar"
    zfilename = os.path.join(tobeunzipped_dir, zfilename)
    zfile = zipfile.ZipFile(zfilename, "r")
    for info in zfile.infolist():
        #
        fname = info.filename
        # check if directory
        if fname.endswith("/"):
            continue

        # check if schema
        fname = fname.replace("/", os.sep)
        basename, extension = os.path.splitext(fname)
        extension = extension.lower()
        if extension != ".xsd":
            continue

        parts = basename.split(os.sep)
        assert parts[0] == "schema"

        parts = parts[1:]

        ptb = os.path.join(*parts)
        fpath = os.path.join(targetdir, ptb) + ".xsd"
#        print fpath

        fcontent = zfile.read(info.filename)

        dpath = os.path.dirname(fpath)
        if not os.path.exists(dpath):
            os.makedirs(dpath)
        fout = open(fpath, "wb")
        fout.write(fcontent)
        fout.close()


def main():
    """
    Map PMC SDK to standard maven format
    """

    tobeunzipped_dir = os.path.join(PMC_DIR, "lib/rest")
    target_dir = os.path.join(PMC_DIR, "target")

    process_uom(tobeunzipped_dir, target_dir)
    process_templates(tobeunzipped_dir, target_dir)
    process_web(tobeunzipped_dir, target_dir)

    # ods

#     extract_ods_zip(tobeunzipped_dir, target_dir,
#                     "pmc.schema.uom.src-7.7.8.0.jar", ".ods", "uom")
#     extract_ods_zip(tobeunzipped_dir, target_dir,
#                     "pmc.schema.templates-7.7.8.0.jar", ".ods", "templates")
#     extract_ods_zip(tobeunzipped_dir, target_dir,
#                     "pmc.schema.web.src-7.7.8.0.jar", ".ods", "web")
    extract_ods_zip(tobeunzipped_dir, target_dir,
                    "pmc.schema.uom.src-8.8.1.0.jar", ".ods", "uom")
    extract_ods_zip(tobeunzipped_dir, target_dir,
                    "pmc.schema.templates-8.8.1.0.jar", ".ods", "templates")
    extract_ods_zip(tobeunzipped_dir, target_dir,
                    "pmc.schema.web.src-8.8.1.0.jar", ".ods", "web")

if __name__ == '__main__':
    sys.exit(main())

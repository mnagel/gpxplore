#!/usr/bin/env python
import argparse
import glob

from data_explorer import app
from gpxplore.testlets import *

APPTITLE = 'GPXplore - GPX File Browser'


def folder_to_gpx_files(path):
    res = []
    for i, file in enumerate(glob.glob(path + "/*.gpx")):
        print("globbed %s" % file)
        res.append(GpxFile(file))
        # if i > 1:
        #     break
    return res


def main(args):
    gpxes = folder_to_gpx_files(args.directory)

    testlets = [
        NameTestlet(),
        MapTestlet(),
        BigMapTestlet(),
        GpsPruneTestlet(),
        HeigthmapTestlet("Point_Index_Flat", ["Point_Elevation"]),
        Length2dTestlet(),
        Length3dTestlet(),
        MovingTimeTestlet(),
        StoppedTimeTestlet(),
        MovingDistanceTestlet(),
        StoppedDistanceTestlet(),
        MaxSpeedTestlet(),
        UphillTestlet(),
        DownhillTestlet(),
        StartedTestlet(),
        EndedTestlet(),
        CountTestlet(),
    ]

    app.execute(
        title=APPTITLE,
        entry_list=gpxes,
        testlet_list=testlets,
        icon=os.path.join(os.path.dirname(__file__), '../icons/open-iconic-master/svg/globe.svg'),
        verbose=args.verbose
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=APPTITLE)
    parser.add_argument(
        '--directory',
        type=str,
        help='path to solutions to be explored',
        required=True
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='log everything'
    )

    tmp = parser.parse_args()
    main(tmp)

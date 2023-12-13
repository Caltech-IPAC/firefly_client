#!/usr/bin/env python

import csv
from glob import glob
import os
import tempfile

import firefly_client


def filetable_to_firefly(ffclient, topdir, pattern, recursive=True):
    """Upload table of files matching a pattern to a FireflyClient

    Parameters:
    -----------
    ffclient: firefly_client.FireflyClient
        Instance of FireflyClient connected to a Firefly server

    topdir: "str"
        pathname for directory to search

    pattern: "str"
        filename pattern to search for, e.g. "*.fits"

    recursive: `bool`
        Search all subdirectories recursively (default=True)

    Returns:
    --------
    tbl_val: "str"
        Descriptor of table that was uploaded to the Firefly server

    metadict: `dict`
        Dictionary of metadata items

    """
    filelist = sorted(glob(topdir + "/**/" + pattern, recursive=recursive))
    metadict = {"datasource": "path"}
    with tempfile.NamedTemporaryFile(mode="w+t", delete=False, suffix=".csv") as fd:
        csv_writer = csv.writer(fd)
        csv_writer.writerow(["number", "name", "path"])
        for i, path in enumerate(filelist):
            # Docker Firefly allows uploads from /external
            csv_writer.writerow([i,
                                 os.path.basename(path),
                                 "file:///external" + path])

    tbl_val = ffclient.upload_file(fd.name)
    os.remove(fd.name)
    return (tbl_val, metadict)


# Sample application
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="""
        Display a table of files in a Firefly window
        """
    )
    parser.add_argument("topdir", help="top-level directory to search")
    parser.add_argument("pattern", help="filename pattern for search")
    parser.add_argument(
        "--norecursion", help="do not recursively search topdir", action="store_true"
    )
    parser.add_argument(
        "--firefly_url", help="URL for Firefly server", default=os.getenv("FIREFLY_URL")
    )
    parser.add_argument("--channel", help="channel name for websocket", default=None)
    parser.add_argument(
        "--printurl",
        help="print browser url instead of" + " attempting to launch browser",
        action="store_true",
    )

    args = parser.parse_args()
    topdir = args.topdir
    pattern = args.pattern
    firefly_url = args.firefly_url
    channel = args.channel
    printurl = args.printurl
    launch_browser = True
    if printurl:
        launch_browser = False
    recursion = not args.norecursion

    fc = firefly_client.FireflyClient.make_client(
        url=firefly_url,
        channel_override=channel,
        html_file="slate.html",
        launch_browser=launch_browser,
    )
    if printurl:
        print("Firefly URL is {}".format(fc.get_firefly_url()))

    print("Searching for files...", end="")
    tbl_val, metainfo = filetable_to_firefly(fc, topdir, pattern, recursive=recursion)
    print("done.")

    if printurl:
        input("Press Enter after your browser is open to the Firefly URL...")

    r = fc.add_cell(0, 0, 1, 2, "tables", "main")
    fc.show_table(tbl_val, meta=metainfo)
    r = fc.add_cell(0, 1, 1, 2, "tableImageMeta", "image-meta")
    fc.show_image_metadata(viewer_id=r["cell_id"])


if __name__ == "__main__":
    main()

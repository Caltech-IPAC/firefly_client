#!/usr/bin/env python

import csv
from glob import glob
import os
import tempfile

import firefly_client


def filetable_to_firefly(
    ffclient, topdir, pattern, path_prefix="", recursive=True, sort=False
):
    """Upload table of files matching a pattern to a FireflyClient

    Parameters:
    -----------
    ffclient: firefly_client.FireflyClient
        Instance of FireflyClient connected to a Firefly server

    topdir: "str"
        pathname for directory to search

    pattern: "str"
        filename pattern to search for, e.g. "*.fits"

    path_prefix: "str"
        string to prepend to each file path after "file://"
        for example, specify "/external" for Firefly-in-Docker
        (default="")

    recursive: `bool`
        Search all subdirectories recursively (default=True)

    sort: `bool`
        Sort the file paths (default=False)

    Returns:
    --------
    tbl_val: "str"
        Descriptor of table that was uploaded to the Firefly server

    metadict: `dict`
        Dictionary of metadata items

    """
    filelist = glob(topdir + "/**/" + pattern, recursive=recursive)
    if sort:
        filelist = sorted(filelist)
    metadict = {"datasource": "path"}
    with tempfile.NamedTemporaryFile(mode="w+t", delete=False, suffix=".csv") as fd:
        csv_writer = csv.writer(fd)
        csv_writer.writerow(["number", "name", "path"])
        for i, path in enumerate(filelist):
            # Docker Firefly allows uploads from /external
            csv_writer.writerow(
                [i, os.path.basename(path), "file://" + path_prefix + path]
            )

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
        "--path_prefix",
        help="string to prepend to file paths\n"
        + "e.g. specify '/external' for Firefly-in-Docker",
        default="",
    )
    parser.add_argument(
        "--norecursion", help="do not recursively search topdir", action="store_true"
    )
    parser.add_argument("--sort", help="sort the file paths", action="store_true")
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
    launch_browser = False if printurl else True
    recursion = not args.norecursion
    sort = args.sort
    path_prefix = args.path_prefix

    fc = firefly_client.FireflyClient.make_client(
        url=firefly_url,
        channel_override=channel,
        html_file="slate.html",
        launch_browser=launch_browser,
    )
    if printurl:
        print("Firefly URL is {}".format(fc.get_firefly_url()))

    print("Searching for files...", end="")
    tbl_val, metainfo = filetable_to_firefly(
        fc, topdir, pattern, path_prefix=path_prefix, recursive=recursion, sort=sort
    )
    print("done.")

    if printurl:
        input("Press Enter after you have opened the Firefly URL printed above...")

    r = fc.add_cell(0, 0, 1, 2, "tables", "main")
    fc.show_table(tbl_val, meta=metainfo)
    r = fc.add_cell(0, 1, 1, 2, "tableImageMeta", "image-meta")
    fc.show_image_metadata(viewer_id=r["cell_id"])


if __name__ == "__main__":
    main()

"""
The firefly CLI.
"""

###############################################################################
# The following code leaves the the convention of using NumpyDoc long         #
# docstrings for the module and classes, and uses the NumpyDoc short          #
# docstrings. These docstrings are also referred to as PandaDoc docstrings.   #
# as they are used in the Pandas library.                                     #
#                                                                             #
# The departure from the convention is intentional, as `click` and `pydantic` #
# only support short docstrings for automatically parsing help text.          #
# Unfortinately, NumpyDoc short docstrings can only support either typing     #
# comments or help text, but not both.                                        #
###############################################################################

# - [ ] Support image displays (FITS and HiPS)
#       - [ ] Support pixel-flag (a/k/a "mask") overlays when the pixel flags are in a separate file from the background image
# - [ ] Support tabular data displays on their own as well as via overlays on images
#       - [ ] Support, at a minimum, the specification of the columns to be used in a default plot for a table
# - [x] Support sending files to Firefly for opening in the "file explorer"
# - [ ] Support data access from:
#       - [x] Files in a Posix filesystem accessible on the host on which the command is run
#       - [x] Data from a Unix pipeline (e.g., "make-data | firefly display --table")
#       - [ ] URLs provided on the command line, including s3: URLs once Firefly itself supports them
# - [ ] Support the use of multiple Firefly servers that a user may have access to
#       - [ ] Universally accessible ones like IRSA Viewer and the projected "Firefly public server"
#       - [ ] Access-controlled ones such as in RSP-like Science Platforms
#       - [ ] Locally-run Firefly servers, e.g., in a Docker container on a laptop
# - [ ] Support sending data to the JupyterLab Firefly extension as well as to dedicated Firefly browser sessions
# - [x] Avoid the necessity for users to repeatedly tangle with explicit URLs for the Firefly server
# - [x] Provide a "session" experience that supports the Firefly "channel" idea
# - [ ] Support the ability to connect to an existing  Firefly browser session in addition to supporting launching a new one
# - [x] Support the configuration of options via files in the user's Posix home space
# - [x] Be easily installable from well-known open-source software repositories
# - [x] Support (as a "version 2"-level feature) optimization of access to the specified file(s) if they are also directly accessible on the Firefly server
#         E.g., if the same NSF file system is mounted on the host on which the command is executed and on the Firefly server
# - [ ] Support (as a "version 3"-level feature) a basic sort of "browsing of a directory full of images" capability
#         May require the use of some sort of auxiliary plug-in to handle metadata extraction

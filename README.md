# firefly_client

Python API for Firefly, IPAC's Advanced Astronomy Web UI Framework

## Usage

The client must be connected to a Firefly server. The Firefly
repository is located at http://github.com/Caltech-IPAC/firefly.
Standalone Firefly servers may be obtained from
[this Dockerhub repository](https://hub.docker.com/r/ipac/firefly/).

For detailed explanation on the usage, see [the online documentation](https://firefly-client.lsst.io),
or [the documentation source file](doc/index.rst). Following is a very simple example:

```
from firefly_client import FireflyClient
fc = FireflyClient.make_client()  # can also explictly pass url of a firefly server; default is http://localhost:8080/firefly
```

A FITS image may be uploaded and displayed:

```
fval = fc.upload_file('image.fits')
fc.show_fits(fval, 'myimage')
```

For more examples, check notebooks & python files in the [examples](examples/) and [test](test/) directories.

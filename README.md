# firefly_client

Python API for Firefly, IPAC's Advanced Astronomy Web UI Framework

## Usage

The client must be connected to a Firefly server. The Firefly
repository is located at http://github.com/Caltech-IPAC/firefly.
Standalone Firefly servers may be obtained from
[this Dockerhub repository](https://hub.docker.com/r/ipac/firefly/).

For examples, see [the online documentation](https://firefly-client.lsst.io),
or [the documentation source file](doc/index.rst).


```
from firefly_client import FireflyClient
fc = FireflyClient('http://localhost:8080')
```

A FITS image may be uploaded and displayed.

```
fval = fc.upload_file('image.fits')
fc.show_fits(fval, 'myimage')
```

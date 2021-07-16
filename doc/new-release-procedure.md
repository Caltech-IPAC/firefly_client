## How to create a firefly_client release

### Procedure
1. To push a new release you must be a maintainer in pypi ([see pypi below](#pypi))
1. Bump version in setup.py  (this step is might be done in the PR)
1. Clean out old distribution 
   - `rm dist/*`
1. Create the distribution
   - Create a tar/gzip file with the correct directory structure
      - `python setup.py sdist` 
   - Create the wheel file
      - `python setup.py bdist_wheel`
   - check it: `ls dist` should show two files a `.tar.gz` file and a `.whl` file
1. _Optional_ - At this point you could do an optional test installation ([see below](#optional-test-installation))
1. Upload to PYPI  
   - `twine upload  dist/*`
1. Tag
   -  `git tag -a 2.5.0`  (replace version number with the current version from setup.py)
1. If any files were edited (i.e `setup.py`) 
   - `git commit - a`
   - `git push origin master`
1. Push tags
   - `git push --tags`
1. After this you can install 
   - `pip install firefly_client`
1. Make is release with github, using the tag above
   - https://github.com/Caltech-IPAC/firefly_client/releases

### PYPI 

- https://pypi.org/project/firefly-client/
- Currently two maintainers
- Testing site: https://test.pypi.org/project/firefly-client/

### Optional Test installation

1. To create a test release you must be a mainainer on testpypi
1. Create the distribution (see above)
1. `twine upload --repository-url https://test.pypi.org/legacy/ dist/*`
1. `pip uninstall firefly_client`
1. `pip install --verbose --index-url https://testpypi.python.org/pypi firefly_client`

### Conda and conda-forge

Anytime the version tag is updated conda-forge it set up to do a pull and add `firefly_client` to its distribution.

See the following sites:
 - https://github.com/conda-forge/firefly-client-feedstock/
 - https://anaconda.org/conda-forge/firefly-client
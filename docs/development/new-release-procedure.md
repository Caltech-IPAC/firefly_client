# Making a release

## Procedure
1. To push a new release you must be a maintainer in pypi ([see pypi below](#pypi))
2. Bump version in setup.py  (this step is might be done in the PR)
3. Clean out old distribution 
   - `rm dist/*`
4. Create the distribution
   - Create a tar/gzip file with the correct directory structure
      ```bash
      python setup.py sdist
      ```
   - Create the wheel file
      ```bash
      pip install --upgrade wheel
      python setup.py bdist_wheel
      ```
   - check it: `ls dist` should show two files a `.tar.gz` file and a `.whl` file
5. _Optional_ - At this point you could do an optional test installation ([see below](#optional-test-installation))
6. Upload to PYPI  
      ```bash
      pip install --upgrade twine
      twine upload dist/*
      ```
7. If any files were edited (i.e `setup.py`) 
   - `git commit - a`
   - `git push origin master`
8. Tag
   -  `git tag -a 2.5.0`  (replace version number with the current version from setup.py)
9. Push tags
   - `git push --tags`
10. After this you can install 
   - `pip install firefly_client`
11. Make is release with github, using the tag above
   - https://github.com/Caltech-IPAC/firefly_client/releases

## PYPI 

- https://pypi.org/project/firefly-client/
- Currently two maintainers
- Testing site: https://test.pypi.org/project/firefly-client/

## Optional Test installation

1. To create a test release you must be a mainainer on testpypi
2. Create the distribution (see above)
3. `twine upload --repository-url https://test.pypi.org/legacy/ dist/*`
4. `pip uninstall firefly_client`
5. `pip install --verbose --index-url https://testpypi.python.org/pypi firefly_client`

## Conda and conda-forge

Anytime the version tag is updated conda-forge it set up to do a pull and add `firefly_client` to its distribution.

See the following sites:
 - https://github.com/conda-forge/firefly-client-feedstock/
 - https://anaconda.org/conda-forge/firefly-client
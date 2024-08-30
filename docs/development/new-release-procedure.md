# Making a release

## Procedure
1. To push a new release you must be a maintainer in pypi ([see pypi below](#pypi))
2. Bump version in pyproject.toml  (this step might be done in the PR)
3. Clean out old distribution 
   - `rm dist/*`
4. Create the distribution
   - Create a tar/gzip file (unbuilt source distibution) and a wheel file 
   (built package) together using the `build` package:
      ```bash
      pip install --upgrade build
      python -m build
      ```
   - Check it: `ls dist` should show two files a `.tar.gz` file and a `.whl` file
   and both file names should contain correct version number that you intend to
   release.
5. _Optional_ - At this point you could do an optional test installation ([see below](#optional-test-installation))
6. Upload to PYPI  
   1. _One-time-only auth setup:_ Login to pypi and then in your account settings, go to the API tokens section and select "Add API token". Give it any name and select scope to project:firefly-client and create token. To save this token for later uses, make sure to create a `$HOME/.pypirc` file (or update it if you already have it) with the following:
      ```ini
      [distutils]
      index-servers =
         firefly-client #note the values here are newline-separated 

      [firefly-client]
      repository = https://upload.pypi.org/legacy/
      username = __token__
      password = pypi-token-you-created
      ```

   2. Upload dist to pypi using twine (with the auth setup in previous step)
      ```bash
      pip install --upgrade twine
      twine upload dist/* --repository firefly-client
      ```
7. If any files were edited (i.e `pyproject.toml`) 
   - `git commit - a`
   - `git push origin master`
8. Tag
   -  `git tag -a 2.5.0`  (replace version number with the current version from pyproject.toml)
9. Push tags
   - `git push --tags`
10. After this you can install 
   - `pip install firefly_client`
11. Make a release with github, using the tag above
   - https://github.com/Caltech-IPAC/firefly_client/releases

## PYPI 

- Must be maintainer at https://pypi.org/project/firefly-client/
- Testing site: https://test.pypi.org/project/firefly-client/

## Optional Test installation

1. To create a test release you must be a mainainer on testpypi
2. Create the distribution (see above)
3. `twine upload --repository-url https://test.pypi.org/legacy/ dist/*`
4. `pip uninstall firefly_client`
5. `pip install --verbose --index-url https://testpypi.python.org/pypi firefly_client`

## Conda and conda-forge

Anytime the version tag is updated, conda-forge is set up to do a pull and add `firefly_client` to its distribution.

See the following sites:
 - https://github.com/conda-forge/firefly-client-feedstock/
 - https://anaconda.org/conda-forge/firefly-client
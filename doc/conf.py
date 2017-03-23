#!/usr/bin/env python
"""Sphinx configurations to build package documentation."""

from documenteer.sphinxconfig.stackconf import build_package_configs

import firefly_client

_g = globals()
_g.update(build_package_configs(
    project_name='firefly_client',
    copyright='2016-2017 California Institute of Technology',
    version=firefly_client.__version__,
    doxygen_xml_dirname=None))

# intersphinx_mapping['astropy'] = ('http://docs.astropy.org/en/stable', None)

# DEBUG only
automodsumm_writereprocessed = False

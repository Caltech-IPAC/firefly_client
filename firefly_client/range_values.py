import math


class RangeValues:
    # for serializing the RangeValues object
    STRETCH_TYPE_DICT = {'percent': 88, 'minmax': 89, 'absolute': 90,  'zscale': 91, 'sigma': 92}
    """Definition of stretch type (`dict`)."""
    INVERSE_STRETCH_TYPE = {v: k for k, v in STRETCH_TYPE_DICT.items()}

    STRETCH_ALGORITHM_DICT = {'linear': 44, 'log': 45, 'loglog': 46, 'equal': 47, 'squared': 48, 'sqrt': 49,
                              'asinh': 50, 'powerlaw_gamma': 51}
    """Definition of stretch algorithm (`dict`)."""
    INVERSE_STRETCH_ALGORITHM = {v: k for k, v in STRETCH_ALGORITHM_DICT.items()}

    @classmethod
    def create_rv(cls, stretch_type, lower_value, upper_value, algorithm,
                  zscale_contrast=25, zscale_samples=600, zscale_samples_perline=120,
                  asinh_q_value=None, gamma_value=2.0,
                  rgb_preserve_hue=0, asinh_stretch=None, scaling_k=1.0):
        retval = None
        st = stretch_type.lower()
        a = algorithm.lower()

        # when q is NaN (case-sensitive), Firefly will calculate q using range
        if asinh_q_value is None or math.isnan(asinh_q_value):
            qstr = 'NaN'
        elif math.isinf(asinh_q_value):
            raise ValueError('invalid asinh_q_value: %f' % asinh_q_value)
        else:
            qstr = '%f' % asinh_q_value

        # when asinh_stretch is NaN (case-sensitive), Firefly will calculate asinh_stretch
        # for hue-preserving rgb using z-scale range of intensity
        if asinh_stretch is None or math.isnan(asinh_stretch):
            asinh_stretch_str = 'NaN'
        elif math.isinf(asinh_stretch) or asinh_stretch < 0:
            raise ValueError('invalid asinh_stretch for hue-preserving rgb: %f' % asinh_stretch)
        else:
            asinh_stretch_str = '%f' % asinh_stretch

        if rgb_preserve_hue is None:
            rgb_preserve_hue = 0

        if st in cls.STRETCH_TYPE_DICT and a in cls.STRETCH_ALGORITHM_DICT:
            retval = '%d,%f,%d,%f,%s,%f,%d,%d,%d,%d,%d,%s,%f' % \
                     (cls.STRETCH_TYPE_DICT[st], lower_value,
                      cls.STRETCH_TYPE_DICT[st], upper_value,
                      qstr, gamma_value,
                      cls.STRETCH_ALGORITHM_DICT[a],
                      zscale_contrast, zscale_samples, zscale_samples_perline,
                      rgb_preserve_hue, asinh_stretch_str, scaling_k)
        return retval

    @classmethod
    def create_rv_by_stretch_type(cls, algorithm, stretch_type, **additional_params):
        a = algorithm.lower() if algorithm else 'linear'
        st = stretch_type.lower() if stretch_type else 'percent'
        if st == 'zscale':
            return cls.create_rv_zscale(a, **additional_params)
        elif st in ['minmax', 'maxmin']:  # 'maxmin' retained for backwards compatibility
            return cls.create_rv_standard(a, 'percent', lower_value=0, upper_value=100, **additional_params)
        else:
            return cls.create_rv_standard(a, stretch_type, **additional_params)

    @classmethod
    def create_rv_standard(cls, algorithm, stretch_type='Percent', lower_value=1, upper_value=99, **additional_params):
        """
        Create range values for non-zscale cases.

        Parameters
        -----------
        algorithm : {'Linear', 'Log', 'LogLog', 'Equal', 'Squared', 'Sqrt'}
            Stretch algorithm.
        stretch_type : {'Percent', 'Absolute', 'Sigma'}
            Stretch type.
        lower_value: `int` or  `float`
            Lower end of stretch.
        upper_value: `int` or  `float`
            Upper end of stretch

        **additional_params : optional keyword arguments
            Algorithm specific parameters for changing the stretch. The options are shown as below:

            **asinh_q_value** : `float`, optional
                The asinh softening parameter for Asinh stretch.
                Use Q=0 for linear stretch, increase Q to make brighter features visible.
                When not specified, Q is calculated by Firefly to use full color range.
            **gamma_value**
                The gamma value for Power Law Gamma stretch

        Returns
        -------
        out : `str`
            a serialized range values string
        """
        retval = cls.create_rv(stretch_type, lower_value, upper_value, algorithm, **additional_params)
        if not retval:
            t = stretch_type if stretch_type.lower() in cls.STRETCH_TYPE_DICT else 'percent'
            a = algorithm if algorithm.lower() in cls.STRETCH_ALGORITHM_DICT else 'linear'
            retval = cls.create_rv(t, 1, 99, a, **additional_params)
        return retval

    @classmethod
    def create_rv_zscale(cls, algorithm, zscale_contrast=25,
                         zscale_samples=600, zscale_samples_perline=120, **additional_params):
        """
        Create range values for zscale case.

        Parameters
        ----------
        algorithm: {'Linear', 'Log', 'LogLog', 'Equal', 'Squared', 'Sqrt'}
            Stretch algorithm.
        zscale_contrast: `int`
            Zscale contrast.
        zscale_samples: `int`
            Zscale samples
        zscale_samples_perline: `int`
            Zscale samples per line

        **additional_params : optional keyword arguments
            Algorithm specific parameters for changing the stretch. The options are shown as below:

            **asinh_q_value** : `float`, optional
                The asinh softening parameter for Asinh stretch.
                Use Q=0 for linear stretch, increase Q to make brighter features visible.
                When not specified, Q is calculated by Firefly to use full color range.
            **gamma_value**
                The gamma value for Power Law Gamma stretch

        Returns
        -------
        out : `str`
            a serialized range values string
        """
        retval = RangeValues.create_rv('zscale', 1, 1, algorithm, zscale_contrast, zscale_samples,
                                       zscale_samples_perline, **additional_params)
        if not retval:
            a = algorithm if algorithm.lower() in cls.STRETCH_ALGORITHM_DICT else 'linear'
            retval = cls.create_rv('zscale', 1, 2, a, 25, 600, 120, **additional_params)
        return retval

    @classmethod
    def parse_rvstring(cls, rvstring):
        """parse a Firefly RangeValues string into a dictionary

        Parameters
        ----------
        rvstring : `str`
            RangeValues string as returned by the set_stretch method.

        Returns
        -------
        outdict : `dict`
            dictionary of the inputs
        """
        vals = rvstring.split(',')
        assert 10 <= len(vals) <= 13
        outdict = dict(lower_type=cls.INVERSE_STRETCH_TYPE[int(vals[0])],
                       lower_value=float(vals[1]),
                       upper_type=cls.INVERSE_STRETCH_TYPE[int(vals[2])],
                       upper_value=float(vals[3]),
                       asinh_q_value=float(vals[4]),
                       gamma_value=float(vals[5]),
                       algorithm=cls.INVERSE_STRETCH_ALGORITHM[int(vals[6])],
                       zscale_contrast=int(vals[7]),
                       zscale_samples=int(vals[8]),
                       zscale_samples_perline=int(vals[9]))
        if len(vals) > 10:
            outdict['rgb_preserve_hue'] = int(vals[10])
            outdict['asinh_stretch'] = float(vals[11])
            outdict['scaling_k'] = float(vals[12])
        return outdict

    @classmethod
    def rvstring_from_dict(cls, rvdict):
        """create an rvstring from a dictionary

        Parameters
        ----------
        rvdict : `dict`
            Dictionary with the same keys as those returned by parse_rvstring

        Returns
        -------
        rvstring : `str`
            RangeValues string that can be passed to the show_fits methods
        """

        argnames = ['lower_value', 'upper_value', 'upper_value', 'algorithm',
                    'zscale_contrast', 'zscale_samples', 'zscale_samples_perline',
                    'asinh_q_value', 'gamma_value', 'rgb_preserve_hue', 'asinh_stretch', 'scaling_k']
        kw = dict((k, rvdict[k]) for k in argnames)
        return RangeValues.create_rv(stretch_type=rvdict['lower_type'], **kw)

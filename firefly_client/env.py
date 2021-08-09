import base64
import os
import uuid
import datetime

try:
    from .fc_utils import str_2_bool
except ImportError:
    from fc_utils import str_2_bool

# environment variable list
ENV_FF_LAB_EXT = 'fireflyLabExtension'
ENV_FF_CHANNEL_LAB = 'fireflyChannelLab'
ENV_FF_URL_LAB = 'fireflyURLLab'
ENV_FF_URL = 'FIREFLY_URL'
ENV_FF_CHANNEL = 'FIREFLY_CHANNEL'
ENV_FF_HTML = 'FIREFLY_HTML'
ENV_USER = 'USER'

EXT_INCORRECT = 'jupyter_firefly_extensions appears to be installed incorrectly.'
SUGGESTION = 'fix jupyter_firefly_extensions in Jupyter Lab or use FireflyClient.make_client()'
COULD_NO_FIND_ENV = 'Could not find environment variable '


class Env:
    # all os environment access here
    firefly_lab_extension = str_2_bool(os.environ.get(ENV_FF_LAB_EXT, ''))
    firefly_channel_lab = os.environ.get(ENV_FF_CHANNEL_LAB)
    firefly_url_lab = os.environ.get(ENV_FF_URL_LAB)
    firefly_url = os.environ.get(ENV_FF_URL)
    firefly_channel_from_env = os.environ.get(ENV_FF_CHANNEL)
    firefly_html = os.environ.get(ENV_FF_HTML, 'slate.html')
    user = os.environ.get(ENV_USER, '')

    @classmethod
    def validate_lab_client(cls, generate_lab_ext_channel):
        """ return the url and channel or raise an Error """
        not cls.lab_ext_valid() and cls.raise_invalid_lab_error()
        return cls.firefly_url_lab, cls.resolve_lab_channel(generate_lab_ext_channel)

    @classmethod
    def raise_invalid_lab_error(cls):
        if not cls.firefly_lab_extension:
            raise RuntimeError('FireflyClient.makeLabClient can only be used in the Jupyterlab environment. ' +
                               SUGGESTION)
        if not cls.firefly_channel_lab:
            raise RuntimeError(COULD_NO_FIND_ENV + ENV_FF_CHANNEL_LAB + '. ' + EXT_INCORRECT + ' ' + SUGGESTION)
        if not cls.firefly_url_lab:
            raise RuntimeError(COULD_NO_FIND_ENV + ENV_FF_URL_LAB_LAB + '. ' + EXT_INCORRECT + ' ' + SUGGESTION)

    @classmethod
    def show_start_browser_tab_msg(cls, url):
        print('Firefly URL is {}'.format(url))
        print('To start a new tab you you will have to disable popup blocking for this site.')
        print('     Chrome: look at the right side of the address bar')
        print('     Firefox: a preference bar appears at the top')
        print('     Safari: shows an animation to follow on left side bar')

    @classmethod
    def lab_ext_valid(cls): return bool(cls.firefly_lab_extension and cls.firefly_channel_lab and cls.firefly_url_lab)

    @classmethod
    def resolve_client_channel(cls, in_channel):
        if in_channel is not None:
            return in_channel
        elif cls.firefly_channel_from_env:
            return cls.firefly_channel_from_env
        else:
            start_str = cls.user + datetime.datetime.today().strftime('%Y-%m-%d')
            return base64.urlsafe_b64encode(start_str.encode()).decode().replace('=', '')

    @classmethod
    def resolve_lab_channel(cls, generate_lab_ext_channel):
        if cls.lab_ext_valid():
            if generate_lab_ext_channel:
                return cls.firefly_channel_lab + '__lab-external__viewer'
            else:
                return cls.firefly_channel_lab
        else:
            return str(uuid.uuid1())

    @classmethod
    def find_default_firefly_url(cls):
        if cls.firefly_lab_extension:
            return cls.firefly_url_lab
        elif cls.firefly_url:
            return cls.firefly_url
        else:
            return 'http://localhost:8080/firefly'

    @classmethod
    def find_default_firefly_html(cls): return cls.firefly_html

    @classmethod
    def failed_net_message(cls, location, status_code=-1):
        s_str = 'with status: %s' % status_code if (status_code > -1) else ''
        check = 'You may want to check the URL with your web browser.\n'
        err_message = 'Connection fail to URL %s %s\n%s' % (location, s_str, check)
        if cls.firefly_lab_extension and cls.firefly_url_lab:
            err_message += ('\nCheck the Firefly URL in ~/.jupyter/jupyter_notebook_config.py' +
                            ' or ~/.jupyter/jupyter_notebook_config.json')
        elif firefly_url:
            err_message += 'Check setting of FIREFLY_URL environment variable: %s' % cls.firefly_url
        return err_message

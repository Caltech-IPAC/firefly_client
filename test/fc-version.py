from firefly_client import FireflyClient
import firefly_client
v_str = firefly_client.__dict__['__version__'] if '__version__' in firefly_client.__dict__ else 'development'
print('Version: %s' % v_str)

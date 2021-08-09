from firefly_client import FireflyClient
import firefly_client
import time

lsst_demo_host = 'https://lsst-demo.ncsa.illinois.edu/firefly'
local_host = 'http://127.0.0.1:8080/firefly'
fd = 'https://fireflydev.ipac.caltech.edu/firefly'
irsa_host = 'https://irsa.ipac.caltech.edu/irsaviewer'
data_lsst_host = 'https://data.lsst.cloud/portal/app/'
# host =  'https://fireflydev.ipac.caltech.edu/firefly-multi-ticket/firefly/'
host =  local_host
channel1 = 'channel-test-1'

v_str = firefly_client.__dict__['__version__'] if '__version__' in firefly_client.__dict__ else 'development'
print('Version: %s' % v_str)
FireflyClient._debug = False
token = None
# fc = FireflyClient.make_client(host, channel_override=channel1, launch_browser=True, token=token)
fc = FireflyClient.make_client(host, launch_browser=True, token=token)
print(fc.get_firefly_url())
fc.show_fits(url="http://web.ipac.caltech.edu.s3-us-west-2.amazonaws.com/staff/roby/demo/wise-00.fits")


def example_listener(ev):
    if False:
        print(ev)
    if 'data' not in ev:
        print('no data found in ev')
        return
    data = ev['data']
    if 'payload' in data:
        print(data['payload'])
    if 'type' in data:
        print(data['type'])
        if data['type'] == 'POINT':
            print('   plotId: ' + data['plotId'])
            print('   image point: %s' % data['ipt'])
            print('   world point: %s' % data['wpt'])
        if data['type'] == 'LINE_SELECT' or data['type'] == 'AREA_SELECT':
            print('   plotId: ' + data['plotId'])
            print('   image points: %s to %s' % (data['ipt0'], data['ipt1']))
            print('   world points: %s to %s' % (data['wpt0'], data['wpt1']))


fc.add_extension(ext_type='POINT', title='Output Selected Point', shortcut_key='ctrl-p')
fc.add_extension(ext_type='LINE_SELECT', title='Output Selected line', shortcut_key='meta-b')
fc.add_extension(ext_type='AREA_SELECT', title='Output Selected Area', shortcut_key='a')
# ------------ add listener and wait
fc.add_listener(example_listener)
print('listener is added')
# time.sleep(3)
# fc.remove_listener(example_listener)
# time.sleep(2)
# fc.add_listener(example_listener)
fc.wait_for_events()
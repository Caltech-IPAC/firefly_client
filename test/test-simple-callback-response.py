from firefly_client import FireflyClient

lsst_demo_host = 'https://lsst-demo.ncsa.illinois.edu/firefly'
local_host = 'http://127.0.0.1:8080/firefly'
fd = 'https://fireflydev.ipac.caltech.edu/firefly'
irsa_host = 'https://irsa.ipac.caltech.edu/irsaviewer'
data_lsst_host = 'https://data.lsst.cloud/portal/app/'
host = irsa_host
channel1 = 'channel-test-1'

FireflyClient._debug = True
token = None
fc = FireflyClient.make_client(host, channel_override=channel1, launch_browser=True, token=token)
print(fc.get_firefly_url())


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
            print('   image point: %s' % data['ipt'])
            print('   world point: %s' % data['wpt'])
        if data['type'] == 'LINE_SELECT' or data['type'] == 'AREA_SELECT':
            print('   image points: %s to %s' % (data['ipt0'], data['ipt1']))
            print('   world points: %s to %s' % (data['wpt0'], data['wpt1']))


fc.add_extension(ext_type='POINT', title='Output Selected Point')
fc.add_extension(ext_type='LINE_SELECT', title='Output Selected line')
fc.add_extension(ext_type='AREA_SELECT', title='Output Selected Area')
# ------------ add listener and wait
fc.add_listener(example_listener)
fc.wait_for_events()
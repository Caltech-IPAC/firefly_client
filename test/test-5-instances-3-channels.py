from firefly_client import FireflyClient


def listener1(ev):
    print('l1')
    print(ev)


def listener2(ev):
    print('l2')
    print(ev)


def listener3(ev):
    print('l3')
    print(ev)


def listener4(ev):
    print('l4')
    print(ev)


lsst_demo_host = 'https://lsst-demo.ncsa.illinois.edu/firefly'
local_host = 'http://127.0.0.1:8080/firefly'
host = local_host
channel1 = 'channel-test-1'
channel2 = 'channel-test-2'
channel3 = 'channel-test-3'


print("""
    --------------------------------------------
    5 instance of firefly that define 3 channels")
      - since listeners are only added on 2 channels, only two websockets are made")
      - The first 3 instances use the same channel so they share a websocket")
      - instance 5 never adds a listener and therefore not websocket is made")
      - The initial response on the listeners will show the number connections")
      - example look for something like: channel-test: ['1b4', '1b5']")
      - You can see this on the server side my monitoring firefly.log")
    --------------------------------------------
""")

fc1_c1 = FireflyClient.make_client(host, channel_override=channel1, launch_browser=True)
fc1_c1.add_extension(ext_type='POINT', title='a point')
# fc.add_extension(ext_type='LINE_SELECT', title='a line')
fc2_c1 = FireflyClient.make_client(host, channel_override=channel1, launch_browser=False)
fc3_c1 = FireflyClient.make_client(host, channel_override=channel1, launch_browser=False)
fc1_c2 = FireflyClient.make_client(host, channel_override=channel2, launch_browser=True)
fc1_c2.add_extension(ext_type='POINT', title='a point')
fc1_c3 = FireflyClient.make_client(host, channel_override=channel3, launch_browser=True)
print(f'>>>>>> channel: {channel1}, firefly url: {fc1_c1.get_firefly_url()}')
print(f'>>>>>> channel: {channel2}, firefly url: {fc1_c2.get_firefly_url()}')
print(f'>>>>>> channel: {channel3}, firefly url: {fc1_c3.get_firefly_url()}')
# adding stuff but there is not listener
fc1_c3.show_fits(url="http://web.ipac.caltech.edu.s3-us-west-2.amazonaws.com/staff/roby/demo/wise-00.fits")
fc1_c3.add_extension(ext_type='POINT', title='a point no CB')

# ------------ add listeners
fc1_c1.add_listener(listener1)  # one web socket should be made for first 3 (channel1)
fc2_c1.add_listener(listener2)
fc3_c1.add_listener(listener3)
fc1_c2.add_listener(listener4)  # one web socket should be made for chanel2

# note - no listener added for channel3, so no websocket made

fc1_c1.wait_for_events()

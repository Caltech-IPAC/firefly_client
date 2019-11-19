import astropy.utils.data
from firefly_client import FireflyClient
fc = FireflyClient.make_client('http://127.0.0.1:8080/firefly', channel_override='moc-channel')
print('firefly url: {}'.format(fc.get_firefly_url()))
mocs = ['galex.fits', 'hershel.fits', 'nicmos.fits']

meta = {'PREFERRED_HIPS': 'https://irsa.ipac.caltech.edu/data/hips/CDS/2MASS/Color'}
for m in mocs:
    result = input('load {}? (y or n): '.format(m))
    if result == 'y':
        downloadName = astropy.utils.data.download_file('http://web.ipac.caltech.edu/staff/roby/demo/moc/{}'.format(m),
                                            timeout=120, cache=True)
        serverFile= fc.upload_file(downloadName)
        fc.fetch_table(serverFile, m, title=m, meta=meta)
        print(m)

import json
import urllib.parse
import mimetypes
import base64


class DebugMarker:
    firefly_client_debug = False


def str_2_bool(v): return v.lower() in ("yes", "true", "t", "1")
def _make_key(channel, location): return channel+'---'+location
def debug(s): DebugMarker.firefly_client_debug and print('DEBUG: %s' % s)
def warn(s): print('WARNING: %s' % s)
def dict_to_str(in_dict): return json.dumps(in_dict, indent=2, default=str)


# id for table, region layer, extension
_item_id = {'Table': 0, 'RegionLayer': 0, 'Extension': 0, 'MaskLayer': 0, 'XYPlot': 0,
            'Cell': 0, 'Histogram': 0, 'Plotly': 0, 'Image': 0, 'FootprintLayer': 0}

ALL = 'ALL_EVENTS_ENABLED'


def gen_item_id(item):
    """
    Generate an ID for table, region layer, or extension entity.

    Parameters
    ----------
    item : {'Table', 'RegionLayer', 'Extension', 'XYPlot', 'Cell', 'FootprintLayer'}
        Entity type.

    Returns
    -------
    out : `str`
        ID string.
    """

    if item in _item_id:
        _item_id[item] += 1
        return item + '-' + str(_item_id[item])
    else:
        return None


def create_image_url(image_source):
    def is_url(url): return urllib.parse.urlparse(url).scheme != ''

    if not image_source.startswith('data:image') and not is_url(image_source):
        mime, _ = mimetypes.guess_type(image_source)
        with open(image_source, 'rb') as fp:
            data = fp.read()
            data_uri = b''.join(base64.encodestring(data).splitlines())
            return 'data:%s;base64,%s' % (mime, data_uri)
    return image_source


def ensure3(val, name):
    """ Make sure that the value is a scalar or a list with 3 values otherwise raise ValueError """
    ret = val if type(val) == list else [val, val, val]
    if not len(ret) == 3:
        raise ValueError('%s list should have 3 items' % name)
    return ret


# actions from Firefly
ACTION_DICT = {
    'ShowFits': 'ImagePlotCntlr.PlotImage',
    'AddExtension': 'ExternalAccessCntlr/extensionAdd',
    'FetchTable': 'table.fetch',
    'ShowTable': 'table.search',
    'ShowXYPlot': 'charts.data/chartAdd',
    'ShowPlot': 'charts.data/chartAdd',
    'ZoomImage': 'ImagePlotCntlr.ZoomImage',
    'PanImage': 'ImagePlotCntlr.recenter',
    'StretchImage': 'ImagePlotCntlr.StretchChange',
    'ColorImage': 'ImagePlotCntlr.ColorChange',
    'CreateRegionLayer': 'DrawLayerCntlr.RegionPlot.createLayer',
    'DeleteRegionLayer': 'DrawLayerCntlr.RegionPlot.deleteLayer',
    'AddRegionData': 'DrawLayerCntlr.RegionPlot.addRegion',
    'RemoveRegionData': 'DrawLayerCntlr.RegionPlot.removeRegion',
    'PlotMask': 'ImagePlotCntlr.plotMask',
    'DeleteOverlayMask': 'ImagePlotCntlr.deleteOverlayPlot',
    'AddCell': 'layout.addCell',
    'ShowCoverage': 'layout.enableSpecialViewer',
    'ShowImageMetaData': 'layout.enableSpecialViewer',
    'ReinitViewer': 'app_data.reinitApp',
    'ShowHiPS': 'ImagePlotCntlr.PlotHiPS',
    'ShowImageOrHiPS': 'ImagePlotCntlr.plotHiPSOrImage',
    'ImagelineBasedFootprint': 'DrawLayerCntlr.ImageLineBasedFP.imagelineBasedFPCreate',
    'StartLabWindow': 'StartLabWindow',
    'StartBrowserTab': 'StartBrowserTab'
}
"""Definition of Firefly action (`dict`)."""

# layout view type
LO_VIEW_DICT = {'table': 'tables',
                'image': 'images',
                'xyPlot': 'xyPlots',
                'imageMeta': 'tableImageMeta',
                'coverImage': 'coverageImage'}
"""Definition of layout viewer (`dict`)."""

# extension type
EXTENSION_TYPE = ['AREA_SELECT', 'LINE_SELECT', 'POINT', 'table.highlight', 'table.select']
"""Type of plot where the extension is added to (`list` of `str`)."""

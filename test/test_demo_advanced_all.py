import time

import pytest
from firefly_client import FireflyClient
from pytest_container.container import ContainerData
from test.container import FIREFLY_CONTAINER


@pytest.mark.parametrize("container", [FIREFLY_CONTAINER])
def test_adv(container: ContainerData):
    assert container.forwarded_ports[0].host_port >= 8000
    assert container.forwarded_ports[0].host_port <= 65534
    assert container.forwarded_ports[0].container_port == 8080
    assert container.forwarded_ports[0].bind_ip == "127.0.0.1"

    time.sleep(5)

    host = f"http://{container.forwarded_ports[0].bind_ip}:{container.forwarded_ports[0].host_port}/firefly"

    fc = FireflyClient.make_client(url=host, launch_browser=False)

    fc.change_triview_layout(FireflyClient.BIVIEW_T_IChCov)

    target = "10.68479;41.26906;EQ_J2000"  # Galaxy M31
    # other notable targets to try
    # target = '148.88822;69.06529;EQ_J2000'  #Galaxy M81
    # target = '202.48417;47.23056;EQ_J2000'  #Galaxy M51
    # target = '136.9316774;+1.1195886;galactic' # W5 star-forming region

    r = fc.add_cell(0, 4, 2, 2, "tables", "main")

    if r["success"]:
        fc.show_table(
            tbl_id="wiseCatTbl",
            title="WISE catalog",
            target_search_info={
                "catalogProject": "WISE",
                "catalog": "allwise_p3as_psd",
                "position": target,
                "SearchMethod": "Cone",
                "radius": 1200,
            },
            options={"removable": True, "showUnits": False, "showFilters": True},
        )

    # Add first chart - scatter (plot.ly direct plot)
    # in cell 0, 0, 2, 2,
    viewer_id = "newChartContainer"
    r = fc.add_cell(0, 0, 2, 2, "xyPlots", viewer_id)

    if r["success"]:
        trace1 = {
            "tbl_id": "wiseCatTbl",
            "x": "tables::w1mpro-w2mpro",
            "y": "tables::w2mpro-w3mpro",
            "mode": "markers",
            "type": "scatter",
            "marker": {"size": 4},
        }
        trace_data = [trace1]

        layout_s = {
            "title": "Color-Color",
            "xaxis": {"title": "w1mpro-w2mpro (mag)"},
            "yaxis": {"title": "w2mpro-w3mpro (mag)"},
        }
        fc.show_chart(group_id=viewer_id, layout=layout_s, data=trace_data)

    # Add second chart - heatmap  (plot.ly direct plot)
    # in cell 2, 0, 2, 3
    viewer_id = "heatMapContainer"
    r = fc.add_cell(2, 0, 2, 3, "xyPlots", viewer_id)
    print(r)

    if r["success"]:
        dataHM = [
            {
                "type": "fireflyHeatmap",
                "name": "w1 vs. w2",
                "tbl_id": "wiseCatTbl",
                "x": "tables::w1mpro",
                "y": "tables::w2mpro",
                "colorscale": "Blues",
            },
            {
                "type": "fireflyHeatmap",
                "name": "w1 vs. w3",
                "tbl_id": "wiseCatTbl",
                "x": "tables::w1mpro",
                "y": "tables::w3mpro",
                "colorscale": "Reds",
                "reversescale": True,
            },
            {
                "type": "fireflyHeatmap",
                "name": "w1 vs. w4",
                "tbl_id": "wiseCatTbl",
                "x": "tables::w1mpro",
                "y": "tables::w4mpro",
                "colorscale": "Greens",
            },
        ]

        layout_hm = {
            "title": "Magnitude-magnitude densities",
            "xaxis": {"title": "w1 photometry (mag)"},
            "yaxis": {"title": ""},
            "firefly": {"xaxis": {"min": 5, "max": 20}, "yaxis": {"min": 4, "max": 18}},
        }

        fc.show_chart(group_id=viewer_id, layout=layout_hm, data=dataHM)

    # Add third chart - histogram  (plot.ly direct plot)
    # in cell 2, 2, 2, 3
    viewer_id = "histContainer"
    r = fc.add_cell(2, 2, 2, 3, "xyPlots", viewer_id)

    if r["success"]:
        dataH = [
            {
                "type": "fireflyHistogram",
                "name": "w1mpro",
                "marker": {"color": "rgba(153, 51, 153, 0.8)"},
                "firefly": {
                    "tbl_id": "wiseCatTbl",
                    "options": {
                        "algorithm": "fixedSizeBins",
                        "fixedBinSizeSelection": "numBins",
                        "numBins": 30,
                        "columnOrExpr": "w1mpro",
                    },
                },
            },
            {
                "type": "fireflyHistogram",
                "name": "w2mpro",
                "marker": {"color": "rgba(102, 153, 0, 0.7)"},
                "firefly": {
                    "tbl_id": "wiseCatTbl",
                    "options": {
                        "algorithm": "fixedSizeBins",
                        "fixedBinSizeSelection": "numBins",
                        "numBins": 40,
                        "columnOrExpr": "w2mpro",
                    },
                },
            },
        ]

        layout_hist = {
            "title": "Photometry histogram",
            "xaxis": {"title": "photometry (mag)"},
            "yaxis": {"title": ""},
        }
        result = fc.show_chart(group_id=viewer_id, layout=layout_hist, data=dataH)

        assert result is not None

    # Add fourth chart - 3D plot (plot.ly direct plot)
    # in cell 2, 4, 2, 3,
    viewer_id = "3dChartContainer"
    r = fc.add_cell(2, 4, 2, 3, "xyPlots", viewer_id)

    if r["success"]:
        data3d = [
            {
                "type": "scatter3d",
                "name": "w1-w2-w3",
                "tbl_id": "wiseCatTbl",
                "x": "tables::w1mpro",
                "y": "tables::w2mpro",
                "z": "tables::w3mpro",
                "mode": "markers",
                "marker": {
                    "size": 3,
                    "color": "rgba(127, 127, 127, 1)",
                    "line": {"color": "rgba(127, 127, 127, 0.5)", "width": 1},
                },
                "hoverinfo": "x+y+z",
            }
        ]

        fsize = {"size": 11}
        layout3d = {
            "title": "Photometry in band 1, 2, 3",
            "scene": {
                "xaxis": {"title": "w1 (mag)", "titlefont": fsize},
                "yaxis": {"title": "w2 (mag)", "titlefont": fsize},
                "zaxis": {"title": "w3 (mag)", "titlefont": fsize},
            },
        }

        fc.show_chart(group_id=viewer_id, is_3d=True, layout=layout3d, data=data3d)

    # Add a three color fits
    # in cell 0, 2, 2, 2
    viewer_id = "3C"
    r = fc.add_cell(0, 2, 2, 2, "images", viewer_id)
    rv = "92,-2,92,8,NaN,2,44,25,600,120"
    if r["success"]:
        threeC = [
            {
                "Type": "SERVICE",
                "Service": "WISE",
                "Title": "3 color",
                "SurveyKey": "Atlas",
                "SurveyKeyBand": "1",
                "WorldPt": target,
                "RangeValues": rv,
                "SizeInDeg": "1",
            },
            {
                "Type": "SERVICE",
                "Service": "WISE",
                "Title": "3 color",
                "SurveyKey": "Atlas",
                "SurveyKeyBand": "2",
                "WorldPt": target,
                "RangeValues": rv,
                "SizeInDeg": "1",
            },
            {
                "Type": "SERVICE",
                "Service": "WISE",
                "Title": "3 color",
                "SurveyKey": "Atlas",
                "SurveyKeyBand": "3",
                "WorldPt": target,
                "RangeValues": rv,
                "SizeInDeg": "1",
            },
        ]
        fc.show_fits_3color(threeC, viewer_id=viewer_id)

    fc.change_triview_layout(FireflyClient.BIVIEW_IChCov_T)

    rv = "92,-2,92,8,NaN,2,44,25,600,120"
    threeC = [
        {
            "Type": "SERVICE",
            "Service": "WISE",
            "Title": "3 color",
            "SurveyKey": "Atlas",
            "SurveyKeyBand": "1",
            "WorldPt": target,
            "RangeValues": rv,
            "SizeInDeg": "1",
        },
        {
            "Type": "SERVICE",
            "Service": "WISE",
            "Title": "3 color",
            "SurveyKey": "Atlas",
            "SurveyKeyBand": "2",
            "WorldPt": target,
            "RangeValues": rv,
            "SizeInDeg": "1",
        },
        {
            "Type": "SERVICE",
            "Service": "WISE",
            "Title": "3 color",
            "SurveyKey": "Atlas",
            "SurveyKeyBand": "3",
            "WorldPt": target,
            "RangeValues": rv,
            "SizeInDeg": "1",
        },
    ]
    fc.show_fits_3color(threeC)

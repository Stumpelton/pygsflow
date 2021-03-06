# test ModflowAwu package
import os
from gsflow.modflow import Modflow, ModflowAwu
import numpy as np


def test_ModflowAg_load_write():
    ws = "../examples/data/sagehen/modflow"
    agfile = "sagehen.awu"
    nper = 344

    ml = Modflow("agtest", model_ws=ws)

    ag = ModflowAwu.load(os.path.join(ws, agfile), ml,
                         nper=nper, ext_unit_dict={})


    ws2 = "./temp"
    ml.change_model_ws(ws2)
    ag.write_file()

    agfile2 = "agtest.awu"
    ml2 = Modflow("agtest2", model_ws=ws2)
    ag2 = ModflowAwu.load(os.path.join(ws2, agfile2), ml2,
                          nper=nper, ext_unit_dict={})

    assert repr(ag.options) == repr(ag2.options)

    for ix, rec in enumerate(ag.time_series):
        assert rec == ag2.time_series[ix]

    for ix, rec in enumerate(ag.well_list):
        assert rec == ag2.well_list[ix]

    for per in range(nper):

        for ix, rec in enumerate(ag.irrdiversion[per]):
            rec2 = ag2.irrdiversion[per][ix]
            assert rec['segid'] == rec2['segid']
            assert rec['hru_id0'] == rec2['hru_id0']

        for ix, rec in enumerate(ag.irrwell[per]):
            rec2 = ag2.irrwell[per][ix]
            assert rec['wellid'] == rec2['wellid']
            assert rec["hru_id0"] == rec2["hru_id0"]

        for ix, rec in enumerate(ag.supwell[per]):
            rec2 = ag2.supwell[per][ix]
            assert rec['wellid'] == rec2['wellid']
            assert rec['segid0'] == rec2['segid0']

    assert not ag.plotable
    assert ModflowAwu.ftype() == "AWU"


if __name__ == "__main__":
    test_ModflowAg_load_write()
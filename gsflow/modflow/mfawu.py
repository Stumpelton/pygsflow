import os
import flopy
import numpy as np
from flopy.pakbase import Package
from flopy.utils import MfList
from flopy.utils.recarray_utils import create_empty_recarray
from gsflow.utils.io import multi_line_strip
from flopy.utils.optionblock import OptionBlock
from collections import OrderedDict


class ModflowAwu(Package):
    """
    The ModflowAwu class is used to build read, write, and edit data
    from the MODFLOW-NWT AG package.

    Parameters
    ----------
    model : gsflow.modflow.Modflow object
        model object
    extension : str, optional
        default is .ag
    options : flopy.utils.OptionBlock object
        option block utility from flopy
    unitnumber : list, optional
        fortran unit number for modflow, default 69
    filenames : list, optional
        file name for ModflowAwu package to write input

    Examples
    --------

    load a ModflowAwu file

    >>> ml = gsflow.modflow.Modflow('awutest')
    >>> awu = gsflow.modflow.ModflowAwu.load('test.awu', ml, nper=2, method="gsflow")

    """
    _options = OrderedDict([('noprint', OptionBlock.simple_flag),
                            ('irrigation_diversion', {OptionBlock.dtype: np.bool_,
                                                      OptionBlock.nested: True,
                                                      OptionBlock.n_nested: 2,
                                                      OptionBlock.vars: OrderedDict(
                                                          [('numirrdiversions', OptionBlock.simple_int),
                                                           ('maxcellsdiversion', OptionBlock.simple_int)]
                                                      )}),
                            ('irrigation_well', {OptionBlock.dtype: np.bool_,
                                                 OptionBlock.nested: True,
                                                 OptionBlock.n_nested: 2,
                                                 OptionBlock.vars: OrderedDict(
                                                     [("numirrwells", OptionBlock.simple_int),
                                                      ('maxcellswell', OptionBlock.simple_int)]
                                                 )}),
                            ('supplemental_well', {OptionBlock.dtype: np.bool_,
                                                   OptionBlock.nested: True,
                                                   OptionBlock.n_nested: 2,
                                                   OptionBlock.vars: OrderedDict(
                                                       [("numsupwells", OptionBlock.simple_int),
                                                        ("maxdiversions", OptionBlock.simple_int)]
                                                   )}),
                            ('maxwells', {OptionBlock.dtype: np.bool_,
                                         OptionBlock.nested: True,
                                         OptionBlock.n_nested: 1,
                                         OptionBlock.vars: OrderedDict(
                                             [('nummaxwell', OptionBlock.simple_int)]
                                         )}),
                            ('tabfiles', OptionBlock.simple_tabfile),
                            ('phiramp', OptionBlock.simple_flag),
                            ('etdemand', OptionBlock.simple_flag),
                            ('trigger', OptionBlock.simple_flag),
                            ('timeseries_diversion', OptionBlock.simple_flag),
                            ('timeseries_well', OptionBlock.simple_flag),
                            ('timeseries_diversionet', OptionBlock.simple_flag),
                            ('timeseries_wellet', OptionBlock.simple_flag),
                            ('diversionlist', {OptionBlock.dtype: np.bool_,
                                               OptionBlock.nested: True,
                                               OptionBlock.n_nested: 1,
                                               OptionBlock.vars: OrderedDict(
                                                   [('unit_diversionlist', OptionBlock.simple_int)]
                                               )}),
                            ('welllist', {OptionBlock.dtype: np.bool_,
                                          OptionBlock.nested: True,
                                          OptionBlock.n_nested: 1,
                                          OptionBlock.vars: OrderedDict(
                                              [('unit_diversionlist', OptionBlock.simple_int)]
                                          )}),
                            ('wellirrlist', {OptionBlock.dtype: np.bool_,
                                             OptionBlock.nested: True,
                                             OptionBlock.n_nested: 1,
                                             OptionBlock.vars: OrderedDict(
                                                 [('unit_wellirrlist', OptionBlock.simple_int)]
                                             )}),
                            ('diversionirrlist', {OptionBlock.dtype: np.bool_,
                                                  OptionBlock.nested: True,
                                                  OptionBlock.n_nested: 1,
                                                  OptionBlock.vars: OrderedDict(
                                                      [('unit_diversionirrlist', OptionBlock.simple_int)]
                                                  )}),
                            ('wellcbc', {OptionBlock.dtype: np.bool_,
                                         OptionBlock.nested: True,
                                         OptionBlock.n_nested: 1,
                                         OptionBlock.vars: OrderedDict(
                                             [('unitcbc', OptionBlock.simple_int)]
                                         )})
                            ])

    def __init__(self, model, options=None, time_series=None, well_list=None,
                 irrdiversion=None, irrwell=None, supwell=None,
                 extension="awu", unitnumber=None, filenames=None, nper=0):

        # setup the package parent class
        if unitnumber is None:
            unitnumber = ModflowAwu.defaultunit()

        if filenames is None:
            filenames = [None]
        elif isinstance(filenames, str):
            filenames = [filenames]

        name = [ModflowAwu.ftype()]
        units = [unitnumber]
        extra = [""]

        # set package name
        fname = [filenames[0]]

        super(ModflowAwu, self).__init__(model, extension=extension,
                                         name=name, unit_number=units,
                                         extra=extra, filenames=fname)

        # set up class
        self.heading = "# {} package for {}, generated " \
                       "by pygsflow\n".format(self.name[0],
                                              model.version_types[model.version])
        self.url = "awu.htm"

        # options
        self.noprint = None
        self.irrigation_diversion = False
        self.numirrdiversions = 0
        self.maxcellsdiversion = 0
        self.irrigation_well = False
        self.numirrwells = 0
        self.supplemental_well = False
        self.numsupwells = 0
        self.maxdiversions = 0
        self.maxwells = False
        self.nummaxwell = 0
        self.tabfiles = False
        self.numtab = 0
        self.maxval = 0
        self.phiramp = False
        self.etdemand = False
        self.trigger = False
        self.timeseries_diversion = False
        self.timeseries_well = False
        self.timeseries_diversionet = False
        self.timeseries_wellet = False
        self.diversionlist = False
        self.unit_diversionlist = None
        self.welllist = False
        self.unit_welllist = None
        self.wellirrlist = False
        self.unit_wellirrlist = None
        self.diversionirrlist = False
        self.unit_diversionirrlist = None
        self.wellcbc = False
        self.unitcbc = None

        if isinstance(options, OptionBlock):
            self.options = options
            self._update_attrs_from_option_block(options)
        else:
            self.options = OptionBlock("", ModflowAwu)

        self.time_series = time_series
        self.well_list = well_list
        self.irrdiversion = irrdiversion
        self.irrwell = irrwell
        self.supwell = supwell

        self._nper = self.parent.nper
        if self.parent.nper == 0:
            self._nper = nper

        self.parent.add_package(self)

    @property
    def segment_list(self):
        """
        Method to get a unique list of segments from irrdiversion

        Returns
        -------

        """
        segments = []
        if self.irrdiversion is not None:
            for kper, recarray in self.irrdiversion.items():
                if np.isscalar(recarray):
                    # if recarray is scalar, it means there is no divs or use previouse info
                    continue
                t = np.unique(recarray["segid"])
                for seg in t:
                    segments.append(seg)

            segments = list(set(segments))

        return segments

    def _update_attrs_from_option_block(self, options):
        """
        Method to update option attributes from the
        option block

        Parameters
        ----------
        options : OptionBlock object

        """
        for key, ctx in options._context.items():
            if key in options.__dict__:
                val = options.__dict__[key]
                self.__setattr__(key, val)
                if ctx[OptionBlock.nested]:
                    for k2, ctx2 in ctx[OptionBlock.vars].items():
                        if k2 in options.__dict__:
                            v2 = options.__dict__[k2]
                            self.__setattr__(k2, v2)

    def write_file(self, check=False):
        """
        Write method for ModflowAwu

        Parameters
        ----------
        check: bool
            not implemented currently
        """
        ws = self.parent.model_ws
        name = self.file_name[0]
        with open(os.path.join(ws, name), "w") as foo:
            foo.write(self.heading)

            # update options
            self.options.update_from_package(self)
            self.options.write_options(foo)

            # check if there is a timeseries block and write output
            if self.time_series is not None:
                foo.write("# ag time series\n")
                fmt = "{}   {:d}   {:d}\n"
                foo.write("TIME SERIES \n")
                for record in self.time_series:
                    if record["keyword"] in ('welletall', 'wellall'):
                        foo.write("{}   {:d}\n".format(record['keyword'],
                                                       record['unit']).upper())
                    else:
                        foo.write(fmt.format(*record).upper())

                foo.write("END \n")

            # check if item 12 exists and write item 12 - 14
            if self.segment_list is not None:
                foo.write('# segment list for irriagation diversions\n')
                foo.write("SEGMENT LIST\n")
                for iseg in self.segment_list:
                    foo.write("{:d}\n".format(iseg))

                foo.write("END \n")

            # check if item 15 exists and write item 15 through 17
            if self.well_list is not None:
                foo.write("# ag well list\n")
                foo.write("WELL LIST \n")
                if self.tabfiles:
                    # item 16a
                    fmt16a = True
                    fmt16 = "{:d}   {:d}   {:d}   {:d}   {:d}\n"
                else:
                    # item 16b
                    fmt16a = False
                    fmt16 = "{:d}   {:d}   {:d}   {:f}\n"

                for record in self.well_list:
                    if fmt16a:
                        foo.write(fmt16.format(record["unit"],
                                               record["tabval"],
                                               record["k"] + 1,
                                               record["i"] + 1,
                                               record["j"] + 1))
                    else:
                        foo.write(fmt16.format(record["k"] + 1,
                                               record["i"] + 1,
                                               record["j"] + 1,
                                               record["flux"]))

                foo.write("END \n")

            foo.write("# ag stress period data\n")
            for per in range(self._nper):
                foo.write("STRESS PERIOD {}\n".format(per + 1))

                # check for item 18 and write items 18 - 21
                if self.irrdiversion is not None:
                    foo.write("IRRDIVERSION \n")

                    if self.trigger:
                        # item 20
                        fmt20 = "{:d}   {:d}   {:f}   {:f}\n"
                    else:
                        # item 20, if trigger option is false we need 0's for period and trigger fac.
                        fmt20 = "{:d}   {:d}   0   0\n"

                    if per in self.irrdiversion:
                        if np.isscalar(self.irrdiversion[per]):
                            # write item 19
                            foo.write("-1  \n")
                        else:
                            recarray = self.irrdiversion[per]

                            # write item 19
                            foo.write("{:d} \n".format(len(recarray)))

                            if "i0" in recarray.dtype.names:
                                # item 21a
                                fmt21a = True
                                fmt21 = "{:d}   {:d}   {:f}   {:f}\n"
                            else:
                                # item 21b
                                fmt21a = False
                                fmt21 = "{:d}   {:f}   {:f}\n"

                            for rec in recarray:
                                num = rec['numcell']
                                if self.trigger:
                                    foo.write(fmt20.format(rec['segid'],
                                                           rec['numcell'],
                                                           rec['period'],
                                                           rec['triggerfact']))
                                else:
                                    foo.write(fmt20.format(rec['segid'],
                                                           rec['numcell']))

                                for i in range(num):
                                    if fmt21a:
                                        foo.write(fmt21.format(rec['i{}'.format(i)] + 1,
                                                               rec["j{}".format(i)] + 1,
                                                               rec["eff_fact{}".format(i)],
                                                               rec['field_fact{}'].format(i)))
                                    else:
                                        foo.write(fmt21.format(rec['hru_id{}'.format(i)] + 1,
                                                               rec["eff_fact{}".format(i)],
                                                               rec['field_fact{}'.format(i)]))

                    else:
                        # write item 19
                        foo.write("0  \n")

                # check for item 22 and write 22 - 25
                if self.irrwell is not None:
                    foo.write("IRRWELL \n")

                    if self.trigger:
                        # item 24
                        fmt24 = "{:d}   {:d}   {:f}   {:f}\n"
                    else:
                        # item 24
                        fmt24 = "{:d}   {:d}   0   0\n"

                    if per in self.irrwell:
                        if np.isscalar(self.irrwell[per]):
                            foo.write("-1  \n")
                        else:
                            recarray = self.irrwell[per]

                            # write item 23
                            foo.write("{:d} \n".format(len(recarray)))

                            if "i0" in recarray.dtype.names:
                                fmt25a = False
                            else:
                                fmt25a = True

                            fmt25 = "{:d}   {:d}   {:f}   {:f}\n"

                            for rec in recarray:
                                num = rec['numcell']
                                if self.trigger:
                                    foo.write(fmt24.format(rec['wellid'] + 1,
                                                           rec['numcell'],
                                                           rec['period'],
                                                           rec['triggerfact']))
                                else:
                                    foo.write(fmt24.format(rec['wellid'] + 1,
                                                           rec['numcell']))

                                for i in range(num):
                                    if fmt25a:
                                        foo.write(fmt25.format(rec['hru_id{}'.format(i)] + 1,
                                                               rec['dum{}'.format(i)] + 1,
                                                               rec["eff_fact{}".format(i)],
                                                               rec['field_fact{}'.format(i)]))
                                    else:
                                        foo.write(fmt25.format(rec['i{}'.format(i)] + 1,
                                                               rec["j{}".format(i)] + 1,
                                                               rec["eff_fact{}".format(i)],
                                                               rec['field_fact{}'].format(i)))
                    else:
                        # write item 23
                        foo.write("0  \n")

                # check if item 26 and write items 26 - 29
                if self.supwell is not None:
                    foo.write("SUPWELL \n")

                    fmt28 = "{:d}   {:d}\n"

                    if per in self.supwell:
                        if np.isscalar(self.supwell[per]):
                            foo.write("-1  \n")
                        else:
                            recarray = self.supwell[per]
    
                            # write item 27
                            foo.write("{:d} \n".format(len(recarray)))
    
                            for rec in recarray:
                                num = rec['numcell']
    
                                foo.write(fmt28.format(rec["wellid"] + 1,
                                                       rec["numcell"]))
    
                                for i in range(num):
                                    if rec["fracsupmax{}".format(i)] != -1e+10:
                                        foo.write("{:d}   {:f}   {:f}\n".format(rec['segid{}'.format(i)],
                                                                                rec['fracsup{}'.format(i)],
                                                                                rec['fracsupmax{}'.format(i)]))
    
                                    else:
                                        foo.write("{:d}   {:f}\n".format(rec['segid{}'.format(i)],
                                                                         rec['fracsup{}'.format(i)]))

                    else:
                        # write item 27
                        foo.write("0 \n")

                foo.write("END \n")

    @staticmethod
    def get_empty(numrecords, maxells=0, block="well"):
        """
        Creates an empty record array corresponding to the block data type
        it is associated with.

        Parameters
        ----------
        numrecords : int
            number of records to create recarray with
        maxells : int, optional
            maximum number of irrigation links
        block : str
            str which indicates data set valid options are
            "well" ,
            "tabfile_well" ,
            "timeseries" ,
            "irrdiversion_modflow" ,
            "irrdiversion_gsflow" ,
            "irrwell_modflow" ,
            "irrwell_gsflow" ,
            "supwell"

        Returns:
            np.recarray

        """
        dtype = ModflowAwu.get_default_dtype(maxells=maxells, block=block)
        return create_empty_recarray(numrecords, dtype, default_value=-1.0E+10)

    @staticmethod
    def get_default_dtype(maxells=0, block="well"):
        """

        Parameters
        ----------
        maxells : int
             maximum number of irrigation links
        block : str
            str which indicates data set valid options are
            "well" ,
            "tabfile_well" ,
            "timeseries" ,
            "irrdiversion_modflow" ,
            "irrdiversion_gsflow" ,
            "irrwell_modflow" ,
            "irrwell_gsflow" ,
            "supwell"

        Returns
        -------
            dtype : (list, tuple)
        """
        if block == "well":
            dtype = [('k', np.int), ('i', np.int),
                     ('j', np.int), ('flux', np.float)]

        elif block == "tabfile_well":
            dtype = [('unit', np.int), ('tabval', np.int),
                     ('k', np.int), ('i', np.int), ('j', np.int)]

        elif block == "time series":
            dtype = [('keyword', np.object), ('id', np.int),
                     ('unit', np.int)]

        elif block == "irrdiversion_modflow":
            dtype = [("segid", np.int), ("numcell", np.int),
                     ("period", np.float), ("triggerfact", np.float)]

            for i in range(maxells):
                dtype += [("i{}".format(i), np.int),
                          ("j{}".format(i), np.int),
                          ("eff_fact{}".format(i), np.float),
                          ("field_fact{}".format(i), np.float)]

        elif block == "irrdiversion_gsflow":
            dtype = [("segid", np.int), ("numcell", np.int),
                     ("period", np.float), ("triggerfact", np.float)]

            for i in range(maxells):
                dtype += [("hru_id{}".format(i), np.int),
                          ("eff_fact{}".format(i), np.float),
                          ("field_fact{}".format(i), np.float)]

        elif block == "irrwell_modflow":
            dtype = [("wellid", np.int), ("numcell", np.int),
                     ("period", np.float), ("triggerfact", np.float)]

            for i in range(maxells):
                dtype += [("i{}".format(i), np.int),
                          ("j{}".format(i), np.int),
                          ("eff_fact{}".format(i), np.float),
                          ("field_fact{}".format(i), np.float)]

        elif block == "irrwell_gsflow":
            dtype = [("wellid", np.int), ("numcell", np.int),
                     ("period", np.float), ("triggerfact", np.float)]

            for i in range(maxells):
                dtype += [("hru_id{}".format(i), np.int),
                          ("dum{}".format(i), np.int),
                          ("eff_fact{}".format(i), np.float),
                          ("field_fact{}".format(i), np.float)]

        elif block == "supwell":
            dtype = [("wellid", np.int), ("numcell", np.int)]

            for i in range(maxells):
                dtype += [("segid{}".format(i), np.int),
                          ("fracsup{}".format(i), np.float),
                          ("fracsupmax{}".format(i), np.float)]

        else:
            raise NotImplementedError("block type {}, not supported".format(block))

        return np.dtype(dtype)

    @staticmethod
    def load(f, model, nper=0, method="gsflow", ext_unit_dict=None):
        """
        Method to load the AG package from file

        Parameters
        ----------
        f : str
            filename
        model : gsflow.modflow.Modflow object
            model to attach the ag pacakge to
        nper : int
            number of stress periods in model
        method : str
            "gsflow" or "modflow"
        ext_unit_dict : dict, optional

        Returns
        -------
            ModflowAwu object
        """
        if nper == 0:
            nper = model.nper

        with open(f) as mfag:

            # strip the file header if it exists
            while True:
                line = multi_line_strip(mfag)
                if line:
                    break

            # read the options block
            options = OptionBlock.load_options(mfag, ModflowAwu)

            line = multi_line_strip(mfag)

            time_series = None
            if "time series" in line:
                # read time_series
                t = []
                while True:
                    line = multi_line_strip(mfag)
                    if line == "end":
                        line = multi_line_strip(mfag)
                        break

                    else:
                        t.append(line.split())

                if len(t) > 0:
                    nrec = len(t)
                    time_series = ModflowAwu.get_empty(nrec, block="time series")

                    for ix, rec in enumerate(t):
                        if rec[0] in ('welletall', 'wellall'):
                            time_series[ix] = (rec[0], -999, rec[-1])
                        else:
                            time_series[ix] = tuple(rec[:3])

            # read item 12-14
            segments = None
            if "segment list" in line:
                # read item 13
                t = []
                while True:
                    line = multi_line_strip(mfag)
                    if line == "end":
                        line = multi_line_strip(mfag)
                        break
                    else:
                        t.append(line.split())

                if len(t) > 0:
                    segments = []
                    for rec in t:
                        iseg = int(rec[0])
                        segments.append(iseg)

            # read item 15-17 well_list
            well = None
            if "well list" in line:
                # read item 16
                t = []
                while True:
                    line = multi_line_strip(mfag)
                    if line == "end":
                        line = multi_line_strip(mfag)
                        break

                    else:
                        t.append(line.split())

                if len(t) > 0:
                    nrec = len(t)

                    # check if this is block 16a
                    if isinstance(options.tabfiles, np.recarray):
                        tf = True
                        well = ModflowAwu.get_empty(nrec, block='tabfile_well')
                    else:
                        tf = False
                        well = ModflowAwu.get_empty(nrec, block="well")

                    for ix, rec in enumerate(t):
                        if not tf:
                            k = int(rec[0]) - 1
                            i = int(rec[1]) - 1
                            j = int(rec[2]) - 1
                            well[ix] = (k, i, j, rec[3])
                        else:
                            k = int(rec[2]) - 1
                            i = int(rec[3]) - 1
                            j = int(rec[4]) - 1
                            well[ix] = (rec[0], rec[1], k, i, j)

            maxcellsdiversion = 0
            if options.maxcellsdiversion is not None:
                maxcellsdiversion = options.maxcellsdiversion

            maxcellswell = 0
            if options.maxcellswell is not None:
                maxcellswell = options.maxcellswell

            maxdiversions = 0
            if options.maxdiversions is not None:
                maxdiversions = options.maxdiversions

            irr_diversion = {}
            irr_well = {}
            sup_well = {}
            # get the stress period data from blocks 18 - 29
            for per in range(nper):
                while True:
                    if 'stress period' in line:
                        line = multi_line_strip(mfag)

                    # block 18
                    elif 'irrdiversion' in line:
                        # read block 19
                        nrec = int(multi_line_strip(mfag).split()[0])
                        if nrec == -1:
                            irr = np.copy(irr_diversion[per - 1]) # todo: (Ayman) I think we need to use -1
                        else:
                            # model.version2 will need to be changed
                            # for pure flopy compatibility if migrated
                            if model.version2 == "gsflow":
                                irr = ModflowAwu.get_empty(nrec, maxells=maxcellsdiversion,
                                                           block="irrdiversion_gsflow")
                            else:
                                irr = ModflowAwu.get_empty(nrec, maxells=maxcellsdiversion,
                                                           block="irrdiversion_modflow")

                            # read blocks 20 & 21
                            irr = _read_block_21_25_or_29(mfag, nrec, irr, 21)
                        irr_diversion[per] = irr
                        line = multi_line_strip(mfag)

                    # block 22
                    elif 'irrwell' in line:
                        # read block 23
                        nrec = int(multi_line_strip(mfag).split()[0])
                        if nrec == -1:
                            irr = np.copy(irr_well[per - 1])
                        else:
                            # model.version2 will need to be changed
                            # for pure flopy compatibility if migrated
                            if model.version2 == "gsflow":
                                irr = ModflowAwu.get_empty(nrec, maxells=maxcellswell,
                                                           block="irrwell_gsflow")
                            else:
                                irr = ModflowAwu.get_empty(nrec, maxells=maxcellswell,
                                                           block="irrwell_modflow")

                            # read blocks 24 & 25
                            irr = _read_block_21_25_or_29(mfag, nrec, irr, 25)

                        irr_well[per] = irr
                        line = multi_line_strip(mfag)

                    # block 26
                    elif 'supwel' in line:
                        # read block 27
                        nrec = int(multi_line_strip(mfag).split()[0])
                        if nrec == -1:
                            sup = np.copy(sup_well[per - 1])

                        else:
                            sup = ModflowAwu.get_empty(nrec, maxells=maxdiversions,
                                                       block="supwell")
                            # read blocks 28 & 29
                            sup = _read_block_21_25_or_29(mfag, nrec, sup, 29)

                        sup_well[per] = sup
                        line = multi_line_strip(mfag)

                    # block 30?
                    elif "end" in line:
                        if per == nper - 1:
                            break

                        line = multi_line_strip(mfag)
                        break

                    else:
                        raise ValueError("Something went wrong at: {}".format(line))

        return ModflowAwu(model, options=options, time_series=time_series,
                          well_list=well, irrwell=irr_well,
                          irrdiversion=irr_diversion,
                          supwell=sup_well, nper=nper)

    @staticmethod
    def defaultunit():
        return 69

    @staticmethod
    def ftype():
        return "AWU"

    @property
    def plotable(self):
        return False


def _read_block_21_25_or_29(fobj, nrec, recarray, block):
    """
    Method to read blocks 21, 25, and 29 from the AG package

    Parameters
    ----------
    fobj : File object
    nrec : int
        number of records
    recarray : np.recarray
        recarray to add data to
    block : int
        valid options are 6, 10, or 14

    Returns
    -------
        recarray : np.recarray
    """
    t = []

    hrus = False
    if "hru_id0" in recarray.dtype.names and \
            "segid" in recarray.dtype.names:
        hrus = True

    for _ in range(nrec):
        t1 = []
        ll = multi_line_strip(fobj).split()
        if block in (21, ):
            # do not zero adjust segid
            ll[0] = int(ll[0])
        else:
            ll[0] = int(ll[0]) - 1

        if block in (21, 25):
            # correct list length if not using trigger factor
            if len(ll) == 2:
                ll += [-1e+10, 1e+10]
            elif len(ll) == 3:
                ll += [1e-10]

            t1 += ll[:4]

        elif block == 29:
            t1 += ll[:2]

        else:
            raise AssertionError("block number must be 6, 10, or 14")

        for numcell in range(int(ll[1])):
            if block == 29:
                if len(ll) == 2:
                    ll += [1e-10]

            if hrus or block == 29:
                tmp = multi_line_strip(fobj).split()[:3]
                if block == 29:
                    tmp[0] = int(tmp[0])
                else:
                    tmp[0] = int(tmp[0]) - 1
            else:
                tmp = multi_line_strip(fobj).split()[:4]
                tmp[0:2] = [int(tmp[0]) - 1, int(tmp[1]) - 1]

            t1 += tmp

        t.append(t1)

    if len(t) > 0:
        for ix, rec in enumerate(t):
            for ix2, name in enumerate(recarray.dtype.names):
                if ix2 >= len(rec):
                    pass
                else:
                    recarray[name][ix] = rec[ix2]
    return recarray

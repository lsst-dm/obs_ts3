from lsst.obs.ts3.ingest import Ts3ParseTask
config.parse.retarget(Ts3ParseTask)
config.parse.translation = {
    'expTime': 'EXPTIME',
    'object': 'OBJECT',
    'imageType': 'IMGTYPE',
    'filter': 'FILTER',
    'lsstSerial': 'LSST_NUM',
    'date': 'DATE-OBS'
}
config.parse.translators = {
    'ccd': 'translate_ccd',
    'visit': 'translate_visit',
    # 'date': 'translate_date',
}
config.parse.defaults = {
    'object': "UNKNOWN",
}
config.parse.hdu = 1

config.register.columns = {
    'visit': 'int',
    'basename': 'text',
    'filter': 'text',
    'date': 'text',
    'expTime': 'double',
    'ccd': 'int',
    'object': 'text',
    'imageType': 'text',
    'lsstSerial': 'text',
}
config.register.visit = list(config.register.columns.keys())

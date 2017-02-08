from lsst.obs.monocam.ingest import MonocamParseTask
config.parse.retarget(MonocamParseTask)
config.parse.translation = {
    'expTime': 'EXPTIME',
    'object': 'OBJECT',
    'visit': 'VISIT',
    'imageType': 'IMAGETYP',
    'filter': 'FILTER',
}
config.parse.translators = {
    'ccd': 'translate_ccd',
    'date': 'translate_date',
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
}
config.register.visit = list(config.register.columns.keys())

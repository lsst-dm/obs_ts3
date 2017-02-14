from lsst.obs.ts3 import Ts3IsrTask
config.isr.retarget(Ts3IsrTask)

config.isr.doDark = False
config.isr.doBias = False
config.isr.doFlat = False
config.isr.doFringe = False
config.isr.doLinearize = False

config.charImage.repair.doCosmicRay = False
config.charImage.repair.cosmicray.nCrPixelMax = 100000


config.charImage.background.binSize = 128
# config.charImage.detectAndMeasure.detection.background.binSize = 128
# config.calibrate.detectAndMeasure.detection.background.binSize = 128
config.charImage.background.useApprox = False
# config.charImage.detectAndMeasure.detection.background.useApprox = False
# config.calibrate.detectAndMeasure.detection.background.useApprox = False

# PSFEx gives better PSFs for HSC
try:
    import lsst.meas.extensions.psfex.psfexPsfDeterminer
    config.charImage.measurePsf.psfDeterminer["psfex"].spatialOrder = 2
    config.charImage.measurePsf.psfDeterminer.name = "psfex"
except ImportError as e:
    print "WARNING: Unable to use psfex: %s" % e
    config.charImage.measurePsf.psfDeterminer.name = "pca"

if True:
    # we don't have astrometry_net data (yet) so astrom and photo cal are impossible
    config.doCalibrate = False
elif False:
    # Running on sky data from USNO
    from lsst.meas.astrom import ANetAstrometryTask  # We need to blind-solve because we don't trust the Wcs
    config.calibrate.astrometry.retarget(ANetAstrometryTask)
    for ff in "griz":
        config.calibrate.astrometry.solver.filterMap["SDSS" + ff.upper()] = ff
    config.calibrate.astrometry.solver.useWcsRaDecCenter = False  # It's off for some reason dunno yet
    config.calibrate.astrometry.solver.useWcsParity = False  # I doubt I guess right
    config.calibrate.astrometry.solver.useWcsPixelScale = False  # DGM says it's 0.4, but....
else:
    # Using default astrometry matcher
    for ff in "griz":
        config.calibrate.refObjLoader.filterMap["SDSS" + ff.upper()] = ff

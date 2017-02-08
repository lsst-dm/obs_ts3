from lsst.obs.monocam import MonocamIsrTask
config.isr.retarget(MonocamIsrTask)
config.dateObs = "date"
config.darkTime = None
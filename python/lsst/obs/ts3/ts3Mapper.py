#
# LSST Data Management System
# Copyright 2016 LSST Corporation.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <http://www.lsstcorp.org/LegalNotices/>.
#


import lsst.afw.image.utils as afwImageUtils
import lsst.afw.geom as afwGeom
import lsst.afw.image as afwImage
from lsst.obs.base import CameraMapper
import lsst.pex.policy as pexPolicy
from .ts3 import Ts3

__all__ = ["Ts3Mapper"]


class Ts3Mapper(CameraMapper):
    packageName = 'obs_ts3'

    def __init__(self, inputPolicy=None, **kwargs):
        policyFile = pexPolicy.DefaultPolicyFile(self.packageName, "ts3Mapper.paf", "policy")
        policy = pexPolicy.Policy(policyFile)

        CameraMapper.__init__(self, policy, policyFile.getRepositoryPath(), **kwargs)

        # Ensure each dataset type of interest knows about the full range of keys available from the registry
        keys = {'visit': int,
                'ccd': int,
                'filter': str,
                'date': str,
                'expTime': float,
                'object': str,
                'imageType': str,
                }
        for name in ("raw", "raw_amp",
                     # processCcd outputs
                     "postISRCCD", "calexp", "postISRCCD", "src", "icSrc", "srcMatch",
                     ):
            self.mappings[name].keyDict.update(keys)

        # @merlin, you should swap these out for the filters you actually intend to use.
        self.filterIdMap = {'u': 0, 'g': 1, 'r': 2, 'i': 3, 'z': 4, 'y': 5}

        # The LSST Filters from L. Jones 04/07/10
        afwImageUtils.defineFilter('u', 364.59)
        afwImageUtils.defineFilter('g', 476.31, alias=["SDSSG"])
        afwImageUtils.defineFilter('r', 619.42, alias=["SDSSR"])
        afwImageUtils.defineFilter('i', 752.06, alias=["SDSSI"])
        afwImageUtils.defineFilter('z', 866.85, alias=["SDSSZ"])
        afwImageUtils.defineFilter('y', 971.68, alias=['y4'])  # official y filter
        afwImageUtils.defineFilter('NONE', 0.0, alias=['no_filter', "OPEN"])

    def _extractDetectorName(self, dataId):
        return "0"

    def _computeCcdExposureId(self, dataId):
        """Compute the 64-bit (long) identifier for a CCD exposure.

        @param dataId (dict) Data identifier with visit
        """
        visit = dataId['visit']
        return int(visit)

    def bypass_ccdExposureId(self, datasetType, pythonType, location, dataId):
        return self._computeCcdExposureId(dataId)

    def bypass_ccdExposureId_bits(self, datasetType, pythonType, location, dataId):
        return 41

    def validate(self, dataId):
        visit = dataId.get("visit")
        if visit is not None and not isinstance(visit, int):
            dataId["visit"] = int(visit)
        return dataId

    def _setCcdExposureId(self, propertyList, dataId):
        propertyList.set("Computed_ccdExposureId", self._computeCcdExposureId(dataId))
        return propertyList

    def _makeCamera(self, policy, repositoryDir):
        """Make a camera (instance of lsst.afw.cameraGeom.Camera) describing the camera geometry
        """
        return Ts3()

    def bypass_defects(self, datasetType, pythonType, location, dataId):
        """ since we have no defects, return an empty list.  Fix this when defects exist """
        return [afwImage.DefectBase(afwGeom.Box2I(afwGeom.Point2I(x0, y0), afwGeom.Point2I(x1, y1))) for
                x0, y0, x1, y1 in (
                    # These may be hot pixels, but we'll treat them as bad until we can get more data
                    (3801, 666, 3805, 669),
                    (3934, 582, 3936, 589),
        )]

    def _defectLookup(self, dataId):
        """ This function needs to return a non-None value otherwise the mapper gives up
        on trying to find the defects.  I wanted to be able to return a list of defects constructed
        in code rather than reconstituted from persisted files, so I return a dummy value.
        """
        return "hack"

    def bypass_raw(self, datasetType, pythonType, location, dataId):
        """Read raw image with hacked metadata"""
        filename = location.getLocations()[0]
        md = self.bypass_raw_md(datasetType, pythonType, location, dataId)
        image = afwImage.DecoratedImageU(filename)
        image.setMetadata(md)
        return self.std_raw(image, dataId)

    def bypass_raw_md(self, datasetType, pythonType, location, dataId):
        """Read metadata for raw image, adding fake Wcs"""
        filename = location.getLocations()[0]
        md = afwImage.readMetadata(filename, 1)  # 1 = PHU
        return md

    bypass_raw_amp = bypass_raw
    bypass_raw_amp_md = bypass_raw_md

    def standardizeCalib(self, dataset, item, dataId):
        """Standardize a calibration image read in by the butler

        Some calibrations are stored on disk as Images instead of MaskedImages
        or Exposures.  Here, we convert it to an Exposure.

        @param dataset  Dataset type (e.g., "bias", "dark" or "flat")
        @param item  The item read by the butler
        @param dataId  The data identifier (unused, included for future flexibility)
        @return standardized Exposure
        """
        mapping = self.calibrations[dataset]
        if "MaskedImage" in mapping.python:
            exp = afwImage.makeExposure(item)
        elif "Image" in mapping.python:
            if hasattr(item, "getImage"):  # For DecoratedImageX
                item = item.getImage()
            exp = afwImage.makeExposure(afwImage.makeMaskedImage(item))
        elif "Exposure" in mapping.python:
            exp = item
        else:
            raise RuntimeError("Unrecognised python type: %s" % mapping.python)

        parent = super(CameraMapper, self)
        if hasattr(parent, "std_" + dataset):
            return getattr(parent, "std_" + dataset)(exp, dataId)
        return self._standardizeExposure(mapping, exp, dataId)

    def std_bias(self, item, dataId):
        return self.standardizeCalib("bias", item, dataId)

    def std_dark(self, item, dataId):
        exp = self.standardizeCalib("dark", item, dataId)
        exp.getCalib().setExptime(1.0)
        return exp

    def std_flat(self, item, dataId):
        return self.standardizeCalib("flat", item, dataId)

    def std_fringe(self, item, dataId):
        return self.standardizeCalib("flat", item, dataId)

"""Common functionality for backends."""

import abc
import os
import os.path
import annif


class AnnifBackend(metaclass=abc.ABCMeta):
    """Base class for Annif backends that perform analysis. The
    non-implemented methods should be overridden in subclasses."""

    name = None

    def __init__(self, backend_id, config):
        """Initialize backend with a specific configuration. The
        configuration is a dict. Keys and values depend on the specific
        backend type."""
        self.backend_id = backend_id
        self.config = config
        self._datadir = None

    def _get_datadir(self):
        """return the path of the directory where this backend can store its
        data files"""
        if self._datadir is None:
            self._datadir = os.path.join(
                annif.cxapp.app.config['DATADIR'],
                'backends',
                self.backend_id)
            if not os.path.exists(self._datadir):
                os.makedirs(self._datadir)
        return self._datadir

    @abc.abstractmethod
    def analyze(self, text):
        """Analyze some input text and return a list of subjects represented
        as a list of AnalysisHit objects."""
        pass

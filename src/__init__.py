"""
Tennis Performance Analysis - Source Package
Modular structure for data analysis, feature engineering, and visualization.
"""

__version__ = "0.1.0"
__author__ = "Humphrey"

# Import main modules for easier access
from . import config
from . import dataset
from . import features
from . import utils
from . import plots
from . import constants

__all__ = [
    "config",
    "dataset",
    "features",
    "utils",
    "plots",
    "constants",
]

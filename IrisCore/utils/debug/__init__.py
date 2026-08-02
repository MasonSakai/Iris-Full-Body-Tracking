
    
from config import Config
Debug_ConfigClass: Config = None

def LoadConfig(config_class: Config):
    from utils import debug
    debug.Debug_ConfigClass = config_class

    from utils.debug import DebugViewSettings
    DebugViewSettings.logLoadLevel = config_class.logLoadLevel if hasattr(config_class, 'logLoadLevel') else DebugViewSettings.logLoadLevel
    DebugViewSettings.ScribeDebugLoadIDs = config_class.ScribeDebugLoadIDs if hasattr(config_class, 'ScribeDebugLoadIDs') else DebugViewSettings.ScribeDebugLoadIDs
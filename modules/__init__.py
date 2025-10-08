"""
Inventory Manager Modules
Version: 2.2.0
Developer: Nemanja Komadina
"""

__version__ = "2.2.0"
__app_name__ = "Inventory Manager"
__developer__ = "Nemanja Komadina"

# Global translator instance
_translator = None

def get_translator():
    """Get the global translator instance."""
    global _translator
    if _translator is None:
        from .translations import Translations
        _translator = Translations()
    return _translator

def set_language(language):
    """Set the application language."""
    translator = get_translator()
    return translator.set_language(language)

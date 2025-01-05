from pathlib import Path
import tomli
from typing import Any, Dict, Optional


class Settings:
    """
    A singleton settings class that loads configuration from a TOML file.
    Default settings can be overwritten by values from the TOML file.
    """
    _instance: Optional['Settings'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'Settings':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not Settings._initialized:
            # Default settings
            self._settings: Dict[str, Any] = {
                "app": {
                    "name": "MyApp",
                    "version": "1.0.0",
                    "debug": False
                },
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "name": "myapp_db",
                    "user": "admin",
                    "password": None,
                    "max_connections": 10
                },
                "logging": {
                    "level": "INFO",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "file": "app.log"
                },
                "api": {
                    "host": "0.0.0.0",
                    "port": 8000,
                    "workers": 4,
                    "timeout": 30
                }
            }
            Settings._initialized = True
    
    def load_from_toml(self, file_path: str | Path) -> None:
        """
        Load settings from a TOML file, overwriting default values.
        
        Args:
            file_path: Path to the TOML configuration file
        
        Raises:
            FileNotFoundError: If the TOML file doesn't exist
            tomli.TOMLDecodeError: If the TOML file is invalid
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, "rb") as f:
            toml_settings = tomli.load(f)
        
        # Deep update of settings
        self._deep_update(self._settings, toml_settings)
    
    def _deep_update(self, target: Dict, source: Dict) -> None:
        """
        Recursively update a nested dictionary with values from another dictionary.
        
        Args:
            target: The dictionary to update
            source: The dictionary containing new values
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a setting value by section and key.
        
        Args:
            section: The settings section name
            key: The setting key
            default: Default value if the setting doesn't exist
        
        Returns:
            The setting value or the default value if not found
        """
        return self._settings.get(section, {}).get(key, default)
    
    def __getitem__(self, key: str) -> Dict[str, Any]:
        """
        Get an entire section of settings.
        
        Args:
            key: The section name
        
        Returns:
            Dictionary containing all settings in the specified section
        
        Raises:
            KeyError: If the section doesn't exist
        """
        if key not in self._settings:
            raise KeyError(f"Settings section '{key}' not found")
        return self._settings[key]
    
    @property
    def sections(self) -> list[str]:
        """Get a list of all available settings sections."""
        return list(self._settings.keys())
    
    def __repr__(self) -> str:
        """Return a string representation of the settings."""
        return f"Settings(sections={self.sections})"
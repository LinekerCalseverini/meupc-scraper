"""
Defines the ConfigLoader interface
"""

from abc import ABC, abstractmethod

from infrastructure.config.settings import Config


class ConfigLoader(ABC):
    """
    Defines the ConfigLoader interface
    """

    @abstractmethod
    async def load(self) -> Config:
        """
        Loads configuration
        """

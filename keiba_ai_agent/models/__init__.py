from .entry import EntryFeature
from .feature import Feature
from .horse import HorseFeature
from .race import RaceFeature

__all__ = ["Feature", "HorseFeature", "RaceFeature", "EntryFeature", "FeatureRepository"]


def __getattr__(name: str):
    if name == "FeatureRepository":
        from keiba_ai_agent.database.feature_repository import FeatureRepository

        return FeatureRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

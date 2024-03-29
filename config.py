"""Settings definitions."""
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[".secrets.toml", "settings.toml"],
)

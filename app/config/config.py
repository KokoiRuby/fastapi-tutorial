import glob
from dynaconf import Dynaconf  # type: ignore
from pathlib import Path

# root dir is /app/config
ROOT_DIR = Path(__file__).parent
# print(ROOT_DIR)

# controls which symbols should be exported when from 'module import *' is used
__all__ = ("config", )


# find all files given a filepath pattern
def read_files(filepath: str) -> list:
    return glob.glob(filepath, root_dir=ROOT_DIR)


# read all yaml files in the default dir
# confs = read_files("default/*.yaml")
confs = read_files("default/*.toml")

config = Dynaconf(
    settings_files=confs,
    # core_loaders=["YAML"],  # yaml as the config file format
    core_loaders=["TOML"],  # toml as the config file format
    load_dotenv=True,  # enable loading .env file
    root_path=ROOT_DIR,  # /app/config
)

# print(config.app)

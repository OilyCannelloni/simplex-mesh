from pathlib import Path

import yaml

config = yaml.safe_load(open(Path(__file__).parent.joinpath("config.yaml"), "r"))

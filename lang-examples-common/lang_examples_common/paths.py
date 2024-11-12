from pathlib import Path
from posixpath import expanduser

DATA_DIR = Path(__file__).parent / ".." / "data"
ENV_PATH = Path(expanduser("~")) / "code" / ".env.private"

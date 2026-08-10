"""Entry point for the planner."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from nrplanner.app import main

if __name__ == "__main__":
    sys.exit(main())

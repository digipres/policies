"""Convert Runner takes an input file and converts it into something
that can easily published on GitHub, i.e. a new README.md which provides
default documentation on GitHub and can also be published on GitHub
pages.
"""
import logging
import sys
from typing import Final

from convert_to_md import main

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

try:
    FILE_TO_READ: Final[str] = sys.argv[1]
except IndexError:
    print("No argument or file provided to convert_runner", file=sys.stderr)
    sys.exit(0)

doc = main(FILE_TO_READ)

# Write the results back out to README.md.
NEW_FILE: Final[str] = "README.md"
logging.info("writing README file: %s", NEW_FILE)
with open(NEW_FILE, "w", encoding="utf-8") as file_to_write:
    file_to_write.write(doc)

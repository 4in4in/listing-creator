import argparse
from io import TextIOWrapper
import logging
import os

from typing import Iterable

logger = logging.getLogger(__name__)


class ListingCreator:
    def __init__(
        self,
        root_dir: str,
        out_filename: str,
        skip_dirs: Iterable[str],
        allowed_extensions: Iterable[str],
        *,
        line_sep_char: str = "-",
        encoding: str = "utf-8",
    ) -> None:
        self.root_dir = root_dir
        self.out_filename = out_filename
        self.skip_dirs = skip_dirs
        self.allowed_extensions = allowed_extensions
        self.line_sep_char = line_sep_char
        self.encoding = encoding

    def _check_path(self, file_path: str) -> bool:
        return all(not d in file_path.split(os.sep) for d in self.skip_dirs)

    def _check_ext(self, filename: str) -> bool:
        return os.path.splitext(filename)[1] in self.allowed_extensions

    def _process_file(self, file_path: str, out_file: TextIOWrapper):
        try:
            out_file.write(os.linesep * 2 + file_path + os.linesep)
            if self.line_sep_char:
                out_file.write(self.line_sep_char * len(file_path))
            out_file.write(os.linesep)

            with open(file_path, "r", encoding=self.encoding) as file2:
                out_file.write(file2.read())
        except Exception as ex:
            logging.error("%s: PROCESSING ERROR: %s", file_path, str(ex))

    def create_listing(self):
        with open(self.out_filename, "a", encoding=self.encoding) as out_file:
            for root, _, filename in os.walk(self.root_dir):
                for filename in filename:
                    file_path = os.path.join(root, filename)
                    if all((self._check_path(file_path), self._check_ext(filename))):
                        logger.info("PROCESSING FILE: %s", file_path)
                        self._process_file(file_path, out_file)
                    else:
                        logger.debug("SKIPPED FILE: %s", file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ListingCreator",
        description="Tool for creating one text file from multiple text files",
    )

    OUT_DEFAULT = "out.txt"

    SOURCE = "source"
    OUT = "out"
    SKIP_DIRS = "skip-dir"
    ALLOW_EXT = "allow-ext"
    LOGLEVEL = "loglevel"

    parser.add_argument(
        SOURCE,
        nargs="?",
        default=os.getcwd(),
        help="path to dir to scan, defaults to current working dir",
    )
    parser.add_argument(
        "--" + OUT,
        "-o",
        default=OUT_DEFAULT,
        help=f"output filename path, defaults to {OUT_DEFAULT}",
    )
    parser.add_argument(
        "--" + SKIP_DIRS,
        "-s",
        nargs="*",
        default=[],
        help="name of dirs to skip",
    )
    parser.add_argument(
        "--" + ALLOW_EXT,
        "-a",
        nargs="*",
        default=[],
        help="extensions to skip with leading dot (ex.: .py .tsx)",
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        dest=LOGLEVEL,
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        dest=LOGLEVEL,
        const=logging.INFO,
    )

    args = parser.parse_args()

    source = getattr(args, SOURCE)
    out = getattr(args, OUT)
    skip_dirs = getattr(args, SKIP_DIRS.replace("-", "_"))
    allow_ext = getattr(args, ALLOW_EXT.replace("-", "_"))

    logging.basicConfig(level=getattr(args, LOGLEVEL))
    logger.debug("%s", args)

    ListingCreator(
        root_dir=source,
        out_filename=out,
        skip_dirs=skip_dirs,
        allowed_extensions=allow_ext,
    ).create_listing()

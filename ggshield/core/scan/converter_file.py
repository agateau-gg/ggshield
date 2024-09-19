import logging
import subprocess
from pathlib import Path
from typing import Optional

from ggshield.utils.files import url_for_path

from .scannable import Scannable


logger = logging.getLogger(__name__)


class Converter:
    def convert(self, path: Path) -> bytes:
        raise NotImplementedError

    def can_convert(self, path: Path) -> bool:
        raise NotImplementedError


class PandocConverter(Converter):
    def convert(self, path: Path) -> bytes:
        cmd = ["pandoc", str(path), "-t", "markdown"]
        logger.debug("Running %s", cmd)
        proc = subprocess.run(cmd, check=True, stdout=subprocess.PIPE)
        return proc.stdout

    def can_convert(self, path: Path) -> bool:
        return path.suffix in {".odt", ".docx"}


class PDFConverter(Converter):
    def convert(self, path: Path) -> bytes:
        cmd = ["pdftotext", str(path), "-"]
        logger.debug("Running %s", cmd)
        proc = subprocess.run(cmd, check=True, stdout=subprocess.PIPE)
        return proc.stdout.strip()

    def can_convert(self, path: Path) -> bool:
        return path.suffix in {".pdf"}


CONVERTERS = [
    PandocConverter(),
    PDFConverter(),
]


def get_converter(path: Path) -> Optional[Converter]:
    return next((x for x in CONVERTERS if x.can_convert(path)), None)


class ConverterFile(Scannable):
    def __init__(self, path: Path, converter: Converter) -> None:
        super().__init__()
        self._converter = converter
        self._path = path

    @property
    def url(self) -> str:
        return url_for_path(self._path)

    @property
    def filename(self) -> str:
        name = str(self._path)
        # Change suffix so that GitGuardian API scans the doc
        if name.endswith(".pdf"):
            name = name.removesuffix(".pdf") + "_pdf"
        return name

    @property
    def path(self) -> Path:
        return self._path

    def is_longer_than(self, max_utf8_encoded_size: int) -> bool:
        return False

    def _read_content(self) -> None:
        if self._content is None:
            utf8_content = self._converter.convert(self._path)
            self._utf8_encoded_size = len(utf8_content)
            self._content = utf8_content.decode()

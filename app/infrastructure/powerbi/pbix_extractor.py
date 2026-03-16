from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass(slots=True)
class PBIXMetadata:
    file_name: str
    file_size_bytes: int
    modified_at: datetime


class PBIXExtractor(ABC):
    @abstractmethod
    def extract_metadata(self, pbix_path: str) -> PBIXMetadata:
        raise NotImplementedError


class BasicPBIXExtractor(PBIXExtractor):
    def extract_metadata(self, pbix_path: str) -> PBIXMetadata:
        stat = os.stat(pbix_path)
        return PBIXMetadata(
            file_name=os.path.basename(pbix_path),
            file_size_bytes=stat.st_size,
            modified_at=datetime.fromtimestamp(stat.st_mtime),
        )


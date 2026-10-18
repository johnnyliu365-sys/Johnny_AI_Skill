"""Type-only contracts for the isolated committed-mainline source fixture."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Self

from pydantic import BaseModel, ConfigDict, model_validator

from library.local_orchestration.project_authority.contracts import (
    GitObservation,
    GitObservationSource,
)
from library.workflow_router.contracts import ProjectId
from library.workflow_router.git_handoff_contracts import GitBlobReadStatus
from library.workflow_router.mainline_projection import MainlineProjection
from library.workflow_router.target_document_contracts import FeatureSlug


_WINDOWS_DRIVE_PREFIX = re.compile(r"^[A-Za-z]:")


@dataclass(frozen=True, slots=True)
class TargetRelativePath:
    """A canonical slash-separated relative path with no traversal segments."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("path value must be a string")
        if not self.value or self.value.startswith("/"):
            raise ValueError("path must be non-empty and relative")
        if "\\" in self.value or _WINDOWS_DRIVE_PREFIX.match(self.value) is not None:
            raise ValueError("path must use canonical relative separators")
        segments = self.value.split("/")
        if any(segment in ("", ".", "..") for segment in segments):
            raise ValueError("path cannot contain empty or traversal segments")
        if any(unicodedata.category(character) == "Cc" for character in self.value):
            raise ValueError("path cannot contain control characters")


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        revalidate_instances="always",
        strict=True,
        str_strip_whitespace=False,
    )


class RawGitBlobReadResult(_StrictModel):
    """A single exact Git blob response; bytes exist only at the read boundary."""

    status: GitBlobReadStatus
    payload: bytes | None = None

    @model_validator(mode="after")
    def payload_matches_status(self) -> Self:
        if self.status is GitBlobReadStatus.FOUND:
            if self.payload is None:
                raise ValueError("found blob reads require raw bytes")
        elif self.payload is not None:
            raise ValueError("non-found blob reads cannot carry a payload")
        return self


class MainlineSourcePort(Protocol):
    """Read one path's raw bytes from the exact synthetic observation commit."""

    def read_blob(
        self,
        observation: GitObservation,
        artifact_ref: TargetRelativePath,
    ) -> RawGitBlobReadResult: ...


class MainlineSourceFailure(str, Enum):
    INDEX_NOT_FOUND = "INDEX_NOT_FOUND"
    INDEX_READ_UNAVAILABLE = "INDEX_READ_UNAVAILABLE"
    INDEX_SCHEMA_INVALID = "INDEX_SCHEMA_INVALID"
    INDEX_BINDING_MISMATCH = "INDEX_BINDING_MISMATCH"
    LEAF_NOT_FOUND = "LEAF_NOT_FOUND"
    LEAF_READ_UNAVAILABLE = "LEAF_READ_UNAVAILABLE"
    LEAF_DIGEST_MISMATCH = "LEAF_DIGEST_MISMATCH"
    PROJECTION_INVALID = "PROJECTION_INVALID"


class MainlineSourceScope(str, Enum):
    FIXTURE_ONLY = "FIXTURE_ONLY"


class MainlineSourceRequest(_StrictModel):
    """A fixture-only request bound to one normalized synthetic observation."""

    project_id: ProjectId
    feature: FeatureSlug
    observation: GitObservation

    @model_validator(mode="after")
    def observation_is_synthetic_worktree_head(self) -> Self:
        if self.observation.source is not GitObservationSource.WORKTREE_HEAD:
            raise ValueError("fixture requests require a synthetic WORKTREE_HEAD observation")
        return self


class MainlineSourceResult(_StrictModel):
    """Candidate metadata or one finite failure, always marked fixture-only."""

    scope: MainlineSourceScope = MainlineSourceScope.FIXTURE_ONLY
    projection: MainlineProjection | None = None
    failure: MainlineSourceFailure | None = None

    @model_validator(mode="after")
    def result_has_exactly_one_outcome(self) -> Self:
        if (self.projection is None) == (self.failure is None):
            raise ValueError("source result requires exactly one projection or failure")
        if self.scope is not MainlineSourceScope.FIXTURE_ONLY:
            raise ValueError("mainline source results are fixture-only")
        return self

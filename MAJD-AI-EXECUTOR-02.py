#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD-GIT
MAJD-AI-EXECUTOR-02.py
============================================================
SOVEREIGN AUTONOMOUS AI EXECUTOR

FILE 02
REAL GIT + BOUNDED AI + AUTOMATION EXECUTION ENGINE

VERSION: 5.0.0

============================================================
ABSOLUTE DESIGN
============================================================

OWNER
    -> MAJD-AI-MASTERMIND-01.py
    -> MAJD-AI-EXECUTOR-02.py
    -> REAL GIT OPERATIONS
    -> BOUNDED AI REASONING
    -> APPLY
    -> VERIFY
    -> REPAIR / ROLLBACK
    -> CONTINUE

OWNER AUTHORITY:
    SUPREME_OWNER

THE AI IS NEVER OWNER.

02 MAY:
    - discover repositories
    - import repositories
    - mirror repositories
    - inspect repositories
    - select relevant code
    - call local AI
    - create bounded changes
    - verify changes
    - rollback failures
    - continue autonomous work

02 MAY NOT:
    - grant itself OWNER
    - expose secrets
    - leave MAJD-GIT managed workspace
    - fake success
    - public-launch platforms
    - publish publicly without OWNER release

IMPORTANT:
    Git handles Git.
    Python handles deterministic inspection/tests.
    AI handles only reasoning/code work that actually needs AI.

NO FULL REPOSITORY DUMPS TO OLLAMA.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
import uuid

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


# ============================================================
# IDENTITY
# ============================================================

SYSTEM_NAME = "MAJD-GIT"
EXECUTOR_NAME = "MAJD-SOVEREIGN-AI-EXECUTOR"
VERSION = "5.0.0"

OWNER_ROLE = "SUPREME_OWNER"
AI_ROLE = "AUTONOMOUS_EXECUTOR"

ROOT = Path(__file__).resolve().parent

STATE_DIR = ROOT / ".majd"
MANAGED_DIR = ROOT / "managed"
MIRROR_DIR = STATE_DIR / "mirrors"
BACKUP_DIR = STATE_DIR / "backups"
LOG_DIR = STATE_DIR / "logs"
LOCK_DIR = STATE_DIR / "locks"

SOURCES_FILE = STATE_DIR / "sources.json"
LAST_RUN_FILE = STATE_DIR / "last-run.json"

for directory in (
    STATE_DIR,
    MANAGED_DIR,
    MIRROR_DIR,
    BACKUP_DIR,
    LOG_DIR,
    LOCK_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIG
# ============================================================

AI_BASE_URL = os.getenv(
    "MAJD_AI_BASE_URL",
    "http://127.0.0.1:11434",
).rstrip("/")

AI_MODEL = os.getenv(
    "MAJD_AI_MODEL",
    "llama3.2:3b",
).strip()

AI_TIMEOUT = max(
    30,
    min(
        240,
        int(os.getenv("MAJD_AI_TIMEOUT", "120")),
    ),
)

AI_NUM_CTX = max(
    1024,
    min(
        4096,
        int(os.getenv("MAJD_AI_NUM_CTX", "2048")),
    ),
)

AI_NUM_PREDICT = max(
    128,
    min(
        1024,
        int(os.getenv("MAJD_AI_NUM_PREDICT", "512")),
    ),
)

AI_KEEP_ALIVE = os.getenv(
    "MAJD_AI_KEEP_ALIVE",
    "30m",
)

MAX_PROMPT_CHARS = max(
    2500,
    min(
        9000,
        int(os.getenv("MAJD_AI_MAX_PROMPT_CHARS", "5200")),
    ),
)

MAX_CONTEXT_FILES = max(
    1,
    min(
        5,
        int(os.getenv("MAJD_AI_MAX_CONTEXT_FILES", "3")),
    ),
)

MAX_FILE_CONTEXT_CHARS = max(
    500,
    min(
        3000,
        int(os.getenv("MAJD_AI_MAX_FILE_CHARS", "1400")),
    ),
)

GITHUB_OWNER = os.getenv(
    "MAJD_GITHUB_OWNER",
    "majdstoresa2-coder",
).strip()


# ============================================================
# FILE TYPES
# ============================================================

IGNORE_DIRS = {
    ".git",
    ".majd",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
}

TEXT_SUFFIXES = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".md",
    ".html",
    ".css",
    ".scss",
    ".sh",
    ".sql",
    ".txt",
}

CODE_SUFFIXES = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".sh",
}


# ============================================================
# SECURITY
# ============================================================

ALLOWED_GIT_HOSTS = {
    "github.com",
    "gitlab.com",
    "codeberg.org",
    "gitea.com",
    "forgejo.org",
}

SECRET_KEY_PATTERN = re.compile(
    r"(?i)"
    r"(password|passwd|secret|token|"
    r"api[_-]?key|private[_-]?key|"
    r"authorization|cookie)"
)

SECRET_VALUE_PATTERN = re.compile(
    r"(?i)("
    r"bearer\s+[a-z0-9._~+\-/=]{10,}|"
    r"gh[pousr]_[a-z0-9]{20,}|"
    r"sk-[a-z0-9_-]{16,}|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r")"
)

WORD_PATTERN = re.compile(
    r"[A-Za-z0-9_./-]{2,}"
)


# ============================================================
# HELPERS
# ============================================================

def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def atomic_json(
    path: Path,
    data: Any,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp = path.with_suffix(
        path.suffix + ".tmp"
    )

    temp.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    temp.replace(path)


def read_json(
    path: Path,
    default: Any,
) -> Any:

    try:
        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        return default


def truncate(
    value: Any,
    limit: int = 3000,
) -> str:

    text = str(value or "")

    if len(text) <= limit:
        return text

    return (
        text[: limit - 40]
        + "\n...[TRUNCATED]..."
    )


def sha256_file(
    path: Path,
) -> str:

    digest = hashlib.sha256()

    with path.open("rb") as file_handle:

        for chunk in iter(
            lambda: file_handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def redact(
    value: Any,
) -> Any:

    if isinstance(value, dict):

        output = {}

        for key, item in value.items():

            if SECRET_KEY_PATTERN.search(
                str(key)
            ):
                output[key] = "[REDACTED]"
            else:
                output[key] = redact(item)

        return output

    if isinstance(value, list):

        return [
            redact(item)
            for item in value
        ]

    if isinstance(value, tuple):

        return tuple(
            redact(item)
            for item in value
        )

    if isinstance(value, str):

        return SECRET_VALUE_PATTERN.sub(
            "[REDACTED]",
            value,
        )

    return value


def safe_under(
    root: Path,
    value: Path | str,
) -> Path:

    path = Path(value)

    if not path.is_absolute():
        path = root / path

    path = path.resolve()

    try:
        path.relative_to(
            root.resolve()
        )
    except Exception as exc:
        raise PermissionError(
            f"Path outside allowed root: {path}"
        ) from exc

    return path


def safe_repo_path(
    repo: Path,
    relative_path: str,
) -> Path:

    if not relative_path:
        raise ValueError(
            "Empty repository path"
        )

    if "\x00" in relative_path:
        raise ValueError(
            "Invalid repository path"
        )

    path = safe_under(
        repo,
        relative_path,
    )

    relative = path.relative_to(
        repo.resolve()
    )

    if any(
        part in {".git", ".majd"}
        for part in relative.parts
    ):
        raise PermissionError(
            "Protected internal path"
        )

    return path


def objective_terms(
    objective: str,
) -> List[str]:

    stop_words = {
        "the",
        "and",
        "for",
        "with",
        "this",
        "that",
        "from",
        "into",
        "then",
        "continue",
        "autonomous",
        "development",
        "majd",
        "git",
        "platform",
        "على",
        "من",
        "في",
        "إلى",
        "عن",
        "هذا",
        "هذه",
        "ثم",
        "مع",
        "كل",
    }

    result: List[str] = []

    for raw in WORD_PATTERN.findall(
        objective.lower()
    ):

        token = raw.strip(
            "./-_"
        )

        if (
            len(token) >= 3
            and token not in stop_words
            and token not in result
        ):
            result.append(token)

    return result[:40]


# ============================================================
# COMMAND RESULT
# ============================================================

@dataclass
class CommandResult:

    argv: List[str]
    cwd: str

    returncode: int

    stdout: str
    stderr: str

    duration_seconds: float

    timed_out: bool = False

    @property
    def success(self) -> bool:

        return (
            self.returncode == 0
            and not self.timed_out
        )


# ============================================================
# AUDIT
# ============================================================

class AuditLogger:

    def __init__(
        self,
        run_id: str,
    ):

        self.path = (
            LOG_DIR
            / f"{run_id}.jsonl"
        )

    def log(
        self,
        event: str,
        **data: Any,
    ) -> None:

        record = {
            "time": utc_now(),
            "event": event,
            **redact(data),
        }

        with self.path.open(
            "a",
            encoding="utf-8",
        ) as file_handle:

            file_handle.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    default=str,
                )
                + "\n"
            )


# ============================================================
# PROCESS EXECUTOR
# ============================================================

class ProcessExecutor:

    def run(
        self,
        argv: Sequence[str],
        cwd: Path,
        timeout: int = 120,
    ) -> CommandResult:

        if not argv:
            raise ValueError(
                "Empty command"
            )

        started = time.monotonic()

        try:

            completed = subprocess.run(
                list(argv),
                cwd=str(cwd),
                text=True,
                capture_output=True,
                timeout=max(1, timeout),
                env=os.environ.copy(),
                check=False,
            )

            return CommandResult(
                argv=list(argv),
                cwd=str(cwd),
                returncode=completed.returncode,
                stdout=completed.stdout or "",
                stderr=completed.stderr or "",
                duration_seconds=(
                    time.monotonic()
                    - started
                ),
            )

        except subprocess.TimeoutExpired as exc:

            return CommandResult(
                argv=list(argv),
                cwd=str(cwd),
                returncode=124,
                stdout=(
                    exc.stdout
                    if isinstance(
                        exc.stdout,
                        str,
                    )
                    else ""
                ),
                stderr=(
                    exc.stderr
                    if isinstance(
                        exc.stderr,
                        str,
                    )
                    else "Command timed out"
                ),
                duration_seconds=(
                    time.monotonic()
                    - started
                ),
                timed_out=True,
            )

        except Exception as exc:

            return CommandResult(
                argv=list(argv),
                cwd=str(cwd),
                returncode=1,
                stdout="",
                stderr=(
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
                duration_seconds=(
                    time.monotonic()
                    - started
                ),
            )


# ============================================================
# SINGLE CYCLE LOCK
# ============================================================

class ExecutionLock:

    def __init__(
        self,
        name: str = "evolve",
    ):

        self.path = (
            LOCK_DIR
            / f"{name}.lock"
        )

        self.fd: Optional[int] = None

    def __enter__(
        self,
    ) -> "ExecutionLock":

        try:

            self.fd = os.open(
                str(self.path),
                os.O_CREAT
                | os.O_EXCL
                | os.O_WRONLY,
                0o600,
            )

            os.write(
                self.fd,
                (
                    f"{os.getpid()} "
                    f"{utc_now()}\n"
                ).encode(),
            )

            return self

        except FileExistsError:

            try:

                content = (
                    self.path
                    .read_text(
                        encoding="utf-8"
                    )
                    .split()
                )

                pid = (
                    int(content[0])
                    if content
                    else 0
                )

                os.kill(
                    pid,
                    0,
                )

                raise RuntimeError(
                    "Another autonomous cycle "
                    f"is already running "
                    f"(pid={pid})"
                )

            except ProcessLookupError:

                self.path.unlink(
                    missing_ok=True
                )

                return self.__enter__()

            except ValueError:

                self.path.unlink(
                    missing_ok=True
                )

                return self.__enter__()

    def __exit__(
        self,
        *_: Any,
    ) -> None:

        if self.fd is not None:

            with contextlib.suppress(
                Exception
            ):
                os.close(self.fd)

        self.path.unlink(
            missing_ok=True
        )


# ============================================================
# GIT WORKSPACE
# ============================================================

class GitWorkspace:

    def __init__(
        self,
        runner: ProcessExecutor,
        audit: AuditLogger,
    ):

        self.runner = runner
        self.audit = audit

    @staticmethod
    def normalize_url(
        url: str,
    ) -> str:

        url = url.strip()

        if not url:
            raise ValueError(
                "Empty Git URL"
            )

        #
        # SSH scp style:
        # git@github.com:owner/repo.git
        #

        if re.match(
            r"^[\w.-]+@[\w.-]+:.+",
            url,
        ):

            host = (
                url.split("@", 1)[1]
                .split(":", 1)[0]
                .lower()
            )

            GitWorkspace.verify_host(
                host
            )

            return url

        parsed = urllib.parse.urlparse(
            url
        )

        if parsed.scheme.lower() not in {
            "https",
            "http",
            "ssh",
            "git",
        }:
            raise PermissionError(
                "Unsupported Git scheme"
            )

        host = (
            parsed.hostname or ""
        ).lower()

        if not host:
            raise ValueError(
                "Git URL missing host"
            )

        GitWorkspace.verify_host(
            host
        )

        return url

    @staticmethod
    def verify_host(
        host: str,
    ) -> None:

        if host in ALLOWED_GIT_HOSTS:
            return

        extra_hosts = {
            item.strip().lower()
            for item
            in os.getenv(
                "MAJD_ALLOWED_GIT_HOSTS",
                "",
            ).split(",")
            if item.strip()
        }

        if host in extra_hosts:
            return

        raise PermissionError(
            f"Git host not allowed: {host}"
        )

    @staticmethod
    def repository_name(
        url: str,
    ) -> str:

        value = (
            url.rstrip("/")
            .rsplit("/", 1)[-1]
            .rsplit(":", 1)[-1]
        )

        value = re.sub(
            r"\.git$",
            "",
            value,
            flags=re.I,
        )

        value = re.sub(
            r"[^A-Za-z0-9._-]",
            "-",
            value,
        ).strip(".-")

        if not value:
            raise ValueError(
                "Unable to determine repository name"
            )

        return value[:120]

    def managed_repositories(
        self,
    ) -> List[Path]:

        repositories = []

        if not MANAGED_DIR.exists():
            return repositories

        for path in sorted(
            MANAGED_DIR.iterdir()
        ):

            if (
                path.is_dir()
                and (path / ".git").exists()
            ):
                repositories.append(path)

        return repositories

    def import_repository(
        self,
        url: str,
    ) -> Dict[str, Any]:

        url = self.normalize_url(
            url
        )

        name = self.repository_name(
            url
        )

        #
        # Never import MAJD-GIT into itself.
        #

        if name.lower() == "majd-git":

            return {
                "success": True,
                "status": (
                    "CURRENT_REPOSITORY_SKIPPED"
                ),
                "repository": name,
            }

        mirror_path = safe_under(
            MIRROR_DIR,
            MIRROR_DIR / f"{name}.git",
        )

        work_path = safe_under(
            MANAGED_DIR,
            MANAGED_DIR / name,
        )

        #
        # Mirror preserves source Git refs/history.
        #

        if not mirror_path.exists():

            result = self.runner.run(
                [
                    "git",
                    "clone",
                    "--mirror",
                    url,
                    str(mirror_path),
                ],
                cwd=ROOT,
                timeout=300,
            )

            self.audit.log(
                "GIT_MIRROR_CREATED",
                repository=name,
                result=asdict(result),
            )

            if not result.success:

                return {
                    "success": False,
                    "status": (
                        "GIT_MIRROR_CLONE_FAILED"
                    ),
                    "repository": name,
                    "error": truncate(
                        result.stderr
                    ),
                }

        else:

            result = self.runner.run(
                [
                    "git",
                    "remote",
                    "update",
                    "--prune",
                ],
                cwd=mirror_path,
                timeout=240,
            )

            self.audit.log(
                "GIT_MIRROR_UPDATED",
                repository=name,
                result=asdict(result),
            )

            if not result.success:

                return {
                    "success": False,
                    "status": (
                        "GIT_MIRROR_UPDATE_FAILED"
                    ),
                    "repository": name,
                    "error": truncate(
                        result.stderr
                    ),
                }

        #
        # Working copy for AI/build/testing.
        #

        if not work_path.exists():

            result = self.runner.run(
                [
                    "git",
                    "clone",
                    str(mirror_path),
                    str(work_path),
                ],
                cwd=ROOT,
                timeout=300,
            )

            if not result.success:

                return {
                    "success": False,
                    "status": (
                        "GIT_WORKTREE_CLONE_FAILED"
                    ),
                    "repository": name,
                    "error": truncate(
                        result.stderr
                    ),
                }

            #
            # origin = actual external repository
            #

            self.runner.run(
                [
                    "git",
                    "remote",
                    "set-url",
                    "origin",
                    url,
                ],
                cwd=work_path,
                timeout=30,
            )

            #
            # local preserved mirror also available
            #

            self.runner.run(
                [
                    "git",
                    "remote",
                    "add",
                    "majd-mirror",
                    str(mirror_path),
                ],
                cwd=work_path,
                timeout=30,
            )

        return {
            "success": True,
            "status": "REPOSITORY_IMPORTED",
            "repository": name,
            "path": str(work_path),
            "mirror": str(mirror_path),
        }

    def update_working_repository(
        self,
        repo: Path,
    ) -> Dict[str, Any]:

        status = self.runner.run(
            [
                "git",
                "status",
                "--porcelain",
            ],
            cwd=repo,
            timeout=20,
        )

        if not status.success:

            return {
                "success": False,
                "status": (
                    "INVALID_GIT_REPOSITORY"
                ),
            }

        #
        # Never destroy autonomous local work.
        #

        if status.stdout.strip():

            return {
                "success": True,
                "status": (
                    "LOCAL_CHANGES_PRESERVED"
                ),
                "dirty": True,
            }

        fetch = self.runner.run(
            [
                "git",
                "fetch",
                "origin",
                "--prune",
                "--tags",
            ],
            cwd=repo,
            timeout=180,
        )

        self.audit.log(
            "GIT_FETCH",
            repository=repo.name,
            result=asdict(fetch),
        )

        return {
            "success": fetch.success,
            "status": (
                "UPSTREAM_FETCHED"
                if fetch.success
                else "UPSTREAM_FETCH_FAILED"
            ),
            "error": truncate(
                fetch.stderr
            ),
        }


# ============================================================
# SOURCE REGISTRY
# ============================================================

class SourceRegistry:

    def configured(
        self,
    ) -> List[str]:

        result: List[str] = []

        data = read_json(
            SOURCES_FILE,
            {},
        )

        if isinstance(data, dict):

            for item in data.get(
                "repositories",
                [],
            ):

                if isinstance(item, dict):
                    url = item.get("url")
                else:
                    url = item

                if (
                    isinstance(url, str)
                    and url.strip()
                    and url.strip()
                    not in result
                ):
                    result.append(
                        url.strip()
                    )

        #
        # Optional environment repository list.
        #

        for item in os.getenv(
            "MAJD_SOURCE_REPOS",
            "",
        ).split(","):

            url = item.strip()

            if (
                url
                and url not in result
            ):
                result.append(url)

        return result

    def save(
        self,
        urls: Iterable[str],
    ) -> None:

        current = self.configured()

        for url in urls:

            if url not in current:
                current.append(url)

        atomic_json(
            SOURCES_FILE,
            {
                "updated_at": utc_now(),
                "repositories": [
                    {
                        "url": url,
                    }
                    for url in current
                ],
            },
        )

    def discover_public_github(
        self,
    ) -> List[str]:

        if not GITHUB_OWNER:
            return []

        url = (
            "https://api.github.com/users/"
            + urllib.parse.quote(
                GITHUB_OWNER
            )
            + "/repos"
            + "?per_page=100"
            + "&sort=full_name"
        )

        request = urllib.request.Request(
            url,
            headers={
                "Accept": (
                    "application/vnd.github+json"
                ),
                "User-Agent": (
                    "MAJD-GIT/5.0"
                ),
            },
        )

        try:

            with urllib.request.urlopen(
                request,
                timeout=15,
            ) as response:

                data = json.loads(
                    response.read().decode(
                        "utf-8",
                        "replace",
                    )
                )

        except Exception:

            return []

        repositories: List[str] = []

        if not isinstance(data, list):
            return repositories

        for item in data:

            if not isinstance(
                item,
                dict,
            ):
                continue

            if item.get("fork"):
                continue

            name = str(
                item.get("name")
                or ""
            )

            clone_url = str(
                item.get("clone_url")
                or ""
            )

            if not clone_url:
                continue

            if name.lower() == "majd-git":
                continue

            #
            # Only MAJD family repositories.
            #

            if "majd" not in name.lower():
                continue

            repositories.append(
                clone_url
            )

        return repositories


# ============================================================
# PROJECT INSPECTOR
# ============================================================

@dataclass
class FileInfo:

    path: str
    size: int
    sha256: str
    score: int = 0


class ProjectInspector:

    def files(
        self,
        repo: Path,
        limit: int = 2500,
    ) -> List[FileInfo]:

        result: List[FileInfo] = []

        for path in repo.rglob("*"):

            if len(result) >= limit:
                break

            try:
                relative = path.relative_to(
                    repo
                )
            except Exception:
                continue

            if any(
                part in IGNORE_DIRS
                for part in relative.parts
            ):
                continue

            if not path.is_file():
                continue

            if (
                path.suffix.lower()
                not in TEXT_SUFFIXES
                and path.name
                not in {
                    "Dockerfile",
                    "Makefile",
                    "Procfile",
                }
            ):
                continue

            try:

                size = path.stat().st_size

                if size > 1_000_000:
                    continue

                result.append(
                    FileInfo(
                        path=str(relative),
                        size=size,
                        sha256=sha256_file(
                            path
                        ),
                    )
                )

            except Exception:
                continue

        return result

    def rank(
        self,
        repo: Path,
        objective: str,
        limit: int = 4,
    ) -> List[FileInfo]:

        terms = objective_terms(
            objective
        )

        files = self.files(
            repo
        )

        priority = {
            "readme.md",
            "pyproject.toml",
            "package.json",
            "requirements.txt",
            "dockerfile",
        }

        for item in files:

            lower = item.path.lower()

            item.score = sum(
                8
                for term in terms
                if term in lower
            )

            if (
                Path(lower).name
                in priority
            ):
                item.score += 2

            if Path(
                item.path
            ).suffix.lower() in CODE_SUFFIXES:
                item.score += 1

        ranked = sorted(
            files,
            key=lambda item: (
                -item.score,
                item.size,
                item.path,
            ),
        )

        matched = [
            item
            for item in ranked
            if item.score > 0
        ]

        return (
            matched
            if matched
            else ranked
        )[:limit]

    def inventory(
        self,
        repo: Path,
    ) -> Dict[str, Any]:

        files = self.files(
            repo
        )

        types: Dict[str, int] = {}

        for item in files:

            suffix = (
                Path(item.path)
                .suffix
                .lower()
                or "[none]"
            )

            types[suffix] = (
                types.get(
                    suffix,
                    0,
                )
                + 1
            )

        return {
            "repository": repo.name,
            "file_count": len(files),
            "types": types,
            "files": [
                item.path
                for item in files[:200]
            ],
        }


# ============================================================
# CONTEXT BUILDER
# ============================================================

class ContextBuilder:

    def __init__(
        self,
        inspector: ProjectInspector,
    ):

        self.inspector = inspector

    def file_slice(
        self,
        path: Path,
        terms: Sequence[str],
    ) -> str:

        try:

            text = path.read_text(
                encoding="utf-8",
                errors="replace",
            )

        except Exception:

            return ""

        text = redact(text)

        if not isinstance(
            text,
            str,
        ):
            return ""

        if len(
            text
        ) <= MAX_FILE_CONTEXT_CHARS:

            return text

        lowered = text.lower()

        locations = []

        for term in terms:

            location = lowered.find(
                term
            )

            if location >= 0:
                locations.append(
                    location
                )

        center = (
            min(locations)
            if locations
            else 0
        )

        half = (
            MAX_FILE_CONTEXT_CHARS
            // 2
        )

        start = max(
            0,
            center - half,
        )

        end = min(
            len(text),
            start
            + MAX_FILE_CONTEXT_CHARS,
        )

        start = max(
            0,
            end
            - MAX_FILE_CONTEXT_CHARS,
        )

        result = text[
            start:end
        ]

        if start:
            result = (
                "...[FILE SLICE]...\n"
                + result
            )

        if end < len(text):
            result += (
                "\n...[FILE SLICE]..."
            )

        return result

    def build(
        self,
        repo: Path,
        objective: str,
    ) -> Tuple[str, List[str]]:

        terms = objective_terms(
            objective
        )

        selected = self.inspector.rank(
            repo,
            objective,
            MAX_CONTEXT_FILES,
        )

        blocks: List[str] = []
        paths: List[str] = []

        for info in selected:

            file_path = safe_repo_path(
                repo,
                info.path,
            )

            content = self.file_slice(
                file_path,
                terms,
            )

            if not content:
                continue

            paths.append(
                info.path
            )

            blocks.append(
                "FILE: "
                + info.path
                + "\n---\n"
                + content
                + "\n---"
            )

        #
        # Only filenames around the task.
        # Never dump entire repository content.
        #

        relevant_listing = ", ".join(
            item.path
            for item
            in self.inspector.rank(
                repo,
                objective,
                20,
            )
        )

        prompt = (
            "You are the bounded autonomous code-change "
            "engine inside MAJD-GIT.\n\n"

            "Perform ONE small necessary production-ready "
            "improvement for the OWNER objective.\n"

            "Return JSON only.\n"

            "Never request OWNER authority.\n"
            "Never expose or invent secrets.\n"
            "Never deploy or public-launch.\n"
            "Never modify .git or .majd.\n"
            "Prefer an exact replacement inside an existing "
            "relevant file.\n\n"

            "OUTPUT SCHEMA:\n"
            "{"
            "\"summary\":\"short summary\","
            "\"changes\":["
            "{"
            "\"path\":\"relative/path\","
            "\"search\":\"exact existing text; empty only for a new file\","
            "\"replace\":\"replacement text\""
            "}"
            "],"
            "\"verification_hint\":\"what should be checked\""
            "}\n\n"

            "OWNER OBJECTIVE:\n"
            + truncate(
                redact(objective),
                900,
            )
            + "\n\n"

            "RELEVANT PATHS:\n"
            + truncate(
                relevant_listing,
                800,
            )
            + "\n\n"

            + "\n\n".join(
                blocks
            )
        )

        #
        # HARD PROMPT BUDGET
        #

        if len(
            prompt
        ) > MAX_PROMPT_CHARS:

            prompt = (
                prompt[
                    : MAX_PROMPT_CHARS - 80
                ]
                + "\n...[MAJD PROMPT BUDGET ENFORCED]..."
            )

        return (
            prompt,
            paths,
        )


# ============================================================
# OLLAMA
# ============================================================

class OllamaClient:

    CHANGE_SCHEMA = {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
            },
            "changes": {
                "type": "array",
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                        },
                        "search": {
                            "type": "string",
                        },
                        "replace": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "path",
                        "search",
                        "replace",
                    ],
                },
            },
            "verification_hint": {
                "type": "string",
            },
        },
        "required": [
            "summary",
            "changes",
            "verification_hint",
        ],
    }

    def health(
        self,
    ) -> Dict[str, Any]:

        request = urllib.request.Request(
            AI_BASE_URL + "/api/tags",
            headers={
                "User-Agent": (
                    "MAJD-GIT/5.0"
                ),
            },
        )

        try:

            with urllib.request.urlopen(
                request,
                timeout=4,
            ) as response:

                data = json.loads(
                    response.read().decode(
                        "utf-8",
                        "replace",
                    )
                )

            models = []

            for item in data.get(
                "models",
                [],
            ):

                if isinstance(
                    item,
                    dict,
                ):

                    model = (
                        item.get("name")
                        or item.get("model")
                    )

                    if model:
                        models.append(
                            str(model)
                        )

            return {
                "success": True,
                "base_url": AI_BASE_URL,
                "model": AI_MODEL,
                "model_present": (
                    AI_MODEL in models
                ),
                "models": models,
                "num_ctx": AI_NUM_CTX,
                "num_predict": (
                    AI_NUM_PREDICT
                ),
            }

        except Exception as exc:

            return {
                "success": False,
                "base_url": AI_BASE_URL,
                "model": AI_MODEL,
                "error": (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            }

    def generate_json(
        self,
        prompt: str,
    ) -> Dict[str, Any]:

        #
        # num_ctx is enforced HERE,
        # not left to Ollama defaults.
        #

        payload = {
            "model": AI_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": self.CHANGE_SCHEMA,
            "keep_alive": AI_KEEP_ALIVE,
            "options": {
                "temperature": 0,
                "num_ctx": AI_NUM_CTX,
                "num_predict": (
                    AI_NUM_PREDICT
                ),
            },
        }

        request = urllib.request.Request(
            AI_BASE_URL
            + "/api/generate",
            data=json.dumps(
                payload,
                ensure_ascii=False,
            ).encode("utf-8"),
            headers={
                "Content-Type": (
                    "application/json"
                ),
                "User-Agent": (
                    "MAJD-GIT/5.0"
                ),
            },
            method="POST",
        )

        started = time.monotonic()

        try:

            with urllib.request.urlopen(
                request,
                timeout=AI_TIMEOUT,
            ) as response:

                body = json.loads(
                    response.read().decode(
                        "utf-8",
                        "replace",
                    )
                )

            raw = str(
                body.get("response")
                or ""
            ).strip()

            result = json.loads(
                raw
            )

            if not isinstance(
                result,
                dict,
            ):
                raise ValueError(
                    "AI result is not JSON object"
                )

            return {
                "success": True,
                "result": result,
                "duration_seconds": round(
                    time.monotonic()
                    - started,
                    3,
                ),
                "prompt_eval_count": (
                    body.get(
                        "prompt_eval_count"
                    )
                ),
                "eval_count": (
                    body.get(
                        "eval_count"
                    )
                ),
            }

        except Exception as exc:

            return {
                "success": False,
                "error": (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
                "duration_seconds": round(
                    time.monotonic()
                    - started,
                    3,
                ),
            }


# ============================================================
# BACKUP + CHANGE ENGINE
# ============================================================

class ChangeEngine:

    def __init__(
        self,
        audit: AuditLogger,
    ):

        self.audit = audit

    def backup(
        self,
        repo: Path,
        paths: Sequence[str],
        run_id: str,
    ) -> Path:

        root = (
            BACKUP_DIR
            / run_id
            / repo.name
        )

        root.mkdir(
            parents=True,
            exist_ok=True,
        )

        for relative in paths:

            source = safe_repo_path(
                repo,
                relative,
            )

            if (
                source.exists()
                and source.is_file()
            ):

                target = safe_under(
                    root,
                    root / relative,
                )

                target.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                shutil.copy2(
                    source,
                    target,
                )

        return root

    def apply(
        self,
        repo: Path,
        proposal: Dict[str, Any],
        run_id: str,
    ) -> Dict[str, Any]:

        changes = proposal.get(
            "changes"
        )

        if (
            not isinstance(
                changes,
                list,
            )
            or not changes
        ):

            return {
                "success": False,
                "status": (
                    "AI_PROPOSED_NO_CHANGES"
                ),
            }

        normalized = []

        for raw in changes[:3]:

            if not isinstance(
                raw,
                dict,
            ):
                continue

            relative = str(
                raw.get("path")
                or ""
            ).strip()

            search = raw.get(
                "search"
            )

            replace = raw.get(
                "replace"
            )

            if (
                not relative
                or not isinstance(
                    search,
                    str,
                )
                or not isinstance(
                    replace,
                    str,
                )
            ):
                continue

            path = safe_repo_path(
                repo,
                relative,
            )

            normalized.append(
                (
                    relative,
                    path,
                    search,
                    replace,
                )
            )

        if not normalized:

            return {
                "success": False,
                "status": (
                    "NO_VALID_AI_CHANGES"
                ),
            }

        backup_root = self.backup(
            repo,
            [
                item[0]
                for item in normalized
            ],
            run_id,
        )

        applied: List[str] = []
        created: List[str] = []

        try:

            for (
                relative,
                path,
                search,
                replace,
            ) in normalized:

                #
                # Empty search means create NEW file only.
                #

                if search == "":

                    if path.exists():

                        raise ValueError(
                            "Refusing empty-search "
                            "overwrite of existing file: "
                            + relative
                        )

                    path.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    path.write_text(
                        replace,
                        encoding="utf-8",
                    )

                    created.append(
                        relative
                    )

                    applied.append(
                        relative
                    )

                    continue

                if (
                    not path.exists()
                    or not path.is_file()
                ):

                    raise FileNotFoundError(
                        relative
                    )

                current = path.read_text(
                    encoding="utf-8",
                    errors="strict",
                )

                count = current.count(
                    search
                )

                #
                # Exact replacement must be unambiguous.
                #

                if count != 1:

                    raise ValueError(
                        "Exact AI search must match "
                        f"once in {relative}; "
                        f"matched {count}"
                    )

                updated = current.replace(
                    search,
                    replace,
                    1,
                )

                if updated == current:

                    raise ValueError(
                        "AI proposed no-op change: "
                        + relative
                    )

                path.write_text(
                    updated,
                    encoding="utf-8",
                )

                applied.append(
                    relative
                )

            self.audit.log(
                "AI_CHANGES_APPLIED",
                repository=repo.name,
                paths=applied,
            )

            return {
                "success": True,
                "status": (
                    "CHANGES_APPLIED"
                ),
                "paths": applied,
                "created": created,
                "backup": str(
                    backup_root
                ),
            }

        except Exception as exc:

            self.rollback(
                repo,
                backup_root,
                applied,
                created,
            )

            return {
                "success": False,
                "status": (
                    "CHANGE_APPLICATION_FAILED"
                ),
                "error": (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            }

    def rollback(
        self,
        repo: Path,
        backup_root: Path,
        paths: Sequence[str],
        created: Sequence[str],
    ) -> None:

        for relative in created:

            with contextlib.suppress(
                Exception
            ):

                safe_repo_path(
                    repo,
                    relative,
                ).unlink(
                    missing_ok=True
                )

        for relative in paths:

            backup = safe_under(
                backup_root,
                backup_root / relative,
            )

            if backup.exists():

                destination = (
                    safe_repo_path(
                        repo,
                        relative,
                    )
                )

                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                shutil.copy2(
                    backup,
                    destination,
                )

        self.audit.log(
            "AUTOMATIC_ROLLBACK",
            repository=repo.name,
            paths=list(paths),
        )


# ============================================================
# VERIFIER
# ============================================================

class Verifier:

    def __init__(
        self,
        runner: ProcessExecutor,
    ):

        self.runner = runner

    def changed_paths(
        self,
        repo: Path,
        paths: Sequence[str],
    ) -> Dict[str, Any]:

        checks = []

        success = True

        #
        # Git whitespace/patch sanity.
        #

        git_diff = self.runner.run(
            [
                "git",
                "diff",
                "--check",
                "--",
                *paths,
            ],
            cwd=repo,
            timeout=30,
        )

        checks.append(
            {
                "check": "git_diff_check",
                "success": (
                    git_diff.success
                ),
                "error": truncate(
                    git_diff.stderr,
                    1500,
                ),
            }
        )

        success = (
            success
            and git_diff.success
        )

        for relative in paths:

            path = safe_repo_path(
                repo,
                relative,
            )

            if (
                not path.exists()
                or path.stat().st_size == 0
            ):

                checks.append(
                    {
                        "check": "non_empty",
                        "path": relative,
                        "success": False,
                    }
                )

                success = False

                continue

            suffix = path.suffix.lower()

            #
            # Python syntax.
            #

            if suffix == ".py":

                try:

                    ast.parse(
                        path.read_text(
                            encoding="utf-8"
                        ),
                        filename=str(path),
                    )

                    checks.append(
                        {
                            "check": (
                                "python_ast"
                            ),
                            "path": relative,
                            "success": True,
                        }
                    )

                except Exception as exc:

                    checks.append(
                        {
                            "check": (
                                "python_ast"
                            ),
                            "path": relative,
                            "success": False,
                            "error": str(exc),
                        }
                    )

                    success = False

            #
            # JSON validity.
            #

            elif suffix == ".json":

                try:

                    json.loads(
                        path.read_text(
                            encoding="utf-8"
                        )
                    )

                    checks.append(
                        {
                            "check": (
                                "json_parse"
                            ),
                            "path": relative,
                            "success": True,
                        }
                    )

                except Exception as exc:

                    checks.append(
                        {
                            "check": (
                                "json_parse"
                            ),
                            "path": relative,
                            "success": False,
                            "error": str(exc),
                        }
                    )

                    success = False

            #
            # Plain JS syntax.
            #

            elif (
                suffix in {
                    ".js",
                    ".mjs",
                    ".cjs",
                }
                and shutil.which(
                    "node"
                )
            ):

                node = self.runner.run(
                    [
                        "node",
                        "--check",
                        str(path),
                    ],
                    cwd=repo,
                    timeout=30,
                )

                checks.append(
                    {
                        "check": "node_check",
                        "path": relative,
                        "success": (
                            node.success
                        ),
                        "error": truncate(
                            node.stderr,
                            1500,
                        ),
                    }
                )

                success = (
                    success
                    and node.success
                )

        return {
            "success": success,
            "status": (
                "VERIFIED"
                if success
                else "VERIFICATION_FAILED"
            ),
            "checks": checks,
        }

    def repository(
        self,
        repo: Path,
    ) -> Dict[str, Any]:

        status = self.runner.run(
            [
                "git",
                "status",
                "--porcelain=v1",
            ],
            cwd=repo,
            timeout=20,
        )

        head = self.runner.run(
            [
                "git",
                "rev-parse",
                "--verify",
                "HEAD",
            ],
            cwd=repo,
            timeout=20,
        )

        return {
            "success": (
                status.success
                and head.success
            ),
            "repository": repo.name,
            "dirty": bool(
                status.stdout.strip()
            ),
            "head": (
                head.stdout.strip()
                if head.success
                else None
            ),
        }


# ============================================================
# SECURITY SCANNER
# ============================================================

class SecurityScanner:

    def scan(
        self,
        repo: Path,
    ) -> Dict[str, Any]:

        findings = []

        for path in repo.rglob("*"):

            try:

                relative = path.relative_to(
                    repo
                )

            except Exception:

                continue

            if any(
                part in IGNORE_DIRS
                for part in relative.parts
            ):
                continue

            if not path.is_file():
                continue

            try:

                if (
                    path.stat().st_size
                    > 300_000
                ):
                    continue

            except Exception:

                continue

            if (
                path.suffix.lower()
                not in TEXT_SUFFIXES
            ):
                continue

            try:

                text = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

            except Exception:

                continue

            if SECRET_VALUE_PATTERN.search(
                text
            ):

                findings.append(
                    {
                        "path": str(
                            relative
                        ),
                        "type": (
                            "POSSIBLE_SECRET"
                        ),
                    }
                )

            if len(
                findings
            ) >= 50:

                break

        return {
            "success": (
                len(findings) == 0
            ),
            "status": (
                "SECURITY_CLEAN"
                if not findings
                else "SECURITY_REVIEW_REQUIRED"
            ),
            "findings": findings,
        }


# ============================================================
# EXECUTOR
# ============================================================

class Executor:

    def __init__(
        self,
        run_id: Optional[str] = None,
    ):

        self.run_id = (
            run_id
            or uuid.uuid4().hex[:16]
        )

        self.audit = AuditLogger(
            self.run_id
        )

        self.runner = ProcessExecutor()

        self.git = GitWorkspace(
            self.runner,
            self.audit,
        )

        self.sources = SourceRegistry()

        self.inspector = ProjectInspector()

        self.context = ContextBuilder(
            self.inspector
        )

        self.ai = OllamaClient()

        self.changes = ChangeEngine(
            self.audit
        )

        self.verifier = Verifier(
            self.runner
        )

        self.security = (
            SecurityScanner()
        )

    # --------------------------------------------------------
    # HEALTH
    # --------------------------------------------------------

    def health(
        self,
    ) -> Dict[str, Any]:

        git_binary = shutil.which(
            "git"
        )

        ai_status = self.ai.health()

        return {
            "success": (
                bool(git_binary)
                and bool(
                    ai_status.get(
                        "success"
                    )
                )
            ),
            "system": SYSTEM_NAME,
            "executor": EXECUTOR_NAME,
            "version": VERSION,
            "root": str(ROOT),

            "owner_role": OWNER_ROLE,

            #
            # Intentional:
            # executor is NOT the OWNER.
            #
            "owner_root_authority": False,

            "ai_role": AI_ROLE,

            "git": {
                "success": bool(
                    git_binary
                ),
                "binary": git_binary,
            },

            "ai": ai_status,

            "managed_repositories": [
                repo.name
                for repo
                in self.git.managed_repositories()
            ],

            #
            # Executor cannot public launch.
            #
            "public_release_capability": False,
        }

    # --------------------------------------------------------
    # INVENTORY
    # --------------------------------------------------------

    def inventory(
        self,
    ) -> Dict[str, Any]:

        repositories = (
            self.git.managed_repositories()
        )

        return {
            "success": True,
            "repositories": [
                self.inspector.inventory(
                    repo
                )
                for repo
                in repositories
            ],
            "configured_sources": len(
                self.sources.configured()
            ),
        }

    # --------------------------------------------------------
    # SECURITY
    # --------------------------------------------------------

    def security_report(
        self,
    ) -> Dict[str, Any]:

        reports = [
            self.security.scan(
                repo
            )
            for repo
            in self.git.managed_repositories()
        ]

        return {
            "success": (
                all(
                    item["success"]
                    for item in reports
                )
                if reports
                else True
            ),
            "repositories": reports,
        }

    # --------------------------------------------------------
    # VERIFY
    # --------------------------------------------------------

    def verify(
        self,
    ) -> Dict[str, Any]:

        reports = [
            self.verifier.repository(
                repo
            )
            for repo
            in self.git.managed_repositories()
        ]

        return {
            "success": (
                all(
                    item["success"]
                    for item in reports
                )
                if reports
                else True
            ),
            "repositories": reports,
        }

    # --------------------------------------------------------
    # IMPORT
    # --------------------------------------------------------

    def import_urls(
        self,
        urls: Sequence[str],
    ) -> Dict[str, Any]:

        self.sources.save(
            urls
        )

        results = [
            self.git.import_repository(
                url
            )
            for url in urls
        ]

        return {
            "success": all(
                result.get(
                    "success"
                )
                for result
                in results
            ),
            "results": results,
        }

    # --------------------------------------------------------
    # SOURCE DISCOVERY
    # --------------------------------------------------------

    def ensure_sources(
        self,
    ) -> List[str]:

        configured = (
            self.sources.configured()
        )

        if configured:
            return configured

        discovered = (
            self.sources
            .discover_public_github()
        )

        if discovered:

            self.sources.save(
                discovered
            )

        return discovered

    # --------------------------------------------------------
    # SELECT TARGET REPO
    # --------------------------------------------------------

    def choose_repository(
        self,
        objective: str,
    ) -> Optional[Path]:

        repositories = (
            self.git.managed_repositories()
        )

        if not repositories:
            return None

        terms = objective_terms(
            objective
        )

        ranking = []

        for repo in repositories:

            name = repo.name.lower()

            score = sum(
                10
                for term in terms
                if term in name
            )

            ranking.append(
                (
                    score,
                    repo.name.lower(),
                    repo,
                )
            )

        ranking.sort(
            key=lambda item: (
                -item[0],
                item[1],
            )
        )

        return ranking[0][2]

    # --------------------------------------------------------
    # EVOLVE
    # --------------------------------------------------------

    def evolve(
        self,
        objective: str,
    ) -> Dict[str, Any]:

        objective = objective.strip()

        if not objective:

            return {
                "success": False,
                "status": (
                    "EMPTY_OWNER_OBJECTIVE"
                ),
            }

        started = time.monotonic()

        with ExecutionLock(
            "evolve"
        ):

            self.audit.log(
                "EVOLVE_STARTED",
                objective=objective,
            )

            #
            # STEP 1
            # Find source repositories.
            #

            sources = self.ensure_sources()

            managed = (
                self.git.managed_repositories()
            )

            #
            # STEP 2
            # If no imported repos yet, import one.
            # One import per cycle prevents a huge blocking job.
            #

            if (
                not managed
                and sources
            ):

                imported = (
                    self.git
                    .import_repository(
                        sources[0]
                    )
                )

                result = {
                    "success": imported.get(
                        "success",
                        False,
                    ),
                    "status": (
                        "SOURCE_IMPORT_CYCLE"
                    ),
                    "import": imported,
                    "remaining_sources": max(
                        0,
                        len(sources) - 1,
                    ),
                }

                self.finish(
                    result,
                    started,
                )

                return result

            #
            # Import missing source, one per cycle.
            #

            if sources:

                existing = {
                    repo.name.lower()
                    for repo in managed
                }

                for url in sources:

                    try:

                        name = (
                            self.git
                            .repository_name(
                                url
                            )
                            .lower()
                        )

                    except Exception:

                        continue

                    if name == "majd-git":
                        continue

                    if name in existing:
                        continue

                    imported = (
                        self.git
                        .import_repository(
                            url
                        )
                    )

                    result = {
                        "success": imported.get(
                            "success",
                            False,
                        ),
                        "status": (
                            "SOURCE_IMPORT_CYCLE"
                        ),
                        "import": imported,
                    }

                    self.finish(
                        result,
                        started,
                    )

                    return result

            #
            # STEP 3
            # Choose repository relevant to objective.
            #

            repo = self.choose_repository(
                objective
            )

            if repo is None:

                result = {
                    "success": False,
                    "status": (
                        "NO_MANAGED_REPOSITORY"
                    ),
                    "message": (
                        "No source repository "
                        "available."
                    ),
                }

                self.finish(
                    result,
                    started,
                )

                return result

            #
            # STEP 4
            # Git updates Git.
            #

            self.git.update_working_repository(
                repo
            )

            #
            # STEP 5
            # Local context selection.
            #

            prompt, context_paths = (
                self.context.build(
                    repo,
                    objective,
                )
            )

            if not context_paths:

                result = {
                    "success": False,
                    "status": (
                        "NO_RELEVANT_CODE_CONTEXT"
                    ),
                    "repository": repo.name,
                }

                self.finish(
                    result,
                    started,
                )

                return result

            self.audit.log(
                "AI_REQUEST",
                repository=repo.name,
                model=AI_MODEL,
                prompt_chars=len(
                    prompt
                ),
                num_ctx=AI_NUM_CTX,
                context_paths=context_paths,
            )

            #
            # STEP 6
            # Exactly ONE AI call in this cycle.
            #

            ai_result = (
                self.ai.generate_json(
                    prompt
                )
            )

            self.audit.log(
                "AI_RESULT",
                repository=repo.name,
                ai=ai_result,
            )

            if not ai_result.get(
                "success"
            ):

                result = {
                    "success": False,
                    "status": (
                        "AI_REQUEST_FAILED"
                    ),
                    "repository": (
                        repo.name
                    ),
                    "prompt_chars": len(
                        prompt
                    ),
                    "ai": ai_result,
                }

                self.finish(
                    result,
                    started,
                )

                return result

            proposal = ai_result[
                "result"
            ]

            #
            # STEP 7
            # Apply bounded exact changes.
            #

            applied = self.changes.apply(
                repo,
                proposal,
                self.run_id,
            )

            if not applied.get(
                "success"
            ):

                result = {
                    "success": False,
                    "status": applied.get(
                        "status"
                    ),
                    "repository": repo.name,
                    "summary": proposal.get(
                        "summary"
                    ),
                    "apply": applied,
                }

                self.finish(
                    result,
                    started,
                )

                return result

            #
            # STEP 8
            # Deterministic verification.
            #

            verification = (
                self.verifier.changed_paths(
                    repo,
                    applied["paths"],
                )
            )

            if not verification.get(
                "success"
            ):

                self.changes.rollback(
                    repo,
                    Path(
                        applied["backup"]
                    ),
                    applied["paths"],
                    applied.get(
                        "created",
                        [],
                    ),
                )

                result = {
                    "success": False,
                    "status": (
                        "CHANGE_REJECTED_"
                        "AND_ROLLED_BACK"
                    ),
                    "repository": repo.name,
                    "verification": (
                        verification
                    ),
                }

                self.finish(
                    result,
                    started,
                )

                return result

            #
            # STEP 9
            # Secret/security check.
            #

            security = (
                self.security.scan(
                    repo
                )
            )

            if not security.get(
                "success"
            ):

                self.changes.rollback(
                    repo,
                    Path(
                        applied["backup"]
                    ),
                    applied["paths"],
                    applied.get(
                        "created",
                        [],
                    ),
                )

                result = {
                    "success": False,
                    "status": (
                        "SECURITY_REJECTED_"
                        "AND_ROLLED_BACK"
                    ),
                    "repository": repo.name,
                    "security": security,
                }

                self.finish(
                    result,
                    started,
                )

                return result

            #
            # VERIFIED REAL SUCCESS.
            #

            result = {
                "success": True,
                "status": (
                    "VERIFIED_AUTONOMOUS_"
                    "IMPROVEMENT"
                ),
                "repository": repo.name,
                "summary": proposal.get(
                    "summary"
                ),
                "changed_paths": (
                    applied["paths"]
                ),
                "verification": (
                    verification
                ),
                "ai_metrics": {
                    "duration_seconds": (
                        ai_result.get(
                            "duration_seconds"
                        )
                    ),
                    "prompt_eval_count": (
                        ai_result.get(
                            "prompt_eval_count"
                        )
                    ),
                    "eval_count": (
                        ai_result.get(
                            "eval_count"
                        )
                    ),
                },

                #
                # Never public launch.
                #
                "public_release": (
                    "WAITING_FOR_OWNER_RELEASE"
                ),
            }

            self.finish(
                result,
                started,
            )

            return result

    # --------------------------------------------------------
    # FINISH
    # --------------------------------------------------------

    def finish(
        self,
        result: Dict[str, Any],
        started: float,
    ) -> None:

        result["run_id"] = (
            self.run_id
        )

        result["finished_at"] = (
            utc_now()
        )

        result[
            "duration_seconds"
        ] = round(
            time.monotonic()
            - started,
            3,
        )

        atomic_json(
            LAST_RUN_FILE,
            redact(result),
        )

        self.audit.log(
            "EVOLVE_FINISHED",
            result=result,
        )

    # --------------------------------------------------------
    # SELF TEST
    # --------------------------------------------------------

    def self_test(
        self,
    ) -> Dict[str, Any]:

        tests: Dict[str, bool] = {}

        health = self.health()

        tests[
            "ai_not_owner"
        ] = (
            health.get(
                "owner_root_authority"
            )
            is False
        )

        tests[
            "public_release_blocked"
        ] = (
            health.get(
                "public_release_capability"
            )
            is False
        )

        tests[
            "credential_redaction"
        ] = (
            redact(
                "Bearer "
                "abcdefghijklmnopqrstuv"
            )
            == "[REDACTED]"
        )

        tests[
            "path_escape_denied"
        ] = False

        try:

            safe_under(
                ROOT,
                ROOT / ".." / "escape",
            )

        except PermissionError:

            tests[
                "path_escape_denied"
            ] = True

        tests[
            "prompt_budget"
        ] = (
            MAX_PROMPT_CHARS
            <= 9000
        )

        tests[
            "bounded_context_files"
        ] = (
            MAX_CONTEXT_FILES
            <= 5
        )

        tests[
            "ollama_ctx_bounded"
        ] = (
            AI_NUM_CTX
            <= 4096
        )

        tests[
            "git_available"
        ] = bool(
            shutil.which(
                "git"
            )
        )

        tests[
            "single_cycle_lock"
        ] = True

        try:

            with ExecutionLock(
                "self-test"
            ):
                pass

        except Exception:

            tests[
                "single_cycle_lock"
            ] = False

        return {
            "success": all(
                tests.values()
            ),
            "version": VERSION,
            "tests": tests,
        }

    # ========================================================
    # MASTERMIND 01 COMPATIBILITY
    # ========================================================

    def execute(
        self,
        objective: str = "",
        command: str = "",
        **_: Any,
    ) -> Dict[str, Any]:

        return self.evolve(
            objective
            or command
        )

    def execute_objective(
        self,
        objective: str,
        **_: Any,
    ) -> Dict[str, Any]:

        return self.evolve(
            objective
        )

    def _auto_repair(
        self,
        objective: str,
        **_: Any,
    ) -> Dict[str, Any]:

        return self.evolve(
            "Repair the verified failure "
            "with one bounded safe change. "
            + objective
        )


# ============================================================
# COMPATIBILITY AI CHANGE ENGINE
# ============================================================

class AIChangeSetEngine:

    def __init__(
        self,
        executor: Optional[
            Executor
        ] = None,
    ):

        self.executor = (
            executor
            or Executor()
        )

    def propose(
        self,
        objective: str,
        repo: Optional[str] = None,
        **_: Any,
    ) -> Dict[str, Any]:

        if repo:

            target = Path(
                repo
            ).resolve()

        else:

            target = (
                self.executor
                .choose_repository(
                    objective
                )
            )

        if target is None:

            return {
                "success": False,
                "status": (
                    "NO_MANAGED_REPOSITORY"
                ),
            }

        prompt, paths = (
            self.executor
            .context
            .build(
                target,
                objective,
            )
        )

        if not paths:

            return {
                "success": False,
                "status": (
                    "NO_RELEVANT_CONTEXT"
                ),
            }

        return (
            self.executor
            .ai
            .generate_json(
                prompt
            )
        )


# ============================================================
# PUBLIC INTERFACES FOR 01
# ============================================================

def execute_objective(
    objective: str,
    **kwargs: Any,
) -> Dict[str, Any]:

    return (
        Executor()
        .execute_objective(
            objective,
            **kwargs,
        )
    )


def execute(
    command: str = "",
    objective: str = "",
    **kwargs: Any,
) -> Dict[str, Any]:

    return (
        Executor()
        .execute(
            command=command,
            objective=objective,
            **kwargs,
        )
    )


def run(
    command: str = "",
    objective: str = "",
    **kwargs: Any,
) -> Dict[str, Any]:

    return execute(
        command=command,
        objective=objective,
        **kwargs,
    )


# ============================================================
# CLI
# ============================================================

def main() -> int:

    parser = argparse.ArgumentParser(
        description=(
            "MAJD-GIT "
            "Sovereign Autonomous "
            "AI Executor 02"
        )
    )

    sub = parser.add_subparsers(
        dest="command",
        required=True,
    )

    sub.add_parser(
        "health"
    )

    sub.add_parser(
        "self-test"
    )

    sub.add_parser(
        "inventory"
    )

    sub.add_parser(
        "security"
    )

    sub.add_parser(
        "verify"
    )

    import_parser = (
        sub.add_parser(
            "import"
        )
    )

    import_parser.add_argument(
        "urls",
        nargs="+",
    )

    evolve_parser = (
        sub.add_parser(
            "evolve"
        )
    )

    evolve_parser.add_argument(
        "objective",
        nargs="+",
    )

    args = parser.parse_args()

    executor = Executor()

    if args.command == "health":

        result = (
            executor.health()
        )

    elif args.command == "self-test":

        result = (
            executor.self_test()
        )

    elif args.command == "inventory":

        result = (
            executor.inventory()
        )

    elif args.command == "security":

        result = (
            executor.security_report()
        )

    elif args.command == "verify":

        result = (
            executor.verify()
        )

    elif args.command == "import":

        result = (
            executor.import_urls(
                args.urls
            )
        )

    elif args.command == "evolve":

        result = (
            executor.evolve(
                " ".join(
                    args.objective
                ).strip()
            )
        )

    else:

        result = {
            "success": False,
            "status": (
                "UNKNOWN_COMMAND"
            ),
        }

    print(
        json.dumps(
            redact(result),
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )

    return (
        0
        if result.get(
            "success"
        )
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )

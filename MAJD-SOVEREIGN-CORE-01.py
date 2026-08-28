#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
MAJD
MAJD-SOVEREIGN-CORE-01.py
===============================================================================

MAJD SOVEREIGN CORE
المجد — النواة السيادية الأساسية

This file establishes the sovereign foundation of the MAJD-GIT platform.

CORE PRINCIPLES
---------------
1. MAJD is the platform identity.
2. OWNER is the supreme authority.
3. Artificial intelligence operates under OWNER authority.
4. Routine technical operations may execute autonomously.
5. Critical owner-only actions require explicit OWNER authorization.
6. No external component receives authority over MAJD.
7. Every operation is auditable.
8. False-success reporting is prohibited.
9. Failures must be detected and reported truthfully.
10. The architecture is designed for future expansion without weakening
    OWNER authority.

This file intentionally depends only on the Python standard library.
===============================================================================
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import socket
import sys
import threading
import time
import uuid

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


# =============================================================================
# PLATFORM CONSTANTS
# =============================================================================

MAJD_NAME = "MAJD"
MAJD_PROJECT = "MAJD-GIT"
MAJD_CORE_ID = "MAJD-SOVEREIGN-CORE-01"
MAJD_VERSION = "1.0.0"
MAJD_SCHEMA_VERSION = "1"

OWNER_ROLE = "OWNER"

BASE_DIR = Path(__file__).resolve().parent
STATE_DIR = BASE_DIR / ".majd"
STATE_FILE = STATE_DIR / "core-state.json"
AUDIT_FILE = STATE_DIR / "audit.jsonl"


# =============================================================================
# TIME
# =============================================================================


def utc_now() -> str:
    """Return current UTC time in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


# =============================================================================
# ENUMS
# =============================================================================


class AuthorityLevel(str, Enum):
    OWNER = "OWNER"
    SOVEREIGN_CORE = "SOVEREIGN_CORE"
    SYSTEM = "SYSTEM"
    AGENT = "AGENT"
    SERVICE = "SERVICE"
    USER = "USER"
    GUEST = "GUEST"


class CoreStatus(str, Enum):
    CREATED = "CREATED"
    STARTING = "STARTING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    OWNER_REQUIRED = "OWNER_REQUIRED"


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# =============================================================================
# DATA MODELS
# =============================================================================


@dataclass(frozen=True)
class PlatformIdentity:
    name: str = MAJD_NAME
    project: str = MAJD_PROJECT
    core_id: str = MAJD_CORE_ID
    version: str = MAJD_VERSION
    schema_version: str = MAJD_SCHEMA_VERSION


@dataclass
class RuntimeEnvironment:
    python_version: str
    implementation: str
    operating_system: str
    architecture: str
    hostname: str
    process_id: int
    working_directory: str
    executable: str


@dataclass
class AuthorityContext:
    actor_id: str
    authority: AuthorityLevel
    authenticated: bool = False
    owner_verified: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoreRequest:
    action: str
    actor: AuthorityContext
    payload: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=utc_now)


@dataclass
class CoreResponse:
    ok: bool
    request_id: str
    decision: Decision
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=utc_now)


@dataclass
class AuditEvent:
    event_id: str
    timestamp: str
    severity: Severity
    category: str
    action: str
    actor_id: str
    authority: str
    success: bool
    details: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# JSON UTILITIES
# =============================================================================


def json_safe(value: Any) -> Any:
    """Convert supported Python values into JSON-safe values."""

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, Path):
        return str(value)

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: json_safe(item)
            for key, item in asdict(value).items()
        }

    if isinstance(value, dict):
        return {
            str(key): json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [json_safe(item) for item in value]

    return value


def canonical_json(value: Any) -> str:
    return json.dumps(
        json_safe(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()


# =============================================================================
# LOCAL STATE
# =============================================================================


class LocalStateStore:
    """
    Minimal local state store.

    Atomic replacement is used when saving state so that MAJD does not leave
    a partially written state file if the process is interrupted.
    """

    def __init__(
        self,
        state_file: Path = STATE_FILE,
        audit_file: Path = AUDIT_FILE,
    ) -> None:
        self.state_file = state_file
        self.audit_file = audit_file
        self._lock = threading.RLock()

    def initialize(self) -> None:
        with self._lock:
            self.state_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

    def load(self) -> Dict[str, Any]:
        self.initialize()

        if not self.state_file.exists():
            return {}

        try:
            with self.state_file.open(
                "r",
                encoding="utf-8",
            ) as handle:
                data = json.load(handle)

            if isinstance(data, dict):
                return data

        except (OSError, json.JSONDecodeError):
            return {}

        return {}

    def save(self, state: Dict[str, Any]) -> None:
        self.initialize()

        with self._lock:
            temp_file = self.state_file.with_suffix(".tmp")

            with temp_file.open(
                "w",
                encoding="utf-8",
            ) as handle:
                json.dump(
                    json_safe(state),
                    handle,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                handle.flush()
                os.fsync(handle.fileno())

            os.replace(temp_file, self.state_file)

    def append_audit(self, event: AuditEvent) -> None:
        self.initialize()

        with self._lock:
            with self.audit_file.open(
                "a",
                encoding="utf-8",
            ) as handle:
                handle.write(
                    canonical_json(event) + "\n"
                )
                handle.flush()


# =============================================================================
# AUDIT SYSTEM
# =============================================================================


class MajdAudit:
    def __init__(self, store: LocalStateStore) -> None:
        self.store = store

    def record(
        self,
        *,
        category: str,
        action: str,
        actor: AuthorityContext,
        success: bool,
        severity: Severity = Severity.INFO,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=utc_now(),
            severity=severity,
            category=category,
            action=action,
            actor_id=actor.actor_id,
            authority=actor.authority.value,
            success=success,
            details=details or {},
        )

        self.store.append_audit(event)

        return event


# =============================================================================
# AUTHORITY ENGINE
# =============================================================================


class MajdAuthorityEngine:
    """
    Central authority policy.

    OWNER is always the highest authority.

    The core may autonomously perform routine internal operations, but actions
    classified as owner-only cannot be approved by lower authorities.
    """

    OWNER_ONLY_ACTIONS = {
        "TRANSFER_OWNERSHIP",
        "CHANGE_OWNER_AUTHORITY",
        "DISABLE_SOVEREIGN_CORE",
        "DELETE_PLATFORM",
        "ROTATE_OWNER_ROOT_IDENTITY",
        "EXPORT_ROOT_SECRETS",
    }

    SYSTEM_ALLOWED_ACTIONS = {
        "STATUS",
        "HEALTH",
        "SELF_TEST",
        "READ_RUNTIME",
        "READ_PLATFORM_IDENTITY",
        "WRITE_AUDIT",
        "RECOVER_RUNTIME",
        "VERIFY_STATE",
    }

    def evaluate(
        self,
        request: CoreRequest,
    ) -> Decision:

        action = request.action.strip().upper()
        actor = request.actor

        if not actor.authenticated:
            if action in {
                "STATUS",
                "HEALTH",
                "READ_PLATFORM_IDENTITY",
            }:
                return Decision.ALLOW

            return Decision.DENY

        if action in self.OWNER_ONLY_ACTIONS:
            if (
                actor.authority == AuthorityLevel.OWNER
                and actor.owner_verified
            ):
                return Decision.ALLOW

            return Decision.OWNER_REQUIRED

        if actor.authority == AuthorityLevel.OWNER:
            return Decision.ALLOW

        if actor.authority in {
            AuthorityLevel.SOVEREIGN_CORE,
            AuthorityLevel.SYSTEM,
        }:
            if action in self.SYSTEM_ALLOWED_ACTIONS:
                return Decision.ALLOW

        return Decision.DENY


# =============================================================================
# SOVEREIGN CORE
# =============================================================================


class MajdSovereignCore:
    """
    First sovereign runtime component of MAJD-GIT.
    """

    def __init__(self) -> None:
        self.identity = PlatformIdentity()
        self.store = LocalStateStore()
        self.audit = MajdAudit(self.store)
        self.authority = MajdAuthorityEngine()

        self.status = CoreStatus.CREATED
        self.started_at: Optional[str] = None
        self.instance_id = str(uuid.uuid4())

        self._lock = threading.RLock()

    # -------------------------------------------------------------------------
    # ENVIRONMENT
    # -------------------------------------------------------------------------

    def runtime_environment(self) -> RuntimeEnvironment:
        return RuntimeEnvironment(
            python_version=sys.version.split()[0],
            implementation=platform.python_implementation(),
            operating_system=platform.platform(),
            architecture=platform.machine(),
            hostname=socket.gethostname(),
            process_id=os.getpid(),
            working_directory=str(Path.cwd()),
            executable=sys.executable,
        )

    # -------------------------------------------------------------------------
    # OWNER CONTEXT
    # -------------------------------------------------------------------------

    def owner_context(
        self,
        owner_id: str = "MAJD-OWNER",
        verified: bool = True,
    ) -> AuthorityContext:

        return AuthorityContext(
            actor_id=owner_id,
            authority=AuthorityLevel.OWNER,
            authenticated=True,
            owner_verified=verified,
        )

    def system_context(self) -> AuthorityContext:
        return AuthorityContext(
            actor_id=MAJD_CORE_ID,
            authority=AuthorityLevel.SOVEREIGN_CORE,
            authenticated=True,
            owner_verified=False,
        )

    # -------------------------------------------------------------------------
    # STATE
    # -------------------------------------------------------------------------

    def state_snapshot(self) -> Dict[str, Any]:

        snapshot = {
            "identity": json_safe(self.identity),
            "instance_id": self.instance_id,
            "status": self.status.value,
            "started_at": self.started_at,
            "updated_at": utc_now(),
            "runtime": json_safe(
                self.runtime_environment()
            ),
        }

        snapshot["integrity"] = sha256_json(snapshot)

        return snapshot

    def persist_state(self) -> Dict[str, Any]:
        state = self.state_snapshot()
        self.store.save(state)
        return state

    # -------------------------------------------------------------------------
    # START
    # -------------------------------------------------------------------------

    def start(self) -> Dict[str, Any]:

        with self._lock:

            if self.status == CoreStatus.READY:
                return self.state_snapshot()

            self.status = CoreStatus.STARTING

            try:
                self.store.initialize()

                self.started_at = utc_now()
                self.status = CoreStatus.READY

                state = self.persist_state()

                self.audit.record(
                    category="CORE",
                    action="START",
                    actor=self.system_context(),
                    success=True,
                    details={
                        "instance_id": self.instance_id,
                        "version": MAJD_VERSION,
                    },
                )

                return state

            except Exception as exc:
                self.status = CoreStatus.FAILED

                try:
                    self.audit.record(
                        category="CORE",
                        action="START",
                        actor=self.system_context(),
                        success=False,
                        severity=Severity.CRITICAL,
                        details={
                            "error": repr(exc),
                        },
                    )
                except Exception:
                    pass

                raise

    # -------------------------------------------------------------------------
    # HEALTH
    # -------------------------------------------------------------------------

    def health(self) -> Dict[str, Any]:

        state_exists = self.store.state_file.exists()

        return {
            "ok": self.status == CoreStatus.READY,
            "platform": MAJD_NAME,
            "project": MAJD_PROJECT,
            "core": MAJD_CORE_ID,
            "version": MAJD_VERSION,
            "status": self.status.value,
            "instance_id": self.instance_id,
            "state_storage": state_exists,
            "timestamp": utc_now(),
        }

    # -------------------------------------------------------------------------
    # SELF TEST
    # -------------------------------------------------------------------------

    def self_test(self) -> Dict[str, Any]:

        tests: List[Dict[str, Any]] = []

        def add_test(
            name: str,
            passed: bool,
            detail: str,
        ) -> None:
            tests.append(
                {
                    "name": name,
                    "passed": passed,
                    "detail": detail,
                }
            )

        add_test(
            "python",
            sys.version_info >= (3, 9),
            sys.version.split()[0],
        )

        add_test(
            "identity",
            self.identity.name == MAJD_NAME,
            self.identity.name,
        )

        add_test(
            "owner_supreme",
            AuthorityLevel.OWNER.value == OWNER_ROLE,
            OWNER_ROLE,
        )

        owner = self.owner_context()

        owner_request = CoreRequest(
            action="TRANSFER_OWNERSHIP",
            actor=owner,
        )

        owner_decision = self.authority.evaluate(
            owner_request
        )

        add_test(
            "owner_authority",
            owner_decision == Decision.ALLOW,
            owner_decision.value,
        )

        system_request = CoreRequest(
            action="TRANSFER_OWNERSHIP",
            actor=self.system_context(),
        )

        system_decision = self.authority.evaluate(
            system_request
        )

        add_test(
            "system_cannot_take_owner_action",
            system_decision == Decision.OWNER_REQUIRED,
            system_decision.value,
        )

        try:
            self.persist_state()
            storage_ok = self.store.state_file.exists()
        except Exception:
            storage_ok = False

        add_test(
            "state_storage",
            storage_ok,
            str(self.store.state_file),
        )

        passed = all(
            item["passed"]
            for item in tests
        )

        result = {
            "ok": passed,
            "tests": tests,
            "timestamp": utc_now(),
        }

        self.audit.record(
            category="CORE",
            action="SELF_TEST",
            actor=self.system_context(),
            success=passed,
            severity=(
                Severity.INFO
                if passed
                else Severity.ERROR
            ),
            details=result,
        )

        return result

    # -------------------------------------------------------------------------
    # REQUEST HANDLER
    # -------------------------------------------------------------------------

    def execute(
        self,
        request: CoreRequest,
    ) -> CoreResponse:

        decision = self.authority.evaluate(request)

        if decision != Decision.ALLOW:

            self.audit.record(
                category="AUTHORITY",
                action=request.action,
                actor=request.actor,
                success=False,
                severity=Severity.WARNING,
                details={
                    "decision": decision.value,
                    "request_id": request.request_id,
                },
            )

            return CoreResponse(
                ok=False,
                request_id=request.request_id,
                decision=decision,
                message=(
                    "OWNER authorization required."
                    if decision == Decision.OWNER_REQUIRED
                    else "Request denied."
                ),
            )

        action = request.action.strip().upper()

        try:

            if action in {
                "STATUS",
                "HEALTH",
            }:
                data = self.health()

            elif action == "SELF_TEST":
                data = self.self_test()

            elif action == "READ_RUNTIME":
                data = json_safe(
                    self.runtime_environment()
                )

            elif action == "READ_PLATFORM_IDENTITY":
                data = json_safe(
                    self.identity
                )

            elif action == "VERIFY_STATE":
                data = self.verify_state()

            else:
                return CoreResponse(
                    ok=False,
                    request_id=request.request_id,
                    decision=Decision.DENY,
                    message="Action is not implemented by Core 01.",
                    data={
                        "action": action,
                    },
                )

            self.audit.record(
                category="EXECUTION",
                action=action,
                actor=request.actor,
                success=True,
                details={
                    "request_id": request.request_id,
                },
            )

            return CoreResponse(
                ok=True,
                request_id=request.request_id,
                decision=Decision.ALLOW,
                message="Operation completed.",
                data=data,
            )

        except Exception as exc:

            self.audit.record(
                category="EXECUTION",
                action=action,
                actor=request.actor,
                success=False,
                severity=Severity.ERROR,
                details={
                    "request_id": request.request_id,
                    "error": repr(exc),
                },
            )

            return CoreResponse(
                ok=False,
                request_id=request.request_id,
                decision=Decision.ALLOW,
                message="Operation failed.",
                data={
                    "error": repr(exc),
                },
            )

    # -------------------------------------------------------------------------
    # STATE VERIFICATION
    # -------------------------------------------------------------------------

    def verify_state(self) -> Dict[str, Any]:

        state = self.store.load()

        if not state:
            return {
                "ok": False,
                "reason": "STATE_NOT_FOUND",
            }

        stored_hash = state.get("integrity")

        if not stored_hash:
            return {
                "ok": False,
                "reason": "INTEGRITY_HASH_MISSING",
            }

        candidate = dict(state)
        candidate.pop("integrity", None)

        calculated_hash = sha256_json(candidate)

        return {
            "ok": stored_hash == calculated_hash,
            "stored": stored_hash,
            "calculated": calculated_hash,
        }


# =============================================================================
# CLI
# =============================================================================


def print_json(data: Any) -> None:
    print(
        json.dumps(
            json_safe(data),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


def main() -> int:

    core = MajdSovereignCore()

    try:
        core.start()
    except Exception as exc:
        print_json(
            {
                "ok": False,
                "core": MAJD_CORE_ID,
                "error": repr(exc),
            }
        )
        return 1

    command = (
        sys.argv[1].strip().lower()
        if len(sys.argv) > 1
        else "self-test"
    )

    if command in {
        "health",
        "status",
    }:
        print_json(core.health())
        return 0 if core.health()["ok"] else 1

    if command in {
        "self-test",
        "test",
    }:
        result = core.self_test()
        print_json(result)
        return 0 if result["ok"] else 1

    if command == "state":
        print_json(core.state_snapshot())
        return 0

    if command == "verify":
        result = core.verify_state()
        print_json(result)
        return 0 if result.get("ok") else 1

    print_json(
        {
            "ok": False,
            "error": "UNKNOWN_COMMAND",
            "supported": [
                "health",
                "status",
                "self-test",
                "state",
                "verify",
            ],
        }
    )

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

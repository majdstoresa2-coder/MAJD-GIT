#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
MAJD-GIT
MAJD-AI-MASTERMIND-01.py
===============================================================================

MAJD AI SOVEREIGN MASTERMIND
العقل المدبر السيادي لمنصة MAJD-GIT

VERSION: 2.0.0

ARCHITECTURE
------------
OWNER_ROOT
    ↓
MAJD-AI-MASTERMIND-01
    ↓
MAJD-AI-EXECUTOR-02
    ↓
Git / Inspection / Verification / Repair / AI jobs when needed
    ↓
WAITING_FOR_OWNER_RELEASE

FOUNDATION RULES
----------------
1. OWNER_ROOT is permanently above AI authority.
2. 01 is the mastermind and primary orchestration entry point.
3. 02 is the execution layer and never becomes OWNER_ROOT.
4. Repository content is untrusted input.
5. Secrets are redacted from state/audit/output.
6. Cross-repository and cross-tenant access is denied by default.
7. No successful result without verification.
8. Public release is NEVER performed autonomously.
9. AI/model failure or timeout must not falsely report success.
10. Deterministic work may continue without waiting indefinitely for an LLM.
11. Executor failures are bounded; no infinite repair loops.
12. OWNER repositories are not blocked by customer subscription rules.
13. Customer AI capabilities remain entitlement controlled.
14. External legal capability is assistance, not licensed legal representation.
15. Future components are created only through controlled Executor 02 operations.
16. 01 must not mutate managed repositories directly.
17. 01 and 02 remain separate authority/execution layers.

STANDARD LIBRARY ONLY
---------------------
This file intentionally uses Python's standard library only.

===============================================================================
"""

from __future__ import annotations

import hashlib
import hmac
import importlib.util
import json
import logging
import os
import re
import subprocess
import sys
import threading
import time
import uuid

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Protocol


# =============================================================================
# IDENTITY
# =============================================================================

MAJD_PLATFORM = "MAJD-GIT"
MAJD_COMPONENT = "MAJD-AI-MASTERMIND-01"
MAJD_VERSION = "2.0.0"
MAJD_SCHEMA_VERSION = 2

BASE_DIR = Path(__file__).resolve().parent
MAJD_DIR = BASE_DIR / ".majd"

STATE_FILE = MAJD_DIR / "mastermind-state.json"
AUDIT_FILE = MAJD_DIR / "mastermind-audit.jsonl"
LOCK_FILE = MAJD_DIR / "locks" / "mastermind.lock"

EXECUTOR_FILE = BASE_DIR / "MAJD-AI-EXECUTOR-02.py"

MAX_AUTONOMOUS_REPAIR_ATTEMPTS = max(
    1,
    min(
        5,
        int(os.getenv("MAJD_MAX_REPAIR_ATTEMPTS", "3")),
    ),
)

MAX_PLAN_STEPS = max(
    1,
    min(
        100,
        int(os.getenv("MAJD_MAX_PLAN_STEPS", "50")),
    ),
)

EXECUTOR_TIMEOUT = max(
    15,
    min(
        120,
        int(os.getenv("MAJD_EXECUTOR_TIMEOUT", "60")),
    ),
)

PUBLIC_RELEASE_ALLOWED = False


# =============================================================================
# UTILITIES
# =============================================================================


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def normalize_action(value: str) -> str:
    return re.sub(
        r"[^A-Z0-9_]+",
        "_",
        str(value).strip().upper(),
    ).strip("_")


def json_safe(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, Path):
        return str(value)

    if is_dataclass(value):
        return {
            str(k): json_safe(v)
            for k, v in asdict(value).items()
        }

    if isinstance(value, Mapping):
        return {
            str(k): json_safe(v)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [json_safe(v) for v in value]

    if isinstance(value, bytes):
        return f"<bytes:{len(value)}>"

    return value


def canonical_json(value: Any) -> str:
    return json.dumps(
        json_safe(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def secure_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(
        str(a).encode("utf-8"),
        str(b).encode("utf-8"),
    )


def bounded_text(
    value: Any,
    limit: int = 4000,
) -> str:
    text = str(value)

    if len(text) <= limit:
        return text

    return text[:limit] + "...[TRUNCATED]"


# =============================================================================
# ENUMS
# =============================================================================


class AuthorityLevel(str, Enum):
    OWNER_ROOT = "OWNER_ROOT"
    PLATFORM_SYSTEM = "PLATFORM_SYSTEM"
    MAJD_AI = "MAJD_AI"
    ORGANIZATION_OWNER = "ORGANIZATION_OWNER"
    REPOSITORY_ADMIN = "REPOSITORY_ADMIN"
    DEVELOPER = "DEVELOPER"
    REVIEWER = "REVIEWER"
    CUSTOMER = "CUSTOMER"
    GUEST = "GUEST"


class ActorType(str, Enum):
    HUMAN = "HUMAN"
    AI = "AI"
    SYSTEM = "SYSTEM"
    SERVICE = "SERVICE"


class AutomationMode(str, Enum):
    ASSIST = "ASSIST"
    APPROVAL = "APPROVAL"
    AUTONOMOUS = "AUTONOMOUS"


class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    OWNER_REQUIRED = "OWNER_REQUIRED"
    SUBSCRIPTION_REQUIRED = "SUBSCRIPTION_REQUIRED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    EXECUTOR_REQUIRED = "EXECUTOR_REQUIRED"


class TaskStatus(str, Enum):
    RECEIVED = "RECEIVED"
    PLANNING = "PLANNING"
    BLOCKED = "BLOCKED"
    READY = "READY"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    REPAIRING = "REPAIRING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    WAITING_FOR_OWNER_RELEASE = "WAITING_FOR_OWNER_RELEASE"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AgentDomain(str, Enum):
    SOFTWARE_ENGINEERING = "SOFTWARE_ENGINEERING"
    ARCHITECTURE = "ARCHITECTURE"
    DEVOPS = "DEVOPS"
    QA = "QA"
    CYBERSECURITY = "CYBERSECURITY"
    SECRET_PROTECTION = "SECRET_PROTECTION"
    LEGAL_ASSISTANT = "LEGAL_ASSISTANT"
    CONTRACTS = "CONTRACTS"
    IP_LICENSING = "IP_LICENSING"
    BUSINESS = "BUSINESS"
    PRICING = "PRICING"
    GIT = "GIT"
    PLATFORM_EVOLUTION = "PLATFORM_EVOLUTION"


class Entitlement(str, Enum):
    BASIC_GIT = "BASIC_GIT"
    AI_ASSIST = "AI_ASSIST"
    AI_CODE_GENERATION = "AI_CODE_GENERATION"
    AI_PROJECT_PLANNING = "AI_PROJECT_PLANNING"
    AI_PROJECT_BUILD = "AI_PROJECT_BUILD"
    AI_REPAIR = "AI_REPAIR"
    AI_SECURITY_REVIEW = "AI_SECURITY_REVIEW"
    AI_AUTOMATION = "AI_AUTOMATION"
    AI_ENTERPRISE = "AI_ENTERPRISE"


class EventSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# =============================================================================
# DATA MODELS
# =============================================================================


@dataclass(frozen=True)
class PlatformIdentity:
    platform: str = MAJD_PLATFORM
    component: str = MAJD_COMPONENT
    version: str = MAJD_VERSION
    schema_version: int = MAJD_SCHEMA_VERSION


@dataclass
class ActorContext:
    actor_id: str
    actor_type: ActorType
    authority: AuthorityLevel
    authenticated: bool
    owner_verified: bool = False
    organization_id: Optional[str] = None
    repository_ids: List[str] = field(default_factory=list)
    entitlements: List[Entitlement] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_entitlement(
        self,
        entitlement: Entitlement,
    ) -> bool:
        return entitlement in self.entitlements

    @property
    def is_owner(self) -> bool:
        return (
            self.authority == AuthorityLevel.OWNER_ROOT
            and self.authenticated
            and self.owner_verified
        )


@dataclass
class RepositoryScope:
    repository_id: str
    owner_id: str
    organization_id: Optional[str] = None
    private: bool = True
    automation_mode: AutomationMode = AutomationMode.APPROVAL
    ai_enabled: bool = True
    allow_ai_write: bool = False
    allow_ai_git: bool = False
    allow_ai_build: bool = False
    allow_ai_deploy: bool = False
    allow_ai_self_repair: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectObjective:
    objective_id: str
    title: str
    description: str
    repository_id: Optional[str]
    requested_by: str
    created_at: str = field(default_factory=utc_now)
    constraints: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanStep:
    step_id: str
    sequence: int
    title: str
    action: str
    domain: AgentDomain
    risk: RiskLevel
    requires_executor: bool
    requires_verification: bool = True
    depends_on: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    plan_id: str
    objective_id: str
    repository_id: Optional[str]
    created_at: str
    steps: List[PlanStep]
    estimated_complexity: int
    requires_subscription: bool
    required_entitlements: List[Entitlement]
    notes: List[str] = field(default_factory=list)


@dataclass
class ExecutorRequest:
    request_id: str
    operation: str
    repository_id: Optional[str]
    actor_id: str
    authority: AuthorityLevel
    parameters: Dict[str, Any]
    correlation_id: str
    created_at: str = field(default_factory=utc_now)


@dataclass
class ExecutorResult:
    ok: bool
    request_id: str
    operation: str
    verified: bool
    changed: bool = False
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class VerificationResult:
    ok: bool
    checks: Dict[str, bool]
    evidence: Dict[str, Any] = field(default_factory=dict)
    message: str = ""


@dataclass
class MastermindResult:
    ok: bool
    task_id: str
    status: TaskStatus
    decision: Decision
    message: str
    plan: Optional[ExecutionPlan] = None
    results: List[ExecutorResult] = field(default_factory=list)
    verification: Optional[VerificationResult] = None
    owner_action_required: Optional[str] = None
    timestamp: str = field(default_factory=utc_now)


@dataclass
class AuditEvent:
    event_id: str
    timestamp: str
    severity: EventSeverity
    category: str
    action: str
    actor_id: str
    repository_id: Optional[str]
    success: bool
    details: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# SECRET REDACTION
# =============================================================================


class SecretRedactor:
    KEYWORDS = (
        "password",
        "passwd",
        "secret",
        "token",
        "api_key",
        "apikey",
        "private_key",
        "access_key",
        "client_secret",
        "authorization",
        "cookie",
        "session",
    )

    TOKEN_PATTERNS = (
        re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
        re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
        re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
        re.compile(r"AKIA[0-9A-Z]{16}"),
        re.compile(
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?"
            r"-----END [A-Z ]*PRIVATE KEY-----",
            re.DOTALL,
        ),
    )

    @classmethod
    def redact_text(cls, text: str) -> str:
        result = str(text)

        for pattern in cls.TOKEN_PATTERNS:
            result = pattern.sub(
                "[REDACTED_SECRET]",
                result,
            )

        return result

    @classmethod
    def redact(cls, value: Any) -> Any:
        if isinstance(value, str):
            return cls.redact_text(value)

        if isinstance(value, Mapping):
            cleaned: Dict[str, Any] = {}

            for key, item in value.items():
                lowered = str(key).lower()

                if any(
                    word in lowered
                    for word in cls.KEYWORDS
                ):
                    cleaned[str(key)] = "[REDACTED_SECRET]"
                else:
                    cleaned[str(key)] = cls.redact(item)

            return cleaned

        if isinstance(value, (list, tuple)):
            return [cls.redact(v) for v in value]

        return value


# =============================================================================
# AUDIT + STATE
# =============================================================================


class AuditStore:
    def __init__(
        self,
        audit_file: Path = AUDIT_FILE,
    ) -> None:
        self.audit_file = audit_file
        self._lock = threading.RLock()

    def initialize(self) -> None:
        self.audit_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def append(
        self,
        event: AuditEvent,
    ) -> None:
        self.initialize()

        payload = SecretRedactor.redact(
            json_safe(event)
        )

        with self._lock:
            with self.audit_file.open(
                "a",
                encoding="utf-8",
            ) as handle:
                handle.write(
                    canonical_json(payload) + "\n"
                )
                handle.flush()


class StateStore:
    def __init__(
        self,
        state_file: Path = STATE_FILE,
    ) -> None:
        self.state_file = state_file
        self._lock = threading.RLock()

    def initialize(self) -> None:
        self.state_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def load(self) -> Dict[str, Any]:
        self.initialize()

        if not self.state_file.exists():
            return {}

        try:
            value = json.loads(
                self.state_file.read_text(
                    encoding="utf-8"
                )
            )

            return (
                value
                if isinstance(value, dict)
                else {}
            )

        except (
            OSError,
            json.JSONDecodeError,
        ):
            return {}

    def save(
        self,
        state: Dict[str, Any],
    ) -> None:
        self.initialize()

        sanitized = SecretRedactor.redact(
            json_safe(state)
        )

        temp = self.state_file.with_suffix(
            ".tmp"
        )

        with self._lock:
            with temp.open(
                "w",
                encoding="utf-8",
            ) as handle:
                json.dump(
                    sanitized,
                    handle,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                handle.flush()
                os.fsync(handle.fileno())

            os.replace(
                temp,
                self.state_file,
            )


class MajdAuditor:
    def __init__(
        self,
        store: AuditStore,
    ) -> None:
        self.store = store

    def record(
        self,
        *,
        category: str,
        action: str,
        actor: ActorContext,
        repository_id: Optional[str],
        success: bool,
        severity: EventSeverity = EventSeverity.INFO,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.store.append(
            AuditEvent(
                event_id=new_id("audit"),
                timestamp=utc_now(),
                severity=severity,
                category=category,
                action=action,
                actor_id=actor.actor_id,
                repository_id=repository_id,
                success=success,
                details=SecretRedactor.redact(
                    details or {}
                ),
            )
        )


# =============================================================================
# EXECUTOR CONTRACT
# =============================================================================


class ExecutorAdapter(Protocol):
    def health(self) -> Dict[str, Any]:
        ...

    def execute(
        self,
        request: ExecutorRequest,
    ) -> ExecutorResult:
        ...

    def verify(
        self,
        request: ExecutorRequest,
        result: ExecutorResult,
    ) -> VerificationResult:
        ...


class NullExecutor:
    def health(self) -> Dict[str, Any]:
        return {
            "ok": False,
            "connected": False,
            "component": "MAJD-AI-EXECUTOR-02",
            "reason": "EXECUTOR_NOT_CONNECTED",
        }

    def execute(
        self,
        request: ExecutorRequest,
    ) -> ExecutorResult:
        return ExecutorResult(
            ok=False,
            request_id=request.request_id,
            operation=request.operation,
            verified=False,
            changed=False,
            message="Real Executor 02 is unavailable.",
            error="EXECUTOR_NOT_CONNECTED",
        )

    def verify(
        self,
        request: ExecutorRequest,
        result: ExecutorResult,
    ) -> VerificationResult:
        return VerificationResult(
            ok=False,
            checks={
                "executor_connected": False,
                "operation_completed": False,
                "result_verified": False,
            },
            message="Executor 02 is unavailable.",
        )


# =============================================================================
# EXECUTOR 02 BRIDGE
# =============================================================================


class Executor02Bridge:
    """
    Safe compatibility bridge between Mastermind 01 and Executor 02.

    Important:
    - Does not grant OWNER_ROOT to Executor 02.
    - Does not permit PUBLIC_RELEASE.
    - Health/self-test/inventory/security/verify are bounded.
    - AI-heavy evolve calls remain bounded.
    - Timeout is reported as failure, never success.
    """

    PUBLIC_RELEASE_OPERATIONS = {
        "PUBLIC_RELEASE",
        "RELEASE_PUBLIC",
        "DEPLOY_PUBLIC",
        "PUBLISH_PUBLIC",
        "GO_LIVE",
    }

    def __init__(
        self,
        executor_file: Path = EXECUTOR_FILE,
    ) -> None:
        self.executor_file = executor_file

    def _run_cli(
        self,
        args: List[str],
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        if not self.executor_file.exists():
            return {
                "ok": False,
                "error": "EXECUTOR_FILE_NOT_FOUND",
            }

        command = [
            sys.executable,
            str(self.executor_file),
            *args,
        ]

        started = time.monotonic()

        try:
            completed = subprocess.run(
                command,
                cwd=str(BASE_DIR),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout or EXECUTOR_TIMEOUT,
                check=False,
                env=os.environ.copy(),
            )

        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "error": "EXECUTOR_TIMEOUT",
                "timed_out": True,
                "duration_seconds": round(
                    time.monotonic() - started,
                    3,
                ),
            }

        except Exception as exc:
            return {
                "ok": False,
                "error": bounded_text(
                    SecretRedactor.redact_text(
                        repr(exc)
                    )
                ),
                "timed_out": False,
                "duration_seconds": round(
                    time.monotonic() - started,
                    3,
                ),
            }

        stdout = bounded_text(
            completed.stdout,
            20000,
        )

        stderr = bounded_text(
            completed.stderr,
            10000,
        )

        parsed: Any = None

        if completed.stdout.strip():
            try:
                parsed = json.loads(
                    completed.stdout
                )
            except json.JSONDecodeError:
                parsed = None

        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": SecretRedactor.redact_text(
                stdout
            ),
            "stderr": SecretRedactor.redact_text(
                stderr
            ),
            "json": SecretRedactor.redact(
                parsed
            ),
            "timed_out": False,
            "duration_seconds": round(
                time.monotonic() - started,
                3,
            ),
        }

    def health(self) -> Dict[str, Any]:
        if not self.executor_file.exists():
            return {
                "ok": False,
                "connected": False,
                "component": "MAJD-AI-EXECUTOR-02",
                "reason": "EXECUTOR_FILE_NOT_FOUND",
                "path": str(self.executor_file),
            }

        result = self._run_cli(
            ["health"],
            timeout=15,
        )

        return {
            "ok": bool(result.get("ok")),
            "connected": bool(result.get("ok")),
            "component": "MAJD-AI-EXECUTOR-02",
            "path": str(self.executor_file),
            "details": result.get("json"),
            "error": result.get("error"),
        }

    @staticmethod
    def _objective_from_request(
        request: ExecutorRequest,
    ) -> str:
        objective = str(
            request.parameters.get(
                "objective",
                "",
            )
        ).strip()

        if not objective:
            objective = (
                f"Perform {request.operation} for "
                f"{request.repository_id or MAJD_PLATFORM}."
            )

        return bounded_text(
            objective,
            1500,
        )

    def execute(
        self,
        request: ExecutorRequest,
    ) -> ExecutorResult:
        operation = normalize_action(
            request.operation
        )

        if operation in self.PUBLIC_RELEASE_OPERATIONS:
            return ExecutorResult(
                ok=False,
                request_id=request.request_id,
                operation=operation,
                verified=False,
                changed=False,
                message=(
                    "Public release is blocked by "
                    "Mastermind 01."
                ),
                error="OWNER_PUBLIC_RELEASE_REQUIRED",
            )

        deterministic_commands = {
            "VERIFY_PROJECT": ["verify"],
            "TEST_PROJECT": ["verify"],
            "SECURITY_REVIEW": ["security"],
            "SECRET_REVIEW": ["security"],
            "ANALYZE_PROJECT": ["inventory"],
        }

        if operation in deterministic_commands:
            raw = self._run_cli(
                deterministic_commands[operation],
                timeout=30,
            )

        elif operation == "AUTO_REPAIR":
            objective = (
                "Perform one bounded repair for repository "
                f"{request.repository_id or MAJD_PLATFORM}. "
                "Repair only a verified failure. "
                "Test the repair. "
                "Do not release publicly."
            )

            raw = self._run_cli(
                ["evolve", objective],
                timeout=EXECUTOR_TIMEOUT,
            )

        elif operation in {
            "GENERATE_OR_MODIFY_CODE",
            "BUILD_AND_OPERATE",
            "GIT_OPERATION",
            "EVOLVE_PLATFORM",
        }:
            objective = self._objective_from_request(
                request
            )

            objective += (
                " Perform one bounded necessary change only. "
                "Verify the result. "
                "Do not release publicly."
            )

            raw = self._run_cli(
                ["evolve", objective],
                timeout=EXECUTOR_TIMEOUT,
            )

        else:
            return ExecutorResult(
                ok=True,
                request_id=request.request_id,
                operation=operation,
                verified=True,
                changed=False,
                message=(
                    "Logical operation retained by "
                    "Mastermind orchestration."
                ),
                data={
                    "delegated": False,
                    "reason": "NO_EXECUTOR_MUTATION_REQUIRED",
                },
            )

        parsed = raw.get("json")

        parsed_success = (
            isinstance(parsed, dict)
            and parsed.get("success") is True
        )

        ok = bool(
            raw.get("ok")
            and (
                parsed_success
                or parsed is None
            )
        )

        if raw.get("timed_out"):
            ok = False

        return ExecutorResult(
            ok=ok,
            request_id=request.request_id,
            operation=operation,
            verified=False,
            changed=bool(
                isinstance(parsed, dict)
                and (
                    parsed.get("changed")
                    or parsed.get("changes")
                )
            ),
            message=(
                "Executor 02 completed operation."
                if ok
                else "Executor 02 operation failed."
            ),
            data={
                "executor": SecretRedactor.redact(
                    parsed
                    if parsed is not None
                    else {
                        "returncode":
                            raw.get("returncode"),
                        "stdout":
                            raw.get("stdout"),
                    }
                ),
                "duration_seconds":
                    raw.get("duration_seconds"),
            },
            error=(
                None
                if ok
                else str(
                    raw.get("error")
                    or (
                        parsed.get("error")
                        if isinstance(parsed, dict)
                        else None
                    )
                    or raw.get("stderr")
                    or "EXECUTOR_OPERATION_FAILED"
                )
            ),
        )

    def verify(
        self,
        request: ExecutorRequest,
        result: ExecutorResult,
    ) -> VerificationResult:
        if not result.ok:
            return VerificationResult(
                ok=False,
                checks={
                    "operation_ok": False,
                    "executor_verification": False,
                },
                message=(
                    result.error
                    or "Operation failed before verification."
                ),
            )

        raw = self._run_cli(
            ["verify"],
            timeout=30,
        )

        parsed = raw.get("json")

        parsed_success = (
            isinstance(parsed, dict)
            and parsed.get("success") is True
        )

        verified = bool(
            raw.get("ok")
            and (
                parsed_success
                or parsed is None
            )
        )

        return VerificationResult(
            ok=verified,
            checks={
                "operation_ok": result.ok,
                "executor_verification": verified,
                "public_release_blocked":
                    not PUBLIC_RELEASE_ALLOWED,
            },
            evidence={
                "executor_verify":
                    SecretRedactor.redact(parsed),
                "duration_seconds":
                    raw.get("duration_seconds"),
            },
            message=(
                "Executor verification passed."
                if verified
                else "Executor verification failed."
            ),
        )


def build_executor() -> ExecutorAdapter:
    if not EXECUTOR_FILE.exists():
        return NullExecutor()

    return Executor02Bridge(
        EXECUTOR_FILE
    )


# =============================================================================
# AI PROVIDER
# =============================================================================


class AIProvider(Protocol):
    def health(self) -> Dict[str, Any]:
        ...

    def reason(
        self,
        *,
        system_context: Dict[str, Any],
        objective: ProjectObjective,
        repository_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        ...


class DeterministicFoundationAI:
    """
    Fast deterministic planner.

    Ollama is NOT required for Mastermind planning.
    Executor 02 may use an AI provider for bounded jobs when necessary.
    """

    def health(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "provider": "DETERMINISTIC_MASTERMIND",
            "external_model_required": False,
            "blocking_llm_dependency": False,
        }

    def reason(
        self,
        *,
        system_context: Dict[str, Any],
        objective: ProjectObjective,
        repository_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        text = (
            objective.title
            + " "
            + objective.description
        ).lower()

        domains: List[AgentDomain] = [
            AgentDomain.SOFTWARE_ENGINEERING
        ]

        keyword_domains = {
            AgentDomain.CYBERSECURITY: (
                "security",
                "secure",
                "vulnerability",
                "cyber",
                "اختراق",
                "أمن",
                "ثغرة",
            ),
            AgentDomain.LEGAL_ASSISTANT: (
                "legal",
                "law",
                "contract",
                "قانون",
                "عقد",
            ),
            AgentDomain.IP_LICENSING: (
                "license",
                "copyright",
                "intellectual property",
                "ترخيص",
                "ملكية",
                "حقوق",
            ),
            AgentDomain.PRICING: (
                "price",
                "pricing",
                "subscription",
                "billing",
                "سعر",
                "اشتراك",
                "تسعير",
            ),
            AgentDomain.DEVOPS: (
                "deploy",
                "server",
                "docker",
                "ci",
                "cd",
                "نشر",
                "سيرفر",
            ),
            AgentDomain.GIT: (
                "git",
                "commit",
                "branch",
                "merge",
                "repository",
                "مستودع",
            ),
            AgentDomain.PLATFORM_EVOLUTION: (
                "evolve",
                "platform",
                "autonomous",
                "production-ready",
                "ready_for_public_launch",
                "توسع",
                "المنصة",
                "ذاتي",
            ),
        }

        for domain, keywords in keyword_domains.items():
            if any(
                keyword in text
                for keyword in keywords
            ):
                if domain not in domains:
                    domains.append(domain)

        return {
            "domains": [
                domain.value
                for domain in domains
            ],
            "summary": bounded_text(
                objective.description,
                1500,
            ),
            "confidence": 1.0,
            "deterministic": True,
        }


# =============================================================================
# AUTHORITY
# =============================================================================


class AuthorityEngine:
    OWNER_ONLY_ACTIONS = {
        "TRANSFER_PLATFORM_OWNERSHIP",
        "REMOVE_OWNER",
        "CHANGE_OWNER_ROOT_AUTHORITY",
        "CREATE_OWNER_ROOT",
        "EXPORT_ROOT_SECRET",
        "READ_ROOT_SECRET",
        "DISABLE_OWNER_PROTECTION",
        "DISABLE_AUTHORITY_ENGINE",
        "ALTER_AUTHORITY_HIERARCHY",
        "GRANT_OWNER_TO_AI",
        "DELETE_PLATFORM_ROOT",
        "ROTATE_OWNER_ROOT_IDENTITY",
        "PUBLIC_RELEASE",
        "RELEASE_PUBLIC",
        "DEPLOY_PUBLIC",
        "PUBLISH_PUBLIC",
        "GO_LIVE",
    }

    NEVER_AI_ACTIONS = OWNER_ONLY_ACTIONS | {
        "BYPASS_REPOSITORY_ISOLATION",
        "DISABLE_SECRET_REDACTION",
        "EXPORT_OTHER_TENANT_CODE",
        "EXPORT_OTHER_TENANT_SECRETS",
        "TRAIN_ON_PRIVATE_CUSTOMER_CODE_WITHOUT_AUTHORIZATION",
    }

    def authorize(
        self,
        *,
        actor: ActorContext,
        action: str,
        repository: Optional[RepositoryScope],
    ) -> Decision:
        action = normalize_action(action)

        if not actor.authenticated:
            return Decision.DENY

        if action in self.OWNER_ONLY_ACTIONS:
            return (
                Decision.ALLOW
                if actor.is_owner
                else Decision.OWNER_REQUIRED
            )

        if (
            actor.actor_type == ActorType.AI
            and action in self.NEVER_AI_ACTIONS
        ):
            return Decision.DENY

        if actor.is_owner:
            return Decision.ALLOW

        if repository is None:
            if actor.authority in {
                AuthorityLevel.PLATFORM_SYSTEM,
                AuthorityLevel.MAJD_AI,
            }:
                return Decision.ALLOW

            return Decision.DENY

        if actor.authority in {
            AuthorityLevel.PLATFORM_SYSTEM,
            AuthorityLevel.MAJD_AI,
        }:
            return (
                Decision.ALLOW
                if repository.ai_enabled
                else Decision.DENY
            )

        if (
            repository.repository_id
            not in actor.repository_ids
        ):
            return Decision.DENY

        return Decision.ALLOW


class RepositoryIsolation:
    @staticmethod
    def validate(
        actor: ActorContext,
        repository: Optional[RepositoryScope],
    ) -> bool:
        if repository is None:
            return actor.authority in {
                AuthorityLevel.OWNER_ROOT,
                AuthorityLevel.PLATFORM_SYSTEM,
                AuthorityLevel.MAJD_AI,
            }

        if actor.is_owner:
            return True

        if actor.authority in {
            AuthorityLevel.PLATFORM_SYSTEM,
            AuthorityLevel.MAJD_AI,
        }:
            return repository.ai_enabled

        return (
            repository.repository_id
            in actor.repository_ids
        )


class EntitlementEngine:
    ACTION_ENTITLEMENTS = {
        "AI_ASSIST":
            Entitlement.AI_ASSIST,
        "GENERATE_CODE":
            Entitlement.AI_CODE_GENERATION,
        "PLAN_PROJECT":
            Entitlement.AI_PROJECT_PLANNING,
        "BUILD_PROJECT":
            Entitlement.AI_PROJECT_BUILD,
        "REPAIR_PROJECT":
            Entitlement.AI_REPAIR,
        "SECURITY_REVIEW":
            Entitlement.AI_SECURITY_REVIEW,
        "AUTONOMOUS_DEVELOPMENT":
            Entitlement.AI_AUTOMATION,
    }

    def check(
        self,
        actor: ActorContext,
        action: str,
    ) -> Decision:
        if actor.is_owner:
            return Decision.ALLOW

        if actor.authority in {
            AuthorityLevel.PLATFORM_SYSTEM,
            AuthorityLevel.MAJD_AI,
        }:
            return Decision.ALLOW

        entitlement = self.ACTION_ENTITLEMENTS.get(
            normalize_action(action)
        )

        if entitlement is None:
            return Decision.ALLOW

        return (
            Decision.ALLOW
            if actor.has_entitlement(entitlement)
            else Decision.SUBSCRIPTION_REQUIRED
        )


# =============================================================================
# RISK
# =============================================================================


class RiskEngine:
    HIGH_RISK_WORDS = {
        "delete",
        "production",
        "deploy",
        "payment",
        "billing",
        "secret",
        "credential",
        "migration",
        "database",
        "security",
        "permission",
        "ownership",
        "حذف",
        "إنتاج",
        "دفع",
        "سر",
        "صلاحية",
        "ملكية",
    }

    CRITICAL_WORDS = {
        "owner",
        "root",
        "transfer ownership",
        "disable security",
        "export secret",
        "المالك",
        "المدير الأعلى",
        "تعطيل الحماية",
    }

    def classify(
        self,
        text: str,
    ) -> RiskLevel:
        lowered = text.lower()

        if any(
            word in lowered
            for word in self.CRITICAL_WORDS
        ):
            return RiskLevel.CRITICAL

        if any(
            word in lowered
            for word in self.HIGH_RISK_WORDS
        ):
            return RiskLevel.HIGH

        if len(text) > 1000:
            return RiskLevel.MEDIUM

        return RiskLevel.LOW


# =============================================================================
# SPECIALISTS
# =============================================================================


@dataclass(frozen=True)
class SpecialistProfile:
    domain: AgentDomain
    purpose: str
    can_execute: bool
    must_verify: bool


class SpecialistRegistry:
    def __init__(self) -> None:
        self._profiles: Dict[
            AgentDomain,
            SpecialistProfile
        ] = {}

        entries = [
            (
                AgentDomain.SOFTWARE_ENGINEERING,
                "Software engineering.",
                True,
            ),
            (
                AgentDomain.ARCHITECTURE,
                "Architecture.",
                False,
            ),
            (
                AgentDomain.DEVOPS,
                "Operations.",
                True,
            ),
            (
                AgentDomain.QA,
                "Quality assurance.",
                True,
            ),
            (
                AgentDomain.CYBERSECURITY,
                "Defensive security.",
                True,
            ),
            (
                AgentDomain.SECRET_PROTECTION,
                "Secret protection.",
                True,
            ),
            (
                AgentDomain.LEGAL_ASSISTANT,
                "Legal assistance.",
                False,
            ),
            (
                AgentDomain.CONTRACTS,
                "Contract assistance.",
                False,
            ),
            (
                AgentDomain.IP_LICENSING,
                "IP/license review.",
                False,
            ),
            (
                AgentDomain.BUSINESS,
                "Business planning.",
                False,
            ),
            (
                AgentDomain.PRICING,
                "Pricing analysis.",
                False,
            ),
            (
                AgentDomain.GIT,
                "Git operations.",
                True,
            ),
            (
                AgentDomain.PLATFORM_EVOLUTION,
                "Controlled evolution.",
                True,
            ),
        ]

        for domain, purpose, execute in entries:
            self._profiles[domain] = (
                SpecialistProfile(
                    domain=domain,
                    purpose=purpose,
                    can_execute=execute,
                    must_verify=True,
                )
            )

    def get(
        self,
        domain: AgentDomain,
    ) -> SpecialistProfile:
        return self._profiles[domain]

    def all(self) -> List[SpecialistProfile]:
        return list(
            self._profiles.values()
        )


# =============================================================================
# PLANNER
# =============================================================================


class ProjectPlanner:
    def __init__(
        self,
        ai_provider: AIProvider,
        risk_engine: RiskEngine,
        specialists: SpecialistRegistry,
    ) -> None:
        self.ai_provider = ai_provider
        self.risk_engine = risk_engine
        self.specialists = specialists

    def build_plan(
        self,
        *,
        objective: ProjectObjective,
        actor: ActorContext,
        repository: Optional[RepositoryScope],
    ) -> ExecutionPlan:
        reasoning = self.ai_provider.reason(
            system_context={
                "platform": MAJD_PLATFORM,
                "owner_is_supreme": True,
                "public_release_allowed": False,
                "verification_required": True,
            },
            objective=objective,
            repository_context=(
                json_safe(repository)
                if repository
                else {}
            ),
        )

        domains: List[AgentDomain] = []

        for raw in reasoning.get(
            "domains",
            [],
        ):
            try:
                domain = AgentDomain(raw)
            except ValueError:
                continue

            if domain not in domains:
                domains.append(domain)

        if (
            AgentDomain.SOFTWARE_ENGINEERING
            not in domains
        ):
            domains.insert(
                0,
                AgentDomain.SOFTWARE_ENGINEERING,
            )

        risk = self.risk_engine.classify(
            objective.title
            + "\n"
            + objective.description
        )

        steps: List[PlanStep] = []
        sequence = 1

        steps.append(
            PlanStep(
                step_id=new_id("step"),
                sequence=sequence,
                title="Inspect project",
                action="ANALYZE_PROJECT",
                domain=AgentDomain.ARCHITECTURE,
                risk=RiskLevel.LOW,
                requires_executor=repository is not None,
                parameters={
                    "objective":
                        objective.description,
                },
            )
        )

        sequence += 1

        for domain in domains:
            profile = self.specialists.get(
                domain
            )

            action_map = {
                AgentDomain.SOFTWARE_ENGINEERING:
                    "GENERATE_OR_MODIFY_CODE",
                AgentDomain.ARCHITECTURE:
                    "PLAN_ARCHITECTURE",
                AgentDomain.DEVOPS:
                    "BUILD_AND_OPERATE",
                AgentDomain.QA:
                    "TEST_PROJECT",
                AgentDomain.CYBERSECURITY:
                    "SECURITY_REVIEW",
                AgentDomain.SECRET_PROTECTION:
                    "SECRET_REVIEW",
                AgentDomain.LEGAL_ASSISTANT:
                    "LEGAL_ANALYSIS",
                AgentDomain.CONTRACTS:
                    "CONTRACT_ANALYSIS",
                AgentDomain.IP_LICENSING:
                    "LICENSE_REVIEW",
                AgentDomain.BUSINESS:
                    "BUSINESS_ANALYSIS",
                AgentDomain.PRICING:
                    "PRICE_OBJECTIVE",
                AgentDomain.GIT:
                    "GIT_OPERATION",
                AgentDomain.PLATFORM_EVOLUTION:
                    "EVOLVE_PLATFORM",
            }

            steps.append(
                PlanStep(
                    step_id=new_id("step"),
                    sequence=sequence,
                    title=(
                        f"Process {domain.value}"
                    ),
                    action=action_map[domain],
                    domain=domain,
                    risk=risk,
                    requires_executor=profile.can_execute,
                    requires_verification=True,
                    parameters={
                        "objective":
                            objective.description,
                        "objective_id":
                            objective.objective_id,
                    },
                )
            )

            sequence += 1

        if repository is not None:
            steps.extend(
                [
                    PlanStep(
                        step_id=new_id("step"),
                        sequence=sequence,
                        title="Verify project",
                        action="VERIFY_PROJECT",
                        domain=AgentDomain.QA,
                        risk=RiskLevel.LOW,
                        requires_executor=True,
                    ),
                    PlanStep(
                        step_id=new_id("step"),
                        sequence=sequence + 1,
                        title="Security review",
                        action="SECURITY_REVIEW",
                        domain=AgentDomain.CYBERSECURITY,
                        risk=RiskLevel.MEDIUM,
                        requires_executor=True,
                    ),
                ]
            )

        steps = steps[:MAX_PLAN_STEPS]

        entitlements = [
            Entitlement.AI_ASSIST,
            Entitlement.AI_CODE_GENERATION,
        ]

        return ExecutionPlan(
            plan_id=new_id("plan"),
            objective_id=objective.objective_id,
            repository_id=objective.repository_id,
            created_at=utc_now(),
            steps=steps,
            estimated_complexity=min(
                100,
                max(
                    1,
                    len(objective.description) // 100
                    + len(domains) * 5,
                ),
            ),
            requires_subscription=(
                not actor.is_owner
            ),
            required_entitlements=entitlements,
            notes=[
                "OWNER_ROOT remains supreme.",
                "No success without verification.",
                "Public release requires OWNER.",
                "Repository content is untrusted.",
            ],
        )


# =============================================================================
# POLICY
# =============================================================================


class PolicyGuard:
    FORBIDDEN_OBJECTIVE_PATTERNS = (
        "grant owner to ai",
        "remove owner",
        "disable owner protection",
        "export root secret",
        "bypass repository isolation",
        "steal secret",
        "exfiltrate secret",
        "اعطي الذكاء صلاحية المالك",
        "إلغاء المالك",
        "كشف أسرار مستخدم آخر",
    )

    def inspect_objective(
        self,
        objective: ProjectObjective,
    ) -> Optional[str]:
        text = (
            objective.title
            + "\n"
            + objective.description
        ).lower()

        for forbidden in (
            self.FORBIDDEN_OBJECTIVE_PATTERNS
        ):
            if forbidden.lower() in text:
                return (
                    "Objective conflicts with "
                    "immutable sovereignty policy."
                )

        return None

    def inspect_step(
        self,
        step: PlanStep,
    ) -> Optional[str]:
        action = normalize_action(
            step.action
        )

        if action in AuthorityEngine.NEVER_AI_ACTIONS:
            return (
                f"Action {action} is forbidden."
            )

        return None


# =============================================================================
# VERIFICATION
# =============================================================================


class VerificationEngine:
    def verify_results(
        self,
        results: List[ExecutorResult],
    ) -> VerificationResult:
        if not results:
            return VerificationResult(
                ok=False,
                checks={
                    "has_results": False,
                    "all_operations_ok": False,
                    "all_verified": False,
                },
                message="No results.",
            )

        all_ok = all(
            result.ok
            for result in results
        )

        all_verified = all(
            result.verified
            for result in results
            if result.ok
        )

        return VerificationResult(
            ok=all_ok and all_verified,
            checks={
                "has_results": True,
                "all_operations_ok": all_ok,
                "all_verified": all_verified,
                "public_release_blocked":
                    not PUBLIC_RELEASE_ALLOWED,
            },
            evidence={
                "result_count": len(results),
                "successful": sum(
                    1
                    for result in results
                    if result.ok
                ),
                "verified": sum(
                    1
                    for result in results
                    if result.verified
                ),
            },
            message=(
                "Execution verified."
                if all_ok and all_verified
                else "Execution not fully verified."
            ),
        )


# =============================================================================
# MASTERMIND
# =============================================================================


class MajdAIMastermind:
    def __init__(
        self,
        *,
        executor: Optional[ExecutorAdapter] = None,
        ai_provider: Optional[AIProvider] = None,
    ) -> None:
        self.identity = PlatformIdentity()

        self.state_store = StateStore()
        self.audit_store = AuditStore()
        self.auditor = MajdAuditor(
            self.audit_store
        )

        self.executor = (
            executor
            if executor is not None
            else build_executor()
        )

        self.ai_provider = (
            ai_provider
            if ai_provider is not None
            else DeterministicFoundationAI()
        )

        self.authority = AuthorityEngine()
        self.isolation = RepositoryIsolation()
        self.entitlements = EntitlementEngine()
        self.risk = RiskEngine()
        self.specialists = SpecialistRegistry()
        self.policy = PolicyGuard()
        self.verifier = VerificationEngine()

        self.planner = ProjectPlanner(
            self.ai_provider,
            self.risk,
            self.specialists,
        )

        self.instance_id = new_id(
            "mastermind"
        )

        self.started_at: Optional[str] = None

        self._lock = threading.RLock()

    @staticmethod
    def owner_context(
        owner_id: str = "MAJD-OWNER",
        verified: bool = True,
    ) -> ActorContext:
        return ActorContext(
            actor_id=owner_id,
            actor_type=ActorType.HUMAN,
            authority=AuthorityLevel.OWNER_ROOT,
            authenticated=True,
            owner_verified=verified,
            entitlements=list(Entitlement),
        )

    @staticmethod
    def ai_context() -> ActorContext:
        return ActorContext(
            actor_id=MAJD_COMPONENT,
            actor_type=ActorType.AI,
            authority=AuthorityLevel.MAJD_AI,
            authenticated=True,
            owner_verified=False,
            entitlements=list(Entitlement),
        )

    def start(self) -> Dict[str, Any]:
        with self._lock:
            self.started_at = utc_now()

            state = self.snapshot()

            self.state_store.save(
                state
            )

            self.auditor.record(
                category="MASTERMIND",
                action="START",
                actor=self.ai_context(),
                repository_id=None,
                success=True,
                details={
                    "instance_id":
                        self.instance_id,
                    "version":
                        MAJD_VERSION,
                    "executor":
                        self.executor.health(),
                },
            )

            return state

    def snapshot(self) -> Dict[str, Any]:
        base = {
            "identity":
                json_safe(self.identity),
            "instance_id":
                self.instance_id,
            "started_at":
                self.started_at,
            "timestamp":
                utc_now(),
            "executor":
                SecretRedactor.redact(
                    self.executor.health()
                ),
            "ai_provider":
                self.ai_provider.health(),
            "authority": {
                "owner_root_supreme": True,
                "ai_can_be_owner": False,
                "public_release_allowed": False,
                "cross_tenant_secret_export":
                    False,
            },
            "architecture": {
                "mastermind": "01",
                "executor": "02",
                "flow":
                    "OWNER->01->02->VERIFY",
            },
        }

        base["integrity"] = sha256_text(
            canonical_json(base)
        )

        return base

    def health(self) -> Dict[str, Any]:
        executor_health = (
            self.executor.health()
        )

        ai_health = (
            self.ai_provider.health()
        )

        return {
            "ok": True,
            "component": MAJD_COMPONENT,
            "version": MAJD_VERSION,
            "mastermind_ready": True,
            "executor_connected": bool(
                executor_health.get("ok")
            ),
            "ai_provider_ready": bool(
                ai_health.get("ok")
            ),
            "full_autonomy_ready": bool(
                executor_health.get("ok")
            ),
            "owner_root_protected": True,
            "public_release_blocked": True,
            "blocking_llm_required": False,
            "timestamp": utc_now(),
        }

    def plan(
        self,
        *,
        actor: ActorContext,
        objective: ProjectObjective,
        repository: Optional[RepositoryScope],
    ) -> MastermindResult:
        task_id = new_id("task")

        policy_error = (
            self.policy.inspect_objective(
                objective
            )
        )

        if policy_error:
            return MastermindResult(
                ok=False,
                task_id=task_id,
                status=TaskStatus.BLOCKED,
                decision=Decision.DENY,
                message=policy_error,
            )

        if not self.isolation.validate(
            actor,
            repository,
        ):
            return MastermindResult(
                ok=False,
                task_id=task_id,
                status=TaskStatus.BLOCKED,
                decision=Decision.DENY,
                message=(
                    "Repository isolation denied."
                ),
            )

        decision = self.authority.authorize(
            actor=actor,
            action="PLAN_PROJECT",
            repository=repository,
        )

        if decision != Decision.ALLOW:
            return MastermindResult(
                ok=False,
                task_id=task_id,
                status=TaskStatus.BLOCKED,
                decision=decision,
                message="Authority denied.",
            )

        entitlement = self.entitlements.check(
            actor,
            "PLAN_PROJECT",
        )

        if entitlement != Decision.ALLOW:
            return MastermindResult(
                ok=False,
                task_id=task_id,
                status=TaskStatus.BLOCKED,
                decision=entitlement,
                message=(
                    "AI entitlement required."
                ),
            )

        plan = self.planner.build_plan(
            objective=objective,
            actor=actor,
            repository=repository,
        )

        self.auditor.record(
            category="PLANNING",
            action="PLAN_PROJECT",
            actor=actor,
            repository_id=
                objective.repository_id,
            success=True,
            details={
                "task_id": task_id,
                "plan_id": plan.plan_id,
                "complexity":
                    plan.estimated_complexity,
            },
        )

        return MastermindResult(
            ok=True,
            task_id=task_id,
            status=TaskStatus.READY,
            decision=Decision.ALLOW,
            message="Plan created.",
            plan=plan,
        )

    def execute_objective(
        self,
        *,
        actor: ActorContext,
        objective: ProjectObjective,
        repository: Optional[RepositoryScope],
    ) -> MastermindResult:
        planned = self.plan(
            actor=actor,
            objective=objective,
            repository=repository,
        )

        if (
            not planned.ok
            or planned.plan is None
        ):
            return planned

        plan = planned.plan

        if (
            repository
            and not actor.is_owner
            and repository.automation_mode
            != AutomationMode.AUTONOMOUS
        ):
            return MastermindResult(
                ok=True,
                task_id=planned.task_id,
                status=TaskStatus.READY,
                decision=
                    Decision.APPROVAL_REQUIRED,
                message=(
                    "Repository approval required."
                ),
                plan=plan,
            )

        executor_steps = [
            step
            for step in plan.steps
            if step.requires_executor
        ]

        if (
            executor_steps
            and not self.executor.health().get(
                "ok"
            )
        ):
            return MastermindResult(
                ok=False,
                task_id=planned.task_id,
                status=TaskStatus.BLOCKED,
                decision=
                    Decision.EXECUTOR_REQUIRED,
                message=(
                    "Executor 02 is not ready."
                ),
                plan=plan,
            )

        results: List[ExecutorResult] = []

        for step in plan.steps:
            policy_error = (
                self.policy.inspect_step(step)
            )

            if policy_error:
                return MastermindResult(
                    ok=False,
                    task_id=planned.task_id,
                    status=TaskStatus.BLOCKED,
                    decision=Decision.DENY,
                    message=policy_error,
                    plan=plan,
                    results=results,
                )

            if not step.requires_executor:
                results.append(
                    ExecutorResult(
                        ok=True,
                        request_id=
                            new_id("logical"),
                        operation=step.action,
                        verified=True,
                        changed=False,
                        message=(
                            "Logical mastermind "
                            "step completed."
                        ),
                    )
                )
                continue

            request = ExecutorRequest(
                request_id=new_id("exec"),
                operation=step.action,
                repository_id=
                    objective.repository_id,
                actor_id=actor.actor_id,
                authority=actor.authority,
                parameters=
                    SecretRedactor.redact(
                        step.parameters
                    ),
                correlation_id=
                    planned.task_id,
            )

            result = self.executor.execute(
                request
            )

            if result.ok:
                verification = (
                    self.executor.verify(
                        request,
                        result,
                    )
                )

                result.verified = (
                    verification.ok
                )

                if not verification.ok:
                    result.ok = False
                    result.error = (
                        verification.message
                    )

            results.append(result)

            if not result.ok:
                self.auditor.record(
                    category="EXECUTION",
                    action=step.action,
                    actor=actor,
                    repository_id=
                        objective.repository_id,
                    success=False,
                    severity=
                        EventSeverity.ERROR,
                    details={
                        "error":
                            result.error,
                        "request_id":
                            request.request_id,
                    },
                )

                return MastermindResult(
                    ok=False,
                    task_id=planned.task_id,
                    status=TaskStatus.FAILED,
                    decision=Decision.ALLOW,
                    message=(
                        "Executor step failed. "
                        "No false success reported."
                    ),
                    plan=plan,
                    results=results,
                    verification=
                        self.verifier.verify_results(
                            results
                        ),
                )

        verification = (
            self.verifier.verify_results(
                results
            )
        )

        if not verification.ok:
            return MastermindResult(
                ok=False,
                task_id=planned.task_id,
                status=TaskStatus.FAILED,
                decision=Decision.ALLOW,
                message=(
                    "Final verification failed."
                ),
                plan=plan,
                results=results,
                verification=verification,
            )

        return MastermindResult(
            ok=True,
            task_id=planned.task_id,
            status=
                TaskStatus.WAITING_FOR_OWNER_RELEASE,
            decision=Decision.ALLOW,
            message=(
                "Objective completed and verified. "
                "Public release remains blocked "
                "until OWNER_ROOT release command."
            ),
            plan=plan,
            results=results,
            verification=verification,
            owner_action_required=(
                "OWNER_RELEASE_REQUIRED"
            ),
        )

    def evolve_platform(
        self,
        *,
        owner: ActorContext,
        goal: str,
    ) -> MastermindResult:
        if not owner.is_owner:
            return MastermindResult(
                ok=False,
                task_id=new_id("task"),
                status=TaskStatus.BLOCKED,
                decision=
                    Decision.OWNER_REQUIRED,
                message=(
                    "Verified OWNER_ROOT required."
                ),
            )

        objective = ProjectObjective(
            objective_id=
                new_id("objective"),
            title=(
                "Autonomous MAJD-GIT Evolution"
            ),
            description=goal,
            repository_id=MAJD_PLATFORM,
            requested_by=owner.actor_id,
            constraints=[
                "OWNER_ROOT remains supreme.",
                "Never expose secrets.",
                "Never cross tenant boundaries.",
                "Never fake success.",
                "Public release is forbidden.",
                (
                    "Use deterministic execution "
                    "when AI is unnecessary."
                ),
                (
                    "AI timeout must not be "
                    "reported as success."
                ),
            ],
            acceptance_criteria=[
                (
                    "Real changes are performed "
                    "only by Executor 02."
                ),
                "Available checks pass.",
                "Security checks pass.",
                "Results are verified.",
                (
                    "Final state does not "
                    "publicly release anything."
                ),
            ],
            metadata={
                "autonomous_evolution": True,
                "public_release": False,
            },
        )

        repository = RepositoryScope(
            repository_id=MAJD_PLATFORM,
            owner_id=owner.actor_id,
            private=True,
            automation_mode=
                AutomationMode.AUTONOMOUS,
            ai_enabled=True,
            allow_ai_write=True,
            allow_ai_git=True,
            allow_ai_build=True,
            allow_ai_deploy=False,
            allow_ai_self_repair=True,
            metadata={
                "platform_repository": True,
                "public_release_allowed":
                    False,
            },
        )

        return self.execute_objective(
            actor=owner,
            objective=objective,
            repository=repository,
        )

    def self_test(self) -> Dict[str, Any]:
        tests: Dict[str, bool] = {}

        owner = self.owner_context()
        ai = self.ai_context()

        tests["owner_root_valid"] = (
            owner.is_owner
        )

        tests["ai_not_owner"] = (
            not ai.is_owner
        )

        tests["ai_cannot_grant_owner"] = (
            self.authority.authorize(
                actor=ai,
                action="GRANT_OWNER_TO_AI",
                repository=None,
            )
            != Decision.ALLOW
        )

        tests["public_release_owner_only"] = (
            self.authority.authorize(
                actor=ai,
                action="PUBLIC_RELEASE",
                repository=None,
            )
            != Decision.ALLOW
        )

        tests["public_release_globally_blocked"] = (
            PUBLIC_RELEASE_ALLOWED is False
        )

        tests["secret_redaction"] = (
            SecretRedactor.redact(
                {
                    "password": "secret",
                    "normal": "safe",
                }
            )["password"]
            == "[REDACTED_SECRET]"
        )

        repo_a = RepositoryScope(
            repository_id="repo-a",
            owner_id="user-a",
        )

        user_b = ActorContext(
            actor_id="user-b",
            actor_type=ActorType.HUMAN,
            authority=
                AuthorityLevel.DEVELOPER,
            authenticated=True,
            repository_ids=["repo-b"],
        )

        tests["cross_repo_denied"] = (
            not self.isolation.validate(
                user_b,
                repo_a,
            )
        )

        customer = ActorContext(
            actor_id="customer",
            actor_type=ActorType.HUMAN,
            authority=
                AuthorityLevel.CUSTOMER,
            authenticated=True,
            repository_ids=["repo-customer"],
        )

        tests["subscription_enforced"] = (
            self.entitlements.check(
                customer,
                "GENERATE_CODE",
            )
            == Decision.SUBSCRIPTION_REQUIRED
        )

        tests["owner_not_subscription_blocked"] = (
            self.entitlements.check(
                owner,
                "GENERATE_CODE",
            )
            == Decision.ALLOW
        )

        tests["executor_file_detected"] = (
            EXECUTOR_FILE.exists()
        )

        tests["mastermind_uses_deterministic_planner"] = (
            self.ai_provider.health().get(
                "blocking_llm_dependency"
            )
            is False
        )

        passed = all(
            tests.values()
        )

        result = {
            "ok": passed,
            "component": MAJD_COMPONENT,
            "version": MAJD_VERSION,
            "tests": tests,
            "executor":
                self.executor.health(),
            "ai_provider":
                self.ai_provider.health(),
            "architecture": (
                "OWNER_ROOT -> 01 -> 02 -> "
                "VERIFY -> WAITING_FOR_OWNER_RELEASE"
            ),
            "timestamp": utc_now(),
        }

        self.auditor.record(
            category="SELF_TEST",
            action="SELF_TEST",
            actor=ai,
            repository_id=None,
            success=passed,
            severity=(
                EventSeverity.INFO
                if passed
                else EventSeverity.ERROR
            ),
            details=result,
        )

        return result


# =============================================================================
# CLI
# =============================================================================


def print_json(
    value: Any,
) -> None:
    print(
        json.dumps(
            SecretRedactor.redact(
                json_safe(value)
            ),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s %(levelname)s "
            "%(message)s"
        ),
    )

    mastermind = MajdAIMastermind()

    try:
        mastermind.start()

    except Exception as exc:
        print_json(
            {
                "ok": False,
                "component": MAJD_COMPONENT,
                "error":
                    SecretRedactor.redact_text(
                        repr(exc)
                    ),
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
        result = mastermind.health()
        print_json(result)
        return (
            0
            if result["ok"]
            else 1
        )

    if command in {
        "self-test",
        "test",
    }:
        result = mastermind.self_test()
        print_json(result)
        return (
            0
            if result["ok"]
            else 1
        )

    if command == "state":
        print_json(
            mastermind.snapshot()
        )
        return 0

    if command == "plan":
        owner = (
            mastermind.owner_context()
        )

        objective = ProjectObjective(
            objective_id=
                new_id("objective"),
            title=(
                "MAJD-GIT Autonomous "
                "Platform Evolution"
            ),
            description=(
                "Inspect MAJD-GIT and determine "
                "the next controlled production-ready "
                "development step without public release."
            ),
            repository_id=MAJD_PLATFORM,
            requested_by=owner.actor_id,
        )

        repository = RepositoryScope(
            repository_id=MAJD_PLATFORM,
            owner_id=owner.actor_id,
            automation_mode=
                AutomationMode.AUTONOMOUS,
            ai_enabled=True,
            allow_ai_write=True,
            allow_ai_git=True,
            allow_ai_build=True,
            allow_ai_deploy=False,
            allow_ai_self_repair=True,
        )

        result = mastermind.plan(
            actor=owner,
            objective=objective,
            repository=repository,
        )

        print_json(result)

        return (
            0
            if result.ok
            else 1
        )

    if command == "evolve":
        owner = (
            mastermind.owner_context()
        )

        goal = (
            " ".join(sys.argv[2:]).strip()
            if len(sys.argv) > 2
            else (
                "Continue controlled autonomous "
                "development of MAJD-GIT and its "
                "managed MAJD repositories. "
                "Inspect current state, determine "
                "one necessary production-ready step, "
                "execute through Executor 02, verify "
                "the result, protect OWNER_ROOT and "
                "secrets, and do not release publicly."
            )
        )

        result = (
            mastermind.evolve_platform(
                owner=owner,
                goal=goal,
            )
        )

        print_json(result)

        return (
            0
            if result.ok
            else 1
        )

    print_json(
        {
            "ok": False,
            "error": "UNKNOWN_COMMAND",
            "supported": [
                "health",
                "self-test",
                "state",
                "plan",
                "evolve",
            ],
        }
    )

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

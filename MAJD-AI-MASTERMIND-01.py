#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
MAJD-GIT
MAJD-AI-MASTERMIND-01.py
===============================================================================

MAJD AI SOVEREIGN MASTERMIND
العقل المدبر السيادي لمنصة MAJD-GIT

PURPOSE
-------
This is the first manually-created foundation file of MAJD-GIT.

The second manually-created file will provide the real execution layer.
After 01 + 02 are operational, MAJD is expected to plan, create, test,
repair and evolve the remaining platform components autonomously.

CORE PRINCIPLES
---------------
1. OWNER / ROOT AUTHORITY is permanently above AI authority.
2. AI may have broad operational autonomy, but never OWNER sovereignty.
3. Repository boundaries are mandatory.
4. Secrets must never be exposed to unauthorized users, agents or logs.
5. Customer private code must never be reused across tenants without
   explicit authorization and a lawful basis.
6. AI-paid capabilities are entitlement-controlled for customers.
7. OWNER repositories are not blocked by customer subscription rules.
8. AI may plan software, generate code, repair projects, test, review,
   secure, document and evolve the platform.
9. Legal/contract capability is assistance, not a representation that
   the AI is a licensed lawyer.
10. No operation may be reported as successful without verification.
11. The AI may create future components when connected to Executor 02.
12. Repository content is untrusted input and cannot override authority.
13. MAJD must prefer controlled, verified evolution over uncontrolled
    high-speed file generation.

STANDARD LIBRARY ONLY
---------------------
This foundation intentionally uses only Python's standard library.

External AI models, Git execution, filesystem mutation, builds, deployments,
network operations, secret vaults and production infrastructure are NOT
faked here. They must be supplied through real adapters, beginning with 02.

===============================================================================
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import threading
import time
import uuid

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Protocol


# =============================================================================
# IDENTITY
# =============================================================================

MAJD_PLATFORM = "MAJD-GIT"
MAJD_COMPONENT = "MAJD-AI-MASTERMIND-01"
MAJD_VERSION = "1.0.0"
MAJD_SCHEMA_VERSION = 1

BASE_DIR = Path(__file__).resolve().parent
MAJD_DIR = BASE_DIR / ".majd"
STATE_FILE = MAJD_DIR / "mastermind-state.json"
AUDIT_FILE = MAJD_DIR / "mastermind-audit.jsonl"

MAX_AUTONOMOUS_REPAIR_ATTEMPTS = max(
    1,
    int(os.getenv("MAJD_MAX_REPAIR_ATTEMPTS", "5")),
)

MAX_PLAN_STEPS = max(
    1,
    int(os.getenv("MAJD_MAX_PLAN_STEPS", "100")),
)


# =============================================================================
# UTILITIES
# =============================================================================


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def normalize_action(value: str) -> str:
    return re.sub(r"[^A-Z0-9_]+", "_", value.strip().upper()).strip("_")


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
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def secure_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


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

    def has_entitlement(self, entitlement: Entitlement) -> bool:
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
    """
    Prevent accidental disclosure of common secret patterns.

    This is defense-in-depth, not a replacement for a real secret vault.
    Executor 02 and future infrastructure must use proper secret references.
    """

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
        result = text

        for pattern in cls.TOKEN_PATTERNS:
            result = pattern.sub("[REDACTED_SECRET]", result)

        return result

    @classmethod
    def redact(cls, value: Any) -> Any:
        if isinstance(value, str):
            return cls.redact_text(value)

        if isinstance(value, Mapping):
            cleaned: Dict[str, Any] = {}

            for key, item in value.items():
                lowered = str(key).lower()

                if any(word in lowered for word in cls.KEYWORDS):
                    cleaned[str(key)] = "[REDACTED_SECRET]"
                else:
                    cleaned[str(key)] = cls.redact(item)

            return cleaned

        if isinstance(value, list):
            return [cls.redact(v) for v in value]

        if isinstance(value, tuple):
            return [cls.redact(v) for v in value]

        return value


# =============================================================================
# AUDIT STORAGE
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

    def append(self, event: AuditEvent) -> None:
        self.initialize()

        payload = SecretRedactor.redact(
            json_safe(event)
        )

        line = canonical_json(payload)

        with self._lock:
            with self.audit_file.open(
                "a",
                encoding="utf-8",
            ) as handle:
                handle.write(line + "\n")
                handle.flush()


# =============================================================================
# STATE STORE
# =============================================================================


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
            with self.state_file.open(
                "r",
                encoding="utf-8",
            ) as handle:
                value = json.load(handle)

            if isinstance(value, dict):
                return value

        except (OSError, json.JSONDecodeError):
            pass

        return {}

    def save(self, state: Dict[str, Any]) -> None:
        self.initialize()

        sanitized = SecretRedactor.redact(
            json_safe(state)
        )

        temp = self.state_file.with_suffix(".tmp")

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

            os.replace(temp, self.state_file)


# =============================================================================
# AUDITOR
# =============================================================================


class MajdAuditor:
    def __init__(self, store: AuditStore) -> None:
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
        event = AuditEvent(
            event_id=new_id("audit"),
            timestamp=utc_now(),
            severity=severity,
            category=category,
            action=action,
            actor_id=actor.actor_id,
            repository_id=repository_id,
            success=success,
            details=SecretRedactor.redact(details or {}),
        )

        self.store.append(event)


# =============================================================================
# EXECUTOR CONTRACT
# =============================================================================


class ExecutorAdapter(Protocol):
    """
    Contract that MAJD-AI-EXECUTOR-02.py must implement.

    Mastermind 01 intentionally does not pretend to perform filesystem,
    Git, build, network or deployment operations itself.
    """

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
    """
    Safe placeholder before Executor 02 is connected.

    It never claims execution succeeded.
    """

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
            message="Real executor is not connected.",
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
            message="Cannot verify without Executor 02.",
        )


# =============================================================================
# AI PROVIDER CONTRACT
# =============================================================================


class AIProvider(Protocol):
    """
    Future AI provider contract.

    External models may be connected later without granting them OWNER
    authority. Provider output remains untrusted until policy validation.
    """

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
    Foundation planner used before a real model provider is configured.

    It provides deterministic routing only. It does NOT claim to be a
    full external LLM.
    """

    def health(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "provider": "DETERMINISTIC_FOUNDATION",
            "external_model": False,
        }

    def reason(
        self,
        *,
        system_context: Dict[str, Any],
        objective: ProjectObjective,
        repository_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        text = (
            objective.title + " " + objective.description
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
                "hack",
                "اختراق",
                "أمن",
                "ثغرة",
            ),
            AgentDomain.LEGAL_ASSISTANT: (
                "legal",
                "law",
                "contract",
                "قانون",
                "محامي",
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
                "self",
                "autonomous",
                "توسع",
                "المنصة",
                "ذاتي",
            ),
        }

        for domain, keywords in keyword_domains.items():
            if any(keyword in text for keyword in keywords):
                if domain not in domains:
                    domains.append(domain)

        return {
            "domains": [domain.value for domain in domains],
            "summary": objective.description,
            "confidence": 0.50,
            "foundation_only": True,
        }


# =============================================================================
# AUTHORITY ENGINE
# =============================================================================


class AuthorityEngine:
    """
    OWNER_ROOT is permanently above MAJD AI.

    AI receives broad operational authority inside permitted repositories,
    but cannot modify sovereignty or obtain root-owner capabilities.
    """

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

        if actor.actor_type == ActorType.AI:
            if action in self.NEVER_AI_ACTIONS:
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

        if repository.repository_id not in actor.repository_ids:
            return Decision.DENY

        return Decision.ALLOW


# =============================================================================
# REPOSITORY ISOLATION
# =============================================================================


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

        return repository.repository_id in actor.repository_ids


# =============================================================================
# ENTITLEMENT ENGINE
# =============================================================================


class EntitlementEngine:
    """
    Customer AI capabilities are subscription/entitlement controlled.

    OWNER_ROOT is never treated as a paying customer.
    """

    ACTION_ENTITLEMENTS: Dict[str, Entitlement] = {
        "AI_ASSIST": Entitlement.AI_ASSIST,
        "GENERATE_CODE": Entitlement.AI_CODE_GENERATION,
        "PLAN_PROJECT": Entitlement.AI_PROJECT_PLANNING,
        "BUILD_PROJECT": Entitlement.AI_PROJECT_BUILD,
        "REPAIR_PROJECT": Entitlement.AI_REPAIR,
        "SECURITY_REVIEW": Entitlement.AI_SECURITY_REVIEW,
        "AUTONOMOUS_DEVELOPMENT": Entitlement.AI_AUTOMATION,
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

        if actor.has_entitlement(entitlement):
            return Decision.ALLOW

        return Decision.SUBSCRIPTION_REQUIRED


# =============================================================================
# RISK ENGINE
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

    def classify(self, text: str) -> RiskLevel:
        lowered = text.lower()

        if any(word in lowered for word in self.CRITICAL_WORDS):
            return RiskLevel.CRITICAL

        if any(word in lowered for word in self.HIGH_RISK_WORDS):
            return RiskLevel.HIGH

        if len(text) > 1000:
            return RiskLevel.MEDIUM

        return RiskLevel.LOW


# =============================================================================
# SPECIALIST REGISTRY
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

        self._register_defaults()

    def _register_defaults(self) -> None:
        profiles = [
            SpecialistProfile(
                AgentDomain.SOFTWARE_ENGINEERING,
                "Software design, implementation and repair.",
                True,
                True,
            ),
            SpecialistProfile(
                AgentDomain.ARCHITECTURE,
                "System and project architecture.",
                False,
                True,
            ),
            SpecialistProfile(
                AgentDomain.DEVOPS,
                "Build, CI/CD, deployment and operations.",
                True,
                True,
            ),
            SpecialistProfile(
                AgentDomain.QA,
                "Testing and quality verification.",
                True,
                True,
            ),
            SpecialistProfile(
                AgentDomain.CYBERSECURITY,
                "Defensive security analysis and remediation.",
                True,
                True,
            ),
            SpecialistProfile(
                AgentDomain.SECRET_PROTECTION,
                "Secret isolation and leakage prevention.",
                True,
                True,
            ),
            SpecialistProfile(
                AgentDomain.LEGAL_ASSISTANT,
                (
                    "Legal information and contract assistance; "
                    "not a representation of licensed legal counsel."
                ),
                False,
                True,
            ),
            SpecialistProfile(
                AgentDomain.CONTRACTS,
                "Contract drafting and contract workflow assistance.",
                False,
                True,
            ),
            SpecialistProfile(
                AgentDomain.IP_LICENSING,
                "IP provenance and software license analysis.",
                False,
                True,
            ),
            SpecialistProfile(
                AgentDomain.BUSINESS,
                "Business and commercial planning.",
                False,
                True,
            ),
            SpecialistProfile(
                AgentDomain.PRICING,
                "Usage-aware subscription and project pricing analysis.",
                False,
                True,
            ),
            SpecialistProfile(
                AgentDomain.GIT,
                "Repository, branch, commit and merge operations.",
                True,
                True,
            ),
            SpecialistProfile(
                AgentDomain.PLATFORM_EVOLUTION,
                "Controlled autonomous MAJD-GIT evolution.",
                True,
                True,
            ),
        ]

        for profile in profiles:
            self._profiles[profile.domain] = profile

    def get(
        self,
        domain: AgentDomain,
    ) -> SpecialistProfile:
        return self._profiles[domain]

    def all(self) -> List[SpecialistProfile]:
        return list(self._profiles.values())


# =============================================================================
# PROJECT PLANNER
# =============================================================================


class ProjectPlanner:
    """
    Converts an objective into controlled execution steps.

    A real AI provider may enrich the plan, but provider output never bypasses
    MAJD authority, repository isolation, entitlements or verification.
    """

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
        repository_context = (
            json_safe(repository)
            if repository is not None
            else {}
        )

        reasoning = self.ai_provider.reason(
            system_context={
                "platform": MAJD_PLATFORM,
                "owner_is_supreme": True,
                "secret_export_forbidden": True,
                "cross_tenant_access_forbidden": True,
                "verification_required": True,
            },
            objective=objective,
            repository_context=repository_context,
        )

        requested_domains: List[AgentDomain] = []

        for raw_domain in reasoning.get("domains", []):
            try:
                domain = AgentDomain(raw_domain)
            except ValueError:
                continue

            if domain not in requested_domains:
                requested_domains.append(domain)

        if AgentDomain.SOFTWARE_ENGINEERING not in requested_domains:
            requested_domains.insert(
                0,
                AgentDomain.SOFTWARE_ENGINEERING,
            )

        combined_text = (
            objective.title + "\n" + objective.description
        )

        overall_risk = self.risk_engine.classify(
            combined_text
        )

        steps: List[PlanStep] = []

        sequence = 1

        steps.append(
            PlanStep(
                step_id=new_id("step"),
                sequence=sequence,
                title="Understand repository and objective",
                action="ANALYZE_PROJECT",
                domain=AgentDomain.ARCHITECTURE,
                risk=RiskLevel.LOW,
                requires_executor=repository is not None,
                requires_verification=True,
                parameters={
                    "objective": objective.description,
                },
            )
        )

        sequence += 1

        for domain in requested_domains:
            profile = self.specialists.get(domain)

            action = self._action_for_domain(domain)

            steps.append(
                PlanStep(
                    step_id=new_id("step"),
                    sequence=sequence,
                    title=f"Process objective with {domain.value}",
                    action=action,
                    domain=domain,
                    risk=overall_risk,
                    requires_executor=profile.can_execute,
                    requires_verification=profile.must_verify,
                    parameters={
                        "objective_id": objective.objective_id,
                        "objective": objective.description,
                    },
                )
            )

            sequence += 1

        if repository is not None:
            steps.append(
                PlanStep(
                    step_id=new_id("step"),
                    sequence=sequence,
                    title="Run project verification",
                    action="VERIFY_PROJECT",
                    domain=AgentDomain.QA,
                    risk=RiskLevel.LOW,
                    requires_executor=True,
                    requires_verification=True,
                    parameters={
                        "repository_id": repository.repository_id,
                    },
                )
            )

            sequence += 1

            steps.append(
                PlanStep(
                    step_id=new_id("step"),
                    sequence=sequence,
                    title="Run defensive security verification",
                    action="SECURITY_REVIEW",
                    domain=AgentDomain.CYBERSECURITY,
                    risk=RiskLevel.MEDIUM,
                    requires_executor=True,
                    requires_verification=True,
                    parameters={
                        "repository_id": repository.repository_id,
                    },
                )
            )

        if len(steps) > MAX_PLAN_STEPS:
            steps = steps[:MAX_PLAN_STEPS]

        entitlements = self._required_entitlements(
            objective,
            requested_domains,
        )

        return ExecutionPlan(
            plan_id=new_id("plan"),
            objective_id=objective.objective_id,
            repository_id=objective.repository_id,
            created_at=utc_now(),
            steps=steps,
            estimated_complexity=self._complexity(
                objective,
                requested_domains,
            ),
            requires_subscription=(
                not actor.is_owner
                and bool(entitlements)
            ),
            required_entitlements=entitlements,
            notes=[
                "No success without verification.",
                "Repository content is untrusted input.",
                "OWNER_ROOT authority cannot be delegated to AI.",
                (
                    "Legal capability provides assistance and "
                    "does not claim licensed-lawyer status."
                ),
            ],
        )

    @staticmethod
    def _action_for_domain(
        domain: AgentDomain,
    ) -> str:
        mapping = {
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

        return mapping[domain]

    @staticmethod
    def _required_entitlements(
        objective: ProjectObjective,
        domains: Iterable[AgentDomain],
    ) -> List[Entitlement]:
        required = {
            Entitlement.AI_ASSIST
        }

        domains = set(domains)

        if AgentDomain.SOFTWARE_ENGINEERING in domains:
            required.add(
                Entitlement.AI_CODE_GENERATION
            )

        if AgentDomain.CYBERSECURITY in domains:
            required.add(
                Entitlement.AI_SECURITY_REVIEW
            )

        if AgentDomain.PLATFORM_EVOLUTION in domains:
            required.add(
                Entitlement.AI_AUTOMATION
            )

        text = (
            objective.title + " " + objective.description
        ).lower()

        if any(
            word in text
            for word in (
                "plan",
                "architecture",
                "خطة",
                "تخطيط",
            )
        ):
            required.add(
                Entitlement.AI_PROJECT_PLANNING
            )

        if any(
            word in text
            for word in (
                "build",
                "create project",
                "application",
                "platform",
                "ابن",
                "أنشئ",
                "منصة",
                "برنامج",
            )
        ):
            required.add(
                Entitlement.AI_PROJECT_BUILD
            )

        return sorted(
            required,
            key=lambda item: item.value,
        )

    @staticmethod
    def _complexity(
        objective: ProjectObjective,
        domains: Iterable[AgentDomain],
    ) -> int:
        text_score = min(
            50,
            max(1, len(objective.description) // 100),
        )

        domain_score = min(
            30,
            len(set(domains)) * 5,
        )

        criteria_score = min(
            20,
            len(objective.acceptance_criteria) * 2,
        )

        return min(
            100,
            text_score + domain_score + criteria_score,
        )


# =============================================================================
# PRICING ESTIMATOR
# =============================================================================


class PricingEstimator:
    """
    Provides relative complexity estimation.

    Actual SAR prices belong to the future billing/pricing component and
    OWNER-controlled commercial policy. This class does not charge money.
    """

    def estimate(
        self,
        plan: ExecutionPlan,
    ) -> Dict[str, Any]:
        complexity = plan.estimated_complexity

        if complexity <= 20:
            tier = "SMALL"
            multiplier = 1.0
        elif complexity <= 45:
            tier = "MEDIUM"
            multiplier = 2.0
        elif complexity <= 70:
            tier = "LARGE"
            multiplier = 4.0
        else:
            tier = "ENTERPRISE"
            multiplier = 8.0

        return {
            "complexity": complexity,
            "tier": tier,
            "relative_multiplier": multiplier,
            "currency": None,
            "amount": None,
            "requires_pricing_engine": True,
            "rule": (
                "Larger and more resource-intensive objectives "
                "must cost more than smaller objectives."
            ),
        }


# =============================================================================
# POLICY GUARD
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
        "كشف أسرار مستخدم آخر",
        "إلغاء المالك",
        "اعطي الذكاء صلاحية المالك",
    )

    def inspect_objective(
        self,
        objective: ProjectObjective,
    ) -> Optional[str]:
        text = (
            objective.title + "\n" + objective.description
        ).lower()

        for forbidden in self.FORBIDDEN_OBJECTIVE_PATTERNS:
            if forbidden.lower() in text:
                return (
                    "Objective conflicts with immutable "
                    "MAJD sovereignty/security policy."
                )

        return None

    def inspect_step(
        self,
        step: PlanStep,
    ) -> Optional[str]:
        action = normalize_action(step.action)

        if action in AuthorityEngine.NEVER_AI_ACTIONS:
            return (
                f"Action {action} is forbidden for AI execution."
            )

        return None


# =============================================================================
# VERIFICATION ENGINE
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
                    "all_required_verified": False,
                },
                message="No executor results were produced.",
            )

        all_ok = all(result.ok for result in results)
        all_verified = all(
            result.verified
            for result in results
            if result.ok
        )

        ok = all_ok and all_verified

        return VerificationResult(
            ok=ok,
            checks={
                "has_results": True,
                "all_operations_ok": all_ok,
                "all_required_verified": all_verified,
            },
            evidence={
                "result_count": len(results),
                "successful": sum(
                    1 for result in results if result.ok
                ),
                "verified": sum(
                    1 for result in results if result.verified
                ),
            },
            message=(
                "Execution verified."
                if ok
                else "Execution is not fully verified."
            ),
        )


# =============================================================================
# AUTONOMOUS REPAIR
# =============================================================================


class RepairController:
    def __init__(
        self,
        executor: ExecutorAdapter,
    ) -> None:
        self.executor = executor

    def attempt_repair(
        self,
        *,
        failed_request: ExecutorRequest,
        failed_result: ExecutorResult,
        actor: ActorContext,
        repository: Optional[RepositoryScope],
    ) -> ExecutorResult:
        repair_request = ExecutorRequest(
            request_id=new_id("exec"),
            operation="AUTO_REPAIR",
            repository_id=failed_request.repository_id,
            actor_id=actor.actor_id,
            authority=actor.authority,
            correlation_id=failed_request.correlation_id,
            parameters={
                "failed_operation": failed_request.operation,
                "failed_request_id": failed_request.request_id,
                "error": SecretRedactor.redact(
                    failed_result.error
                ),
                "repository": (
                    repository.repository_id
                    if repository
                    else None
                ),
            },
        )

        return self.executor.execute(
            repair_request
        )


# =============================================================================
# MAJD MASTERMIND
# =============================================================================


class MajdAIMastermind:
    """
    Central autonomous decision/orchestration layer for MAJD-GIT.

    It may plan broadly but real mutation is delegated to Executor 02.
    """

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

        self.executor: ExecutorAdapter = (
            executor or NullExecutor()
        )

        self.ai_provider: AIProvider = (
            ai_provider or DeterministicFoundationAI()
        )

        self.authority = AuthorityEngine()
        self.isolation = RepositoryIsolation()
        self.entitlements = EntitlementEngine()
        self.risk = RiskEngine()
        self.specialists = SpecialistRegistry()
        self.policy = PolicyGuard()
        self.verifier = VerificationEngine()
        self.pricing = PricingEstimator()

        self.planner = ProjectPlanner(
            ai_provider=self.ai_provider,
            risk_engine=self.risk,
            specialists=self.specialists,
        )

        self.repair = RepairController(
            self.executor
        )

        self.instance_id = new_id("mastermind")
        self.started_at: Optional[str] = None
        self._lock = threading.RLock()

    # -------------------------------------------------------------------------
    # CONTEXTS
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # START
    # -------------------------------------------------------------------------

    def start(self) -> Dict[str, Any]:
        with self._lock:
            self.state_store.initialize()
            self.audit_store.initialize()

            self.started_at = utc_now()

            state = self.snapshot()
            self.state_store.save(state)

            self.auditor.record(
                category="MASTERMIND",
                action="START",
                actor=self.ai_context(),
                repository_id=None,
                success=True,
                details={
                    "instance_id": self.instance_id,
                    "version": MAJD_VERSION,
                    "executor": self.executor.health(),
                    "ai_provider": self.ai_provider.health(),
                },
            )

            return state

    # -------------------------------------------------------------------------
    # SNAPSHOT
    # -------------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        base = {
            "identity": json_safe(self.identity),
            "instance_id": self.instance_id,
            "started_at": self.started_at,
            "timestamp": utc_now(),
            "executor": SecretRedactor.redact(
                self.executor.health()
            ),
            "ai_provider": SecretRedactor.redact(
                self.ai_provider.health()
            ),
            "authority": {
                "owner_root_supreme": True,
                "ai_can_be_owner": False,
                "cross_tenant_secret_export": False,
            },
            "specialists": [
                profile.domain.value
                for profile in self.specialists.all()
            ],
        }

        base["integrity"] = sha256_text(
            canonical_json(base)
        )

        return base

    # -------------------------------------------------------------------------
    # HEALTH
    # -------------------------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        executor_health = self.executor.health()
        ai_health = self.ai_provider.health()

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
            "full_autonomy_ready": (
                bool(executor_health.get("ok"))
                and bool(ai_health.get("ok"))
            ),
            "owner_root_protected": True,
            "timestamp": utc_now(),
        }

    # -------------------------------------------------------------------------
    # PLAN
    # -------------------------------------------------------------------------

    def plan(
        self,
        *,
        actor: ActorContext,
        objective: ProjectObjective,
        repository: Optional[RepositoryScope],
    ) -> MastermindResult:
        task_id = new_id("task")

        policy_error = self.policy.inspect_objective(
            objective
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
                message="Repository isolation denied access.",
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
                message="Authority check failed.",
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
                    "MAJD AI subscription or entitlement "
                    "is required for this customer operation."
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
            repository_id=objective.repository_id,
            success=True,
            details={
                "task_id": task_id,
                "plan_id": plan.plan_id,
                "complexity": plan.estimated_complexity,
                "pricing": self.pricing.estimate(plan),
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

    # -------------------------------------------------------------------------
    # EXECUTE OBJECTIVE
    # -------------------------------------------------------------------------

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

        if not planned.ok or planned.plan is None:
            return planned

        plan = planned.plan

        if repository is not None:
            if (
                repository.automation_mode
                == AutomationMode.ASSIST
                and not actor.is_owner
            ):
                return MastermindResult(
                    ok=True,
                    task_id=planned.task_id,
                    status=TaskStatus.READY,
                    decision=Decision.APPROVAL_REQUIRED,
                    message=(
                        "Plan is ready. Repository is in ASSIST mode; "
                        "automatic mutation is disabled."
                    ),
                    plan=plan,
                )

            if (
                repository.automation_mode
                == AutomationMode.APPROVAL
                and not actor.is_owner
            ):
                return MastermindResult(
                    ok=True,
                    task_id=planned.task_id,
                    status=TaskStatus.READY,
                    decision=Decision.APPROVAL_REQUIRED,
                    message=(
                        "Plan is ready and requires repository "
                        "approval before mutation."
                    ),
                    plan=plan,
                )

        executor_health = self.executor.health()

        executor_steps = [
            step
            for step in plan.steps
            if step.requires_executor
        ]

        if (
            executor_steps
            and not executor_health.get("ok")
        ):
            return MastermindResult(
                ok=False,
                task_id=planned.task_id,
                status=TaskStatus.BLOCKED,
                decision=Decision.EXECUTOR_REQUIRED,
                message=(
                    "Plan requires real execution. "
                    "MAJD-AI-EXECUTOR-02 is not connected yet."
                ),
                plan=plan,
            )

        results: List[ExecutorResult] = []

        for step in plan.steps:
            policy_error = self.policy.inspect_step(
                step
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
                        request_id=new_id("logical"),
                        operation=step.action,
                        verified=True,
                        changed=False,
                        message=(
                            "Logical specialist step accepted "
                            "by foundation orchestrator."
                        ),
                        data={
                            "domain": step.domain.value,
                        },
                    )
                )
                continue

            step_decision = self.authority.authorize(
                actor=actor,
                action=step.action,
                repository=repository,
            )

            if step_decision != Decision.ALLOW:
                return MastermindResult(
                    ok=False,
                    task_id=planned.task_id,
                    status=TaskStatus.BLOCKED,
                    decision=step_decision,
                    message=(
                        f"Authority denied step {step.action}."
                    ),
                    plan=plan,
                    results=results,
                )

            request = ExecutorRequest(
                request_id=new_id("exec"),
                operation=step.action,
                repository_id=objective.repository_id,
                actor_id=actor.actor_id,
                authority=actor.authority,
                parameters=SecretRedactor.redact(
                    step.parameters
                ),
                correlation_id=planned.task_id,
            )

            result = self.executor.execute(
                request
            )

            if result.ok and step.requires_verification:
                verification = self.executor.verify(
                    request,
                    result,
                )

                result.verified = verification.ok

                if not verification.ok:
                    result.ok = False
                    result.error = (
                        verification.message
                        or "VERIFICATION_FAILED"
                    )

            if not result.ok:
                repaired = self._repair_loop(
                    actor=actor,
                    repository=repository,
                    request=request,
                    failed_result=result,
                )

                results.extend(repaired)

                if not repaired or not repaired[-1].ok:
                    final_verification = (
                        self.verifier.verify_results(
                            results
                        )
                    )

                    return MastermindResult(
                        ok=False,
                        task_id=planned.task_id,
                        status=TaskStatus.FAILED,
                        decision=Decision.ALLOW,
                        message=(
                            "Execution failed and autonomous "
                            "repair did not produce a verified result."
                        ),
                        plan=plan,
                        results=results,
                        verification=final_verification,
                    )

                continue

            results.append(result)

        verification = self.verifier.verify_results(
            results
        )

        success = verification.ok

        self.auditor.record(
            category="EXECUTION",
            action="OBJECTIVE_COMPLETE",
            actor=actor,
            repository_id=objective.repository_id,
            success=success,
            severity=(
                EventSeverity.INFO
                if success
                else EventSeverity.ERROR
            ),
            details={
                "task_id": planned.task_id,
                "plan_id": plan.plan_id,
                "verification": json_safe(verification),
            },
        )

        return MastermindResult(
            ok=success,
            task_id=planned.task_id,
            status=(
                TaskStatus.SUCCEEDED
                if success
                else TaskStatus.FAILED
            ),
            decision=Decision.ALLOW,
            message=(
                "Objective completed and verified."
                if success
                else "Objective did not pass final verification."
            ),
            plan=plan,
            results=results,
            verification=verification,
        )

    # -------------------------------------------------------------------------
    # REPAIR LOOP
    # -------------------------------------------------------------------------

    def _repair_loop(
        self,
        *,
        actor: ActorContext,
        repository: Optional[RepositoryScope],
        request: ExecutorRequest,
        failed_result: ExecutorResult,
    ) -> List[ExecutorResult]:
        repair_results: List[ExecutorResult] = [
            failed_result
        ]

        if (
            repository is not None
            and not repository.allow_ai_self_repair
            and not actor.is_owner
        ):
            return repair_results

        current_failure = failed_result

        for attempt in range(
            1,
            MAX_AUTONOMOUS_REPAIR_ATTEMPTS + 1,
        ):
            repaired = self.repair.attempt_repair(
                failed_request=request,
                failed_result=current_failure,
                actor=actor,
                repository=repository,
            )

            repair_results.append(repaired)

            self.auditor.record(
                category="SELF_REPAIR",
                action="AUTO_REPAIR",
                actor=actor,
                repository_id=request.repository_id,
                success=repaired.ok,
                severity=(
                    EventSeverity.INFO
                    if repaired.ok
                    else EventSeverity.WARNING
                ),
                details={
                    "attempt": attempt,
                    "operation": request.operation,
                    "repair_request_id": repaired.request_id,
                },
            )

            if repaired.ok:
                verification_request = ExecutorRequest(
                    request_id=new_id("exec"),
                    operation="VERIFY_REPAIR",
                    repository_id=request.repository_id,
                    actor_id=actor.actor_id,
                    authority=actor.authority,
                    correlation_id=request.correlation_id,
                    parameters={
                        "original_operation":
                            request.operation,
                        "repair_request_id":
                            repaired.request_id,
                    },
                )

                verification = self.executor.verify(
                    verification_request,
                    repaired,
                )

                repaired.verified = verification.ok

                if verification.ok:
                    return repair_results

                repaired.ok = False
                repaired.error = (
                    verification.message
                    or "REPAIR_VERIFICATION_FAILED"
                )

            current_failure = repaired

        return repair_results

    # -------------------------------------------------------------------------
    # AUTONOMOUS PLATFORM EVOLUTION
    # -------------------------------------------------------------------------

    def evolve_platform(
        self,
        *,
        owner: ActorContext,
        goal: str,
    ) -> MastermindResult:
        """
        OWNER-authorized entry point for autonomous MAJD-GIT evolution.

        Once Executor 02 is connected, this can become the mechanism through
        which MAJD creates future components itself.

        OWNER sovereignty remains immutable.
        """

        if not owner.is_owner:
            return MastermindResult(
                ok=False,
                task_id=new_id("task"),
                status=TaskStatus.BLOCKED,
                decision=Decision.OWNER_REQUIRED,
                message=(
                    "Initial autonomous platform evolution "
                    "requires verified OWNER_ROOT authority."
                ),
            )

        objective = ProjectObjective(
            objective_id=new_id("objective"),
            title="Autonomous MAJD-GIT Evolution",
            description=goal,
            repository_id=MAJD_PLATFORM,
            requested_by=owner.actor_id,
            constraints=[
                "OWNER_ROOT remains supreme.",
                "Never expose secrets.",
                "Never cross tenant boundaries.",
                "Do not claim success without verification.",
                "Prefer controlled incremental evolution.",
                (
                    "Create or modify future components only "
                    "when justified by the platform objective."
                ),
            ],
            acceptance_criteria=[
                "Changes are actually created by the executor.",
                "Generated code passes available syntax/build checks.",
                "Available tests pass.",
                "Security checks pass or findings are reported.",
                "All claimed changes are verified.",
            ],
            metadata={
                "autonomous_evolution": True,
            },
        )

        repository = RepositoryScope(
            repository_id=MAJD_PLATFORM,
            owner_id=owner.actor_id,
            private=True,
            automation_mode=AutomationMode.AUTONOMOUS,
            ai_enabled=True,
            allow_ai_write=True,
            allow_ai_git=True,
            allow_ai_build=True,
            allow_ai_deploy=False,
            allow_ai_self_repair=True,
            metadata={
                "platform_repository": True,
            },
        )

        return self.execute_objective(
            actor=owner,
            objective=objective,
            repository=repository,
        )

    # -------------------------------------------------------------------------
    # SELF TEST
    # -------------------------------------------------------------------------

    def self_test(self) -> Dict[str, Any]:
        tests: Dict[str, bool] = {}

        owner = self.owner_context()
        ai = self.ai_context()

        tests["owner_root_valid"] = owner.is_owner

        tests["ai_not_owner"] = not ai.is_owner

        tests["ai_cannot_grant_itself_owner"] = (
            self.authority.authorize(
                actor=ai,
                action="GRANT_OWNER_TO_AI",
                repository=None,
            )
            == Decision.OWNER_REQUIRED
        )

        tests["owner_can_manage_owner_action"] = (
            self.authority.authorize(
                actor=owner,
                action="CHANGE_OWNER_ROOT_AUTHORITY",
                repository=None,
            )
            == Decision.ALLOW
        )

        tests["secret_redaction"] = (
            SecretRedactor.redact(
                {
                    "password": "very-secret-value",
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
            authority=AuthorityLevel.DEVELOPER,
            authenticated=True,
            repository_ids=["repo-b"],
        )

        tests["cross_repo_denied"] = (
            not self.isolation.validate(
                user_b,
                repo_a,
            )
        )

        normal_customer = ActorContext(
            actor_id="customer",
            actor_type=ActorType.HUMAN,
            authority=AuthorityLevel.CUSTOMER,
            authenticated=True,
            repository_ids=["repo-customer"],
        )

        tests["ai_subscription_enforced"] = (
            self.entitlements.check(
                normal_customer,
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

        null_health = NullExecutor().health()

        tests["null_executor_never_fake_ready"] = (
            null_health.get("ok") is False
        )

        objective = ProjectObjective(
            objective_id=new_id("test-objective"),
            title="Security test",
            description=(
                "Review repository security and Git configuration."
            ),
            repository_id="test-repo",
            requested_by=owner.actor_id,
        )

        test_repo = RepositoryScope(
            repository_id="test-repo",
            owner_id=owner.actor_id,
            automation_mode=AutomationMode.AUTONOMOUS,
            ai_enabled=True,
            allow_ai_write=True,
            allow_ai_git=True,
            allow_ai_build=True,
        )

        plan = self.planner.build_plan(
            objective=objective,
            actor=owner,
            repository=test_repo,
        )

        tests["planner_created_steps"] = (
            len(plan.steps) > 0
        )

        tests["planner_includes_security"] = any(
            step.domain == AgentDomain.CYBERSECURITY
            for step in plan.steps
        )

        passed = all(tests.values())

        result = {
            "ok": passed,
            "component": MAJD_COMPONENT,
            "tests": tests,
            "executor": self.executor.health(),
            "ai_provider": self.ai_provider.health(),
            "note": (
                "Full autonomous execution becomes available only "
                "after real Executor 02 is connected."
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
# DEMO / CLI
# =============================================================================


def print_json(value: Any) -> None:
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


def build_demo_objective(
    owner: ActorContext,
) -> ProjectObjective:
    return ProjectObjective(
        objective_id=new_id("objective"),
        title="MAJD-GIT Autonomous Platform Foundation",
        description=(
            "Analyze MAJD-GIT and prepare the controlled evolution path "
            "for AI-driven Git hosting, software generation, project "
            "planning, defensive cybersecurity, secret protection, "
            "IP/license review, contract assistance, subscriptions, "
            "dynamic pricing, developer marketplace, enterprise services, "
            "testing, repair and autonomous platform evolution."
        ),
        repository_id=MAJD_PLATFORM,
        requested_by=owner.actor_id,
        constraints=[
            "OWNER_ROOT remains above AI.",
            "Do not expose secrets.",
            "Do not cross repository boundaries.",
            "Do not fake execution.",
            "Do not fake legal authority.",
        ],
        acceptance_criteria=[
            "Plan is generated.",
            "Authority policy remains enforced.",
            "Real mutations wait for Executor 02.",
        ],
    )


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    mastermind = MajdAIMastermind()

    try:
        mastermind.start()
    except Exception as exc:
        print_json(
            {
                "ok": False,
                "component": MAJD_COMPONENT,
                "error": SecretRedactor.redact_text(
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

    if command in {"health", "status"}:
        result = mastermind.health()
        print_json(result)
        return 0 if result["ok"] else 1

    if command in {"self-test", "test"}:
        result = mastermind.self_test()
        print_json(result)
        return 0 if result["ok"] else 1

    if command == "state":
        print_json(mastermind.snapshot())
        return 0

    if command == "plan":
        owner = mastermind.owner_context()
        objective = build_demo_objective(owner)

        repository = RepositoryScope(
            repository_id=MAJD_PLATFORM,
            owner_id=owner.actor_id,
            private=True,
            automation_mode=AutomationMode.AUTONOMOUS,
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
        return 0 if result.ok else 1

    if command == "evolve":
        owner = mastermind.owner_context()

        result = mastermind.evolve_platform(
            owner=owner,
            goal=(
                "Continue building MAJD-GIT autonomously. "
                "Determine the next required platform components, "
                "create only what is justified, test every change, "
                "repair failures, preserve OWNER_ROOT authority, "
                "protect secrets and repository isolation, and never "
                "report completion without real verification."
            ),
        )

        print_json(result)

        # Before Executor 02 exists this is expected to return
        # EXECUTOR_REQUIRED rather than falsely claiming success.
        return 0 if result.ok else 1

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
    import sys

    raise SystemExit(main())

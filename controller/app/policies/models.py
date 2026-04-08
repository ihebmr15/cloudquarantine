from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field, model_validator


ActionType = Literal["auto_quarantine", "manual_review", "alert_only", "dismiss"]


class PolicyMetadata(BaseModel):
    name: str
    version: str


class SignalScores(BaseModel):
    shell_spawned: int = 0
    root_user: int = 0
    execve: int = 0
    privileged_container: int = 0
    hostpath_mount: int = 0
    secret_mount: int = 0
    sensitive_service_account: int = 0
    criticality_high: int = 0


class ScoringConfig(BaseModel):
    base_score: int = 0
    max_score: int = 100
    signals: SignalScores


class NamespaceMatch(BaseModel):
    names: List[str] = Field(default_factory=list)


class NamespaceRule(BaseModel):
    name: str
    match: NamespaceMatch
    score_boost: int = 0
    default_action: Optional[ActionType] = None


class WorkloadMatch(BaseModel):
    labels: Dict[str, str] = Field(default_factory=dict)
    privileged: Optional[bool] = None
    hostpath_used: Optional[bool] = None


class WorkloadRule(BaseModel):
    name: str
    match: WorkloadMatch
    score_boost: int = 0
    force_manual_review: bool = False


class SafetyGuards(BaseModel):
    single_replica_requires_review: bool = True
    critical_workload_requires_review: bool = True
    allow_auto_quarantine_in_namespaces: List[str] = Field(default_factory=list)
    deny_auto_quarantine_in_namespaces: List[str] = Field(default_factory=list)


class Thresholds(BaseModel):
    auto_quarantine: int
    manual_review: int
    alert_only: int

    @model_validator(mode="after")
    def validate_order(self):
        if not (self.auto_quarantine >= self.manual_review >= self.alert_only):
            raise ValueError(
                "Thresholds must follow: auto_quarantine >= manual_review >= alert_only"
            )
        return self


class ResponseProfile(BaseModel):
    label_pod: bool
    apply_network_policy: bool
    send_alert: bool
    persist_incident: bool


class ResponseProfiles(BaseModel):
    auto_quarantine: ResponseProfile
    manual_review: ResponseProfile
    alert_only: ResponseProfile
    dismiss: ResponseProfile


class PolicySpec(BaseModel):
    scoring: ScoringConfig
    namespace_rules: List[NamespaceRule] = Field(default_factory=list)
    workload_rules: List[WorkloadRule] = Field(default_factory=list)
    safety_guards: SafetyGuards
    thresholds: Thresholds
    response_profiles: ResponseProfiles


class RuntimeResponsePolicy(BaseModel):
    apiVersion: str
    kind: str
    metadata: PolicyMetadata
    spec: PolicySpec


class NormalizedEvent(BaseModel):
    rule: str
    priority: str
    output: str
    source: str = "falco"
    namespace: Optional[str] = None
    pod_name: Optional[str] = None
    container_name: Optional[str] = None
    container_id: Optional[str] = None
    user: Optional[str] = None
    evt_type: Optional[str] = None
    process_name: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    raw: Dict = Field(default_factory=dict)


class WorkloadContext(BaseModel):
    namespace: str
    pod_name: str
    labels: Dict[str, str] = Field(default_factory=dict)
    service_account: Optional[str] = None
    privileged: bool = False
    hostpath_used: bool = False
    secret_mount: bool = False
    criticality: Optional[str] = None
    replicas: Optional[int] = None
    owner_kind: Optional[str] = None
    owner_name: Optional[str] = None


class PolicyDecision(BaseModel):
    score: int
    action: ActionType
    reasons: List[str] = Field(default_factory=list)
    matched_rules: List[str] = Field(default_factory=list)
    safety_blocks: List[str] = Field(default_factory=list)
    response_profile: Dict = Field(default_factory=dict)
    policy_name: str
    policy_version: str

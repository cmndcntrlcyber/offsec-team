"""
Security-specific data models for cybersecurity AI workflow integration.

This module contains data structures for vulnerabilities, security findings, and risk assessments.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator

from .base_models import IdentifiedModel, SeverityLevel


class ComplianceStatus(str, Enum):
    """Compliance status enumeration."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_TESTED = "not_tested"
    NOT_APPLICABLE = "not_applicable"


class Vulnerability(IdentifiedModel):
    """Vulnerability information model."""
    
    vulnerability_id: str = Field(..., description="Unique vulnerability identifier")
    title: str = Field(..., description="Vulnerability title")
    severity: SeverityLevel = Field(..., description="Vulnerability severity")
    cvss_score: Optional[float] = Field(default=None, description="CVSS base score")
    cvss_vector: Optional[str] = Field(default=None, description="CVSS vector string")
    cve_id: Optional[str] = Field(default=None, description="CVE identifier if applicable")
    cwe_id: Optional[str] = Field(default=None, description="CWE identifier")
    affected_component: str = Field(..., description="Affected system component")
    vulnerability_type: str = Field(..., description="Type of vulnerability")
    discovery_method: str = Field(..., description="How the vulnerability was discovered")
    proof_of_concept: Optional[str] = Field(default=None, description="Proof of concept or reproduction steps")
    impact_description: str = Field(..., description="Description of potential impact")
    remediation_steps: List[str] = Field(default_factory=list, description="Steps to remediate the vulnerability")
    references: List[str] = Field(default_factory=list, description="External references")
    discovered_by: Optional[str] = Field(default=None, description="Tool or person who discovered it")
    verified: bool = Field(default=False, description="Whether vulnerability has been verified")
    false_positive: bool = Field(default=False, description="Whether this is a false positive")
    
    @validator('cvss_score')
    def validate_cvss_score(cls, v):
        if v is not None and not 0.0 <= v <= 10.0:
            raise ValueError('CVSS score must be between 0.0 and 10.0')
        return v
    
    @validator('cve_id')
    def validate_cve_id(cls, v):
        if v and not v.startswith('CVE-'):
            raise ValueError('CVE ID must start with CVE-')
        return v
    
    @validator('cwe_id')
    def validate_cwe_id(cls, v):
        if v and not v.startswith('CWE-'):
            raise ValueError('CWE ID must start with CWE-')
        return v
    
    def mark_verified(self, verified_by: str):
        """Mark vulnerability as verified."""
        self.verified = True
        self.metadata["verified_by"] = verified_by
        self.metadata["verified_at"] = datetime.utcnow().isoformat()
        self.update_timestamp()
    
    def mark_false_positive(self, reason: str, marked_by: str):
        """Mark vulnerability as false positive."""
        self.false_positive = True
        self.metadata["false_positive_reason"] = reason
        self.metadata["marked_by"] = marked_by
        self.metadata["marked_at"] = datetime.utcnow().isoformat()
        self.update_timestamp()


class SecurityFinding(IdentifiedModel):
    """General security finding model."""
    
    finding_type: str = Field(..., description="Type of security finding")
    severity: SeverityLevel = Field(..., description="Finding severity")
    confidence: str = Field(..., description="Confidence level (high, medium, low)")
    affected_asset: str = Field(..., description="Affected asset or system")
    location: str = Field(..., description="Location where finding was identified")
    evidence: List[Dict[str, Any]] = Field(default_factory=list, description="Supporting evidence")
    impact_analysis: str = Field(..., description="Analysis of potential impact")
    recommendation: str = Field(..., description="Recommended remediation action")
    status: str = Field(default="open", description="Finding status")
    assigned_to: Optional[str] = Field(default=None, description="Person assigned to address finding")
    due_date: Optional[datetime] = Field(default=None, description="Due date for remediation")
    effort_estimate: Optional[str] = Field(default=None, description="Estimated effort to fix")
    business_risk: Optional[str] = Field(default=None, description="Business risk assessment")
    technical_risk: Optional[str] = Field(default=None, description="Technical risk assessment")
    exploitability: Optional[str] = Field(default=None, description="Exploitability assessment")
    
    @validator('confidence')
    def validate_confidence(cls, v):
        allowed_values = ['high', 'medium', 'low']
        if v not in allowed_values:
            raise ValueError(f'Confidence must be one of: {", ".join(allowed_values)}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['open', 'in_progress', 'resolved', 'accepted_risk', 'false_positive']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v
    
    def add_evidence(self, evidence_type: str, content: str, source: Optional[str] = None):
        """Add evidence to the finding."""
        evidence_item = {
            "type": evidence_type,
            "content": content,
            "source": source,
            "added_at": datetime.utcnow().isoformat()
        }
        self.evidence.append(evidence_item)
        self.update_timestamp()
    
    def assign_finding(self, assignee: str, due_date: Optional[datetime] = None):
        """Assign finding to someone."""
        self.assigned_to = assignee
        self.due_date = due_date
        self.status = "in_progress"
        self.metadata["assigned_at"] = datetime.utcnow().isoformat()
        self.update_timestamp()
    
    def resolve_finding(self, resolution_note: str, resolved_by: str):
        """Mark finding as resolved."""
        self.status = "resolved"
        self.metadata["resolution_note"] = resolution_note
        self.metadata["resolved_by"] = resolved_by
        self.metadata["resolved_at"] = datetime.utcnow().isoformat()
        self.update_timestamp()


class RiskAssessment(IdentifiedModel):
    """Risk assessment model."""
    
    asset_name: str = Field(..., description="Name of the assessed asset")
    asset_type: str = Field(..., description="Type of asset")
    threat_model: Dict[str, Any] = Field(..., description="Threat model information")
    vulnerabilities: List[str] = Field(default_factory=list, description="List of vulnerability IDs")
    risk_score: float = Field(..., description="Overall risk score")
    risk_level: str = Field(..., description="Risk level (critical, high, medium, low)")
    likelihood: str = Field(..., description="Likelihood of exploitation")
    impact: str = Field(..., description="Potential impact")
    risk_factors: List[Dict[str, Any]] = Field(default_factory=list, description="Contributing risk factors")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Risk mitigation strategies")
    residual_risk: Optional[float] = Field(default=None, description="Residual risk after mitigation")
    assessment_methodology: str = Field(..., description="Risk assessment methodology used")
    assessor: str = Field(..., description="Person who performed the assessment")
    review_date: Optional[datetime] = Field(default=None, description="Next review date")
    approval_status: str = Field(default="pending", description="Approval status")
    approved_by: Optional[str] = Field(default=None, description="Person who approved the assessment")
    
    @validator('risk_score')
    def validate_risk_score(cls, v):
        if not 0.0 <= v <= 10.0:
            raise ValueError('Risk score must be between 0.0 and 10.0')
        return v
    
    @validator('risk_level')
    def validate_risk_level(cls, v):
        allowed_levels = ['critical', 'high', 'medium', 'low']
        if v not in allowed_levels:
            raise ValueError(f'Risk level must be one of: {", ".join(allowed_levels)}')
        return v
    
    @validator('approval_status')
    def validate_approval_status(cls, v):
        allowed_statuses = ['pending', 'approved', 'rejected', 'needs_revision']
        if v not in allowed_statuses:
            raise ValueError(f'Approval status must be one of: {", ".join(allowed_statuses)}')
        return v
    
    def add_vulnerability(self, vulnerability_id: str):
        """Add a vulnerability to the risk assessment."""
        if vulnerability_id not in self.vulnerabilities:
            self.vulnerabilities.append(vulnerability_id)
            self.update_timestamp()
    
    def approve_assessment(self, approver: str, review_date: Optional[datetime] = None):
        """Approve the risk assessment."""
        self.approval_status = "approved"
        self.approved_by = approver
        self.review_date = review_date
        self.metadata["approved_at"] = datetime.utcnow().isoformat()
        self.update_timestamp()


class ScanResult(IdentifiedModel):
    """Security scan result model."""
    
    scan_type: str = Field(..., description="Type of security scan")
    target: str = Field(..., description="Scan target")
    scanner: str = Field(..., description="Scanner tool used")
    scan_policy: Optional[str] = Field(default=None, description="Scan policy used")
    start_time: datetime = Field(..., description="Scan start time")
    end_time: Optional[datetime] = Field(default=None, description="Scan completion time")
    duration: Optional[int] = Field(default=None, description="Scan duration in seconds")
    status: str = Field(default="running", description="Scan status")
    findings_count: Dict[str, int] = Field(default_factory=dict, description="Count of findings by severity")
    vulnerabilities: List[str] = Field(default_factory=list, description="List of vulnerability IDs found")
    false_positives: List[str] = Field(default_factory=list, description="List of false positive IDs")
    scan_coverage: Dict[str, Any] = Field(default_factory=dict, description="Scan coverage information")
    performance_metrics: Dict[str, Union[int, float]] = Field(default_factory=dict, description="Performance metrics")
    raw_output: Optional[str] = Field(default=None, description="Raw scanner output")
    error_messages: List[str] = Field(default_factory=list, description="Any error messages")
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['pending', 'running', 'completed', 'failed', 'cancelled']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v
    
    def complete_scan(self):
        """Mark scan as completed."""
        self.status = "completed"
        self.end_time = datetime.utcnow()
        if self.start_time:
            duration_delta = self.end_time - self.start_time
            self.duration = int(duration_delta.total_seconds())
        self.update_timestamp()
    
    def add_finding(self, vulnerability_id: str, severity: str):
        """Add a finding to the scan result."""
        if vulnerability_id not in self.vulnerabilities:
            self.vulnerabilities.append(vulnerability_id)
            
        # Update findings count
        if severity in self.findings_count:
            self.findings_count[severity] += 1
        else:
            self.findings_count[severity] = 1
        
        self.update_timestamp()
    
    def mark_false_positive(self, vulnerability_id: str):
        """Mark a finding as false positive."""
        if vulnerability_id in self.vulnerabilities and vulnerability_id not in self.false_positives:
            self.false_positives.append(vulnerability_id)
            self.update_timestamp()


class ThreatIntelligence(IdentifiedModel):
    """Threat intelligence information model."""
    
    threat_type: str = Field(..., description="Type of threat")
    threat_actor: Optional[str] = Field(default=None, description="Threat actor or group")
    ioc_type: str = Field(..., description="Indicator of compromise type")
    indicator_value: str = Field(..., description="The actual indicator value")
    confidence_level: str = Field(..., description="Confidence in the intelligence")
    first_seen: datetime = Field(..., description="First time this indicator was seen")
    last_seen: Optional[datetime] = Field(default=None, description="Last time this indicator was seen")
    source: str = Field(..., description="Intelligence source")
    tlp_marking: str = Field(default="TLP:WHITE", description="Traffic Light Protocol marking")
    malware_family: Optional[str] = Field(default=None, description="Associated malware family")
    campaign: Optional[str] = Field(default=None, description="Associated campaign")
    country: Optional[str] = Field(default=None, description="Associated country")
    context: str = Field(..., description="Context about the threat")
    references: List[str] = Field(default_factory=list, description="External references")
    is_active: bool = Field(default=True, description="Whether threat is currently active")
    
    @validator('confidence_level')
    def validate_confidence_level(cls, v):
        allowed_levels = ['high', 'medium', 'low', 'unknown']
        if v not in allowed_levels:
            raise ValueError(f'Confidence level must be one of: {", ".join(allowed_levels)}')
        return v
    
    @validator('tlp_marking')
    def validate_tlp_marking(cls, v):
        allowed_markings = ['TLP:RED', 'TLP:AMBER', 'TLP:GREEN', 'TLP:WHITE']
        if v not in allowed_markings:
            raise ValueError(f'TLP marking must be one of: {", ".join(allowed_markings)}')
        return v
    
    @validator('ioc_type')
    def validate_ioc_type(cls, v):
        allowed_types = [
            'ip_address', 'domain', 'url', 'file_hash', 'email', 
            'registry_key', 'mutex', 'user_agent', 'certificate'
        ]
        if v not in allowed_types:
            raise ValueError(f'IOC type must be one of: {", ".join(allowed_types)}')
        return v
    
    def update_last_seen(self):
        """Update the last seen timestamp."""
        self.last_seen = datetime.utcnow()
        self.update_timestamp()
    
    def deactivate(self, reason: str):
        """Deactivate the threat intelligence."""
        self.is_active = False
        self.metadata["deactivation_reason"] = reason
        self.metadata["deactivated_at"] = datetime.utcnow().isoformat()
        self.update_timestamp()


class ComplianceCheck(IdentifiedModel):
    """Compliance check model."""
    
    framework: str = Field(..., description="Compliance framework (e.g., ISO27001, NIST, SOC2)")
    control_id: str = Field(..., description="Control identifier")
    control_title: str = Field(..., description="Control title")
    requirement_description: str = Field(..., description="Description of the requirement")
    implementation_status: str = Field(..., description="Implementation status")
    compliance_status: str = Field(..., description="Compliance status")
    test_procedure: str = Field(..., description="Test procedure used")
    evidence: List[Dict[str, Any]] = Field(default_factory=list, description="Evidence of compliance")
    gaps_identified: List[str] = Field(default_factory=list, description="Identified compliance gaps")
    remediation_plan: Optional[str] = Field(default=None, description="Plan to address gaps")
    responsible_party: str = Field(..., description="Person/team responsible")
    review_date: datetime = Field(..., description="Date of compliance review")
    next_review_date: Optional[datetime] = Field(default=None, description="Next scheduled review")
    assessor: str = Field(..., description="Person who performed the assessment")
    reviewer: Optional[str] = Field(default=None, description="Person who reviewed the assessment")
    
    @validator('implementation_status')
    def validate_implementation_status(cls, v):
        allowed_statuses = ['implemented', 'partially_implemented', 'not_implemented', 'not_applicable']
        if v not in allowed_statuses:
            raise ValueError(f'Implementation status must be one of: {", ".join(allowed_statuses)}')
        return v
    
    @validator('compliance_status')
    def validate_compliance_status(cls, v):
        allowed_statuses = ['compliant', 'non_compliant', 'partially_compliant', 'not_tested']
        if v not in allowed_statuses:
            raise ValueError(f'Compliance status must be one of: {", ".join(allowed_statuses)}')
        return v
    
    def add_evidence_item(self, evidence_type: str, description: str, file_path: Optional[str] = None):
        """Add evidence to the compliance check."""
        evidence_item = {
            "type": evidence_type,
            "description": description,
            "file_path": file_path,
            "added_at": datetime.utcnow().isoformat()
        }
        self.evidence.append(evidence_item)
        self.update_timestamp()
    
    def add_gap(self, gap_description: str):
        """Add a compliance gap."""
        if gap_description not in self.gaps_identified:
            self.gaps_identified.append(gap_description)
            self.update_timestamp()
    
    def mark_compliant(self, reviewer: str, next_review: Optional[datetime] = None):
        """Mark the control as compliant."""
        self.compliance_status = "compliant"
        self.reviewer = reviewer
        self.next_review_date = next_review
        self.metadata["marked_compliant_at"] = datetime.utcnow().isoformat()
        self.update_timestamp()


class VulnerabilityReport(IdentifiedModel):
    """Comprehensive vulnerability report model."""
    
    scan_target: str = Field(..., description="Target that was scanned")
    report_type: str = Field(default="vulnerability_assessment", description="Type of report")
    executive_summary: str = Field(..., description="Executive summary of findings")
    methodology: str = Field(..., description="Testing methodology used")
    scope: List[str] = Field(..., description="Scope of the assessment")
    vulnerabilities: List[str] = Field(default_factory=list, description="List of vulnerability IDs")
    findings_summary: Dict[str, int] = Field(default_factory=dict, description="Summary of findings by severity")
    risk_rating: str = Field(..., description="Overall risk rating")
    recommendations: List[str] = Field(default_factory=list, description="High-level recommendations")
    scan_metadata: Dict[str, Any] = Field(default_factory=dict, description="Scan metadata and configuration")
    tools_used: List[str] = Field(default_factory=list, description="Tools used in assessment")
    assessor: str = Field(..., description="Person who performed the assessment")
    reviewer: Optional[str] = Field(default=None, description="Person who reviewed the report")
    report_status: str = Field(default="draft", description="Report status")
    
    @validator('risk_rating')
    def validate_risk_rating(cls, v):
        allowed_ratings = ['critical', 'high', 'medium', 'low']
        if v not in allowed_ratings:
            raise ValueError(f'Risk rating must be one of: {", ".join(allowed_ratings)}')
        return v
    
    @validator('report_status')
    def validate_report_status(cls, v):
        allowed_statuses = ['draft', 'review', 'final', 'published']
        if v not in allowed_statuses:
            raise ValueError(f'Report status must be one of: {", ".join(allowed_statuses)}')
        return v
    
    def add_vulnerability(self, vulnerability_id: str, severity: str):
        """Add a vulnerability to the report."""
        if vulnerability_id not in self.vulnerabilities:
            self.vulnerabilities.append(vulnerability_id)
            
        # Update findings summary
        if severity in self.findings_summary:
            self.findings_summary[severity] += 1
        else:
            self.findings_summary[severity] = 1
        
        self.update_timestamp()
    
    def finalize_report(self, reviewer: str):
        """Finalize the report."""
        self.report_status = "final"
        self.reviewer = reviewer
        self.metadata["finalized_at"] = datetime.utcnow().isoformat()
        self.update_timestamp()


class SecurityPolicy(IdentifiedModel):
    """Security policy model."""
    
    policy_type: str = Field(..., description="Type of security policy")
    policy_category: str = Field(..., description="Policy category")
    version: str = Field(..., description="Policy version")
    effective_date: datetime = Field(..., description="When policy becomes effective")
    expiration_date: Optional[datetime] = Field(default=None, description="When policy expires")
    approval_authority: str = Field(..., description="Authority who approved the policy")
    policy_content: str = Field(..., description="Full policy content")
    objectives: List[str] = Field(..., description="Policy objectives")
    scope: List[str] = Field(..., description="Policy scope")
    roles_responsibilities: Dict[str, List[str]] = Field(default_factory=dict, description="Roles and responsibilities")
    compliance_requirements: List[str] = Field(default_factory=list, description="Related compliance requirements")
    enforcement_actions: List[str] = Field(default_factory=list, description="Enforcement actions for violations")
    exceptions: List[Dict[str, Any]] = Field(default_factory=list, description="Policy exceptions")
    review_schedule: str = Field(..., description="Review schedule (e.g., annually)")
    owner: str = Field(..., description="Policy owner")
    stakeholders: List[str] = Field(default_factory=list, description="Policy stakeholders")
    
    @validator('policy_type')
    def validate_policy_type(cls, v):
        allowed_types = [
            'access_control', 'data_classification', 'incident_response', 
            'security_awareness', 'vulnerability_management', 'encryption',
            'network_security', 'physical_security', 'business_continuity'
        ]
        if v not in allowed_types:
            raise ValueError(f'Policy type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('policy_category')
    def validate_policy_category(cls, v):
        allowed_categories = ['technical', 'administrative', 'physical']
        if v not in allowed_categories:
            raise ValueError(f'Policy category must be one of: {", ".join(allowed_categories)}')
        return v
    
    def add_exception(self, exception_type: str, justification: str, approved_by: str, expiration: Optional[datetime] = None):
        """Add a policy exception."""
        exception = {
            "type": exception_type,
            "justification": justification,
            "approved_by": approved_by,
            "approved_at": datetime.utcnow().isoformat(),
            "expires_at": expiration.isoformat() if expiration else None
        }
        self.exceptions.append(exception)
        self.update_timestamp()
    
    def assign_role_responsibility(self, role: str, responsibilities: List[str]):
        """Assign responsibilities to a role."""
        self.roles_responsibilities[role] = responsibilities
        self.update_timestamp()


class PolicyViolation(IdentifiedModel):
    """Policy violation model."""
    
    policy_id: str = Field(..., description="ID of the violated policy")
    violation_type: str = Field(..., description="Type of policy violation")
    severity: SeverityLevel = Field(..., description="Violation severity")
    violating_entity: str = Field(..., description="Entity that violated the policy")
    violation_details: str = Field(..., description="Details of the violation")
    detected_by: str = Field(..., description="System or person that detected the violation")
    detection_method: str = Field(..., description="Method used to detect the violation")
    evidence: List[Dict[str, Any]] = Field(default_factory=list, description="Evidence of the violation")
    impact_assessment: str = Field(..., description="Assessment of violation impact")
    remediation_required: bool = Field(default=True, description="Whether remediation is required")
    remediation_steps: List[str] = Field(default_factory=list, description="Steps to remediate the violation")
    status: str = Field(default="open", description="Violation status")
    assigned_to: Optional[str] = Field(default=None, description="Person assigned to address violation")
    resolution_note: Optional[str] = Field(default=None, description="Resolution notes")
    resolved_by: Optional[str] = Field(default=None, description="Person who resolved the violation")
    resolved_at: Optional[datetime] = Field(default=None, description="Resolution timestamp")
    
    @validator('violation_type')
    def validate_violation_type(cls, v):
        allowed_types = [
            'access_control_violation', 'data_handling_violation', 'security_control_bypass',
            'unauthorized_access', 'policy_non_compliance', 'configuration_violation'
        ]
        if v not in allowed_types:
            raise ValueError(f'Violation type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['open', 'in_progress', 'resolved', 'accepted_risk', 'false_positive']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v
    
    def assign_violation(self, assignee: str):
        """Assign violation to someone for resolution."""
        self.assigned_to = assignee
        self.status = "in_progress"
        self.metadata["assigned_at"] = datetime.utcnow().isoformat()
        self.update_timestamp()
    
    def resolve_violation(self, resolution_note: str, resolved_by: str):
        """Mark violation as resolved."""
        self.status = "resolved"
        self.resolution_note = resolution_note
        self.resolved_by = resolved_by
        self.resolved_at = datetime.utcnow()
        self.update_timestamp()
    
    def add_remediation_step(self, step: str):
        """Add a remediation step."""
        if step not in self.remediation_steps:
            self.remediation_steps.append(step)
            self.update_timestamp()

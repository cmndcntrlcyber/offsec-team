"""
Collaboration Manager for cybersecurity AI workflow integration.

This tool manages inter-agent communication, shared context,
collaboration sessions, and knowledge sharing coordination.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..shared.data_models.workflow_models import CollaborationSession, AgentRole
from ..shared.api_clients.mcp_nexus_client import MCPNexusClient
from ..shared.api_clients.rtpi_pen_client import RTPIPenClient
from ..shared.api_clients.attack_node_client import AttackNodeClient


class CollaborationManager:
    """
    Advanced collaboration management system for multi-agent coordination.
    Provides communication, context sharing, session management, and knowledge coordination.
    """
    
    def __init__(self):
        """Initialize the Collaboration Manager."""
        self.mcp_client = MCPNexusClient("http://localhost:3000")
        self.rtpi_client = RTPIPenClient("http://localhost:8080")
        self.attack_client = AttackNodeClient("http://localhost:5000")
        self.logger = logging.getLogger("CollaborationManager")
        
        self.active_sessions = {}
        self.communication_channels = {}
        self.shared_knowledge_base = {}
        self.collaboration_history = []
        
        # Initialize collaboration infrastructure
        self._initialize_collaboration_system()
    
    def establish_collaboration_session(self, session_name: str = Field(..., description="Name of the collaboration session"),
                                      participants: List[str] = Field(..., description="List of participating agent roles"),
                                      session_type: str = Field(..., description="Type of collaboration session"),
                                      objective: str = Field(..., description="Session objective"),
                                      session_config: Dict[str, Any] = Field(default_factory=dict, description="Session configuration")) -> Dict[str, Any]:
        """
        Establish a collaboration session between multiple agents.
        
        Args:
            session_name: Name for the collaboration session
            participants: List of agent roles to participate
            session_type: Type of collaboration (investigation, assessment, development)
            objective: Main objective of the collaboration
            session_config: Additional session configuration
            
        Returns:
            Collaboration session establishment results
        """
        try:
            session_id = f"collab-{int(datetime.utcnow().timestamp())}"
            
            # Validate participants
            valid_participants = []
            for participant in participants:
                try:
                    agent_role = AgentRole(participant)
                    valid_participants.append(agent_role)
                except ValueError:
                    self.logger.warning(f"Invalid agent role: {participant}")
            
            if not valid_participants:
                return {
                    "success": False,
                    "error": "No valid participants specified"
                }
            
            # Create collaboration session
            session = CollaborationSession(
                id=session_id,
                session_name=session_name,
                participants=valid_participants,
                session_type=session_type,
                objective=objective,
                created_by="system"
            )
            
            # Initialize session context
            session.shared_context.update({
                "session_config": session_config,
                "coordination_rules": self._get_default_coordination_rules(session_type),
                "communication_preferences": self._get_communication_preferences(valid_participants)
            })
            
            # Store session
            self.active_sessions[session_id] = session
            
            # Create communication channels
            self._setup_communication_channels(session_id, valid_participants)
            
            # Initialize shared knowledge space
            self._initialize_shared_knowledge_space(session_id)
            
            # Notify participants
            for participant in valid_participants:
                session.add_message(
                    AgentRole.NEXUS_KAMUY,
                    f"Collaboration session '{session_name}' established. Objective: {objective}",
                    "session_start"
                )
            
            self.logger.info(f"Collaboration session established: {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "session": session.dict(),
                "participants": [p.value for p in valid_participants],
                "communication_channels": self.communication_channels.get(session_id, {}),
                "shared_context_initialized": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to establish collaboration session: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def facilitate_knowledge_sharing(self, session_id: str = Field(..., description="Collaboration session ID"),
                                   knowledge_item: Dict[str, Any] = Field(..., description="Knowledge item to share"),
                                   sharing_agent: str = Field(..., description="Agent sharing the knowledge")) -> Dict[str, Any]:
        """
        Facilitate knowledge sharing between agents in a session.
        
        Args:
            session_id: Collaboration session identifier
            knowledge_item: Knowledge item to be shared
            sharing_agent: Agent role sharing the knowledge
            
        Returns:
            Knowledge sharing results
        """
        try:
            if session_id not in self.active_sessions:
                return {"success": False, "error": f"Session {session_id} not found"}
            
            session = self.active_sessions[session_id]
            
            # Validate sharing agent
            try:
                agent_role = AgentRole(sharing_agent)
                if agent_role not in session.participants:
                    return {
                        "success": False,
                        "error": f"Agent {sharing_agent} is not a participant in this session"
                    }
            except ValueError:
                return {"success": False, "error": f"Invalid agent role: {sharing_agent}"}
            
            knowledge_id = f"knowledge-{int(datetime.utcnow().timestamp())}"
            
            # Process knowledge item
            processed_knowledge = {
                "knowledge_id": knowledge_id,
                "shared_by": sharing_agent,
                "shared_at": datetime.utcnow().isoformat(),
                "knowledge_type": knowledge_item.get("type", "general"),
                "title": knowledge_item.get("title", "Untitled Knowledge"),
                "content": knowledge_item.get("content", {}),
                "tags": knowledge_item.get("tags", []),
                "relevance_score": self._calculate_relevance_score(knowledge_item, session),
                "access_level": knowledge_item.get("access_level", "session"),
                "expiration": knowledge_item.get("expiration")
            }
            
            # Store in shared knowledge base
            if session_id not in self.shared_knowledge_base:
                self.shared_knowledge_base[session_id] = {}
            
            self.shared_knowledge_base[session_id][knowledge_id] = processed_knowledge
            
            # Update session shared context
            session.update_shared_context(
                f"knowledge_{knowledge_id}",
                processed_knowledge,
                agent_role
            )
            
            # Notify other participants
            notification_message = f"New knowledge shared: {processed_knowledge['title']} (Type: {processed_knowledge['knowledge_type']})"
            session.add_message(agent_role, notification_message, "knowledge_share")
            
            # Distribute to relevant agents
            distribution_result = self._distribute_knowledge_to_agents(
                session, processed_knowledge, agent_role
            )
            
            self.logger.info(f"Knowledge shared in session {session_id}: {knowledge_id}")
            
            return {
                "success": True,
                "knowledge_id": knowledge_id,
                "session_id": session_id,
                "processed_knowledge": processed_knowledge,
                "distribution_result": distribution_result,
                "relevance_score": processed_knowledge["relevance_score"]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to facilitate knowledge sharing: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def manage_shared_context(self, session_id: str = Field(..., description="Session ID"),
                            context_updates: Dict[str, Any] = Field(..., description="Context updates"),
                            updating_agent: str = Field(..., description="Agent making the updates")) -> Dict[str, Any]:
        """
        Manage shared context between collaborating agents.
        
        Args:
            session_id: Session identifier
            context_updates: Updates to apply to shared context
            updating_agent: Agent making the updates
            
        Returns:
            Context management results
        """
        try:
            if session_id not in self.active_sessions:
                return {"success": False, "error": f"Session {session_id} not found"}
            
            session = self.active_sessions[session_id]
            
            # Validate updating agent
            try:
                agent_role = AgentRole(updating_agent)
                if agent_role not in session.participants:
                    return {
                        "success": False,
                        "error": f"Agent {updating_agent} is not a participant in this session"
                    }
            except ValueError:
                return {"success": False, "error": f"Invalid agent role: {updating_agent}"}
            
            context_result = {
                "session_id": session_id,
                "update_id": f"ctx-update-{int(datetime.utcnow().timestamp())}",
                "updating_agent": updating_agent,
                "updated_at": datetime.utcnow().isoformat(),
                "successful_updates": 0,
                "failed_updates": 0,
                "update_details": []
            }
            
            # Apply context updates
            for key, value in context_updates.items():
                try:
                    # Validate context update
                    validation_result = self._validate_context_update(key, value, session)
                    
                    if validation_result["valid"]:
                        session.update_shared_context(key, value, agent_role)
                        context_result["successful_updates"] += 1
                        context_result["update_details"].append({
                            "key": key,
                            "success": True,
                            "validation": validation_result
                        })
                        
                        # Log context update
                        session.add_message(
                            agent_role,
                            f"Updated shared context: {key}",
                            "context_update"
                        )
                    else:
                        context_result["failed_updates"] += 1
                        context_result["update_details"].append({
                            "key": key,
                            "success": False,
                            "error": validation_result["error"],
                            "validation": validation_result
                        })
                
                except Exception as e:
                    context_result["failed_updates"] += 1
                    context_result["update_details"].append({
                        "key": key,
                        "success": False,
                        "error": str(e)
                    })
            
            # Synchronize context across platforms
            sync_result = self._synchronize_context_across_platforms(session_id, context_updates)
            context_result["platform_sync"] = sync_result
            
            return {
                "success": context_result["successful_updates"] > 0,
                "context_result": context_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to manage shared context: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def coordinate_agent_communication(self, session_id: str = Field(..., description="Session ID"),
                                     sender: str = Field(..., description="Sending agent role"),
                                     recipients: List[str] = Field(..., description="Recipient agent roles"),
                                     message: Dict[str, Any] = Field(..., description="Message to send")) -> Dict[str, Any]:
        """
        Coordinate communication between agents in a collaboration session.
        
        Args:
            session_id: Session identifier
            sender: Sending agent role
            recipients: List of recipient agent roles
            message: Message content and metadata
            
        Returns:
            Communication coordination results
        """
        try:
            if session_id not in self.active_sessions:
                return {"success": False, "error": f"Session {session_id} not found"}
            
            session = self.active_sessions[session_id]
            
            # Validate sender
            try:
                sender_role = AgentRole(sender)
                if sender_role not in session.participants:
                    return {
                        "success": False,
                        "error": f"Sender {sender} is not a participant in this session"
                    }
            except ValueError:
                return {"success": False, "error": f"Invalid sender role: {sender}"}
            
            # Validate recipients
            valid_recipients = []
            for recipient in recipients:
                try:
                    recipient_role = AgentRole(recipient)
                    if recipient_role in session.participants:
                        valid_recipients.append(recipient_role)
                    else:
                        self.logger.warning(f"Recipient {recipient} not in session {session_id}")
                except ValueError:
                    self.logger.warning(f"Invalid recipient role: {recipient}")
            
            if not valid_recipients:
                return {
                    "success": False,
                    "error": "No valid recipients specified"
                }
            
            communication_result = {
                "message_id": f"msg-{int(datetime.utcnow().timestamp())}",
                "session_id": session_id,
                "sender": sender,
                "recipients": [r.value for r in valid_recipients],
                "sent_at": datetime.utcnow().isoformat(),
                "message_type": message.get("type", "general"),
                "delivery_status": {},
                "communication_success": True
            }
            
            # Process message content
            processed_message = {
                "id": communication_result["message_id"],
                "content": message.get("content", ""),
                "attachments": message.get("attachments", []),
                "priority": message.get("priority", "normal"),
                "requires_response": message.get("requires_response", False),
                "context_references": message.get("context_references", [])
            }
            
            # Deliver message to recipients
            for recipient in valid_recipients:
                delivery_result = self._deliver_message_to_agent(
                    session_id, sender_role, recipient, processed_message
                )
                communication_result["delivery_status"][recipient.value] = delivery_result
                
                if not delivery_result["delivered"]:
                    communication_result["communication_success"] = False
            
            # Log communication in session
            session.add_message(
                sender_role,
                f"Sent message to {', '.join([r.value for r in valid_recipients])}: {processed_message['content'][:100]}...",
                "inter_agent_communication"
            )
            
            # Update communication statistics
            self._update_communication_statistics(session_id, communication_result)
            
            return {
                "success": communication_result["communication_success"],
                "communication_result": communication_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to coordinate agent communication: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def synchronize_session_data(self, session_id: str = Field(..., description="Session ID to synchronize")) -> Dict[str, Any]:
        """
        Synchronize session data across all platforms and participants.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Synchronization results
        """
        try:
            if session_id not in self.active_sessions:
                return {"success": False, "error": f"Session {session_id} not found"}
            
            session = self.active_sessions[session_id]
            
            sync_result = {
                "session_id": session_id,
                "sync_id": f"sync-{int(datetime.utcnow().timestamp())}",
                "sync_time": datetime.utcnow().isoformat(),
                "platforms_synced": [],
                "participants_synced": [],
                "sync_operations": [],
                "overall_success": True
            }
            
            # Synchronize with MCP-Nexus
            mcp_sync = self._sync_with_mcp_nexus(session)
            sync_result["sync_operations"].append(mcp_sync)
            if mcp_sync["success"]:
                sync_result["platforms_synced"].append("mcp_nexus")
            else:
                sync_result["overall_success"] = False
            
            # Synchronize with rtpi-pen
            rtpi_sync = self._sync_with_rtpi_pen(session)
            sync_result["sync_operations"].append(rtpi_sync)
            if rtpi_sync["success"]:
                sync_result["platforms_synced"].append("rtpi_pen")
            else:
                sync_result["overall_success"] = False
            
            # Synchronize with attack-node
            attack_sync = self._sync_with_attack_node(session)
            sync_result["sync_operations"].append(attack_sync)
            if attack_sync["success"]:
                sync_result["platforms_synced"].append("attack_node")
            else:
                sync_result["overall_success"] = False
            
            # Notify participants of synchronization
            for participant in session.participants:
                sync_result["participants_synced"].append(participant.value)
                session.add_message(
                    AgentRole.NEXUS_KAMUY,
                    f"Session data synchronized across platforms",
                    "sync_notification"
                )
            
            return {
                "success": sync_result["overall_success"],
                "sync_result": sync_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to synchronize session data: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def track_collaboration_metrics(self, session_id: str = Field(..., description="Session ID to track")) -> Dict[str, Any]:
        """
        Track collaboration effectiveness and engagement metrics.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Collaboration metrics and analytics
        """
        try:
            if session_id not in self.active_sessions:
                return {"success": False, "error": f"Session {session_id} not found"}
            
            session = self.active_sessions[session_id]
            
            metrics = {
                "session_id": session_id,
                "metrics_id": f"metrics-{int(datetime.utcnow().timestamp())}",
                "analysis_time": datetime.utcnow().isoformat(),
                "session_duration": self._calculate_session_duration(session),
                "communication_metrics": {},
                "engagement_metrics": {},
                "productivity_metrics": {},
                "collaboration_effectiveness": 0.0
            }
            
            # Communication metrics
            metrics["communication_metrics"] = {
                "total_messages": len(session.communication_log),
                "messages_by_agent": self._analyze_messages_by_agent(session),
                "message_types": self._analyze_message_types(session),
                "average_response_time": self._calculate_average_response_time(session),
                "communication_frequency": self._calculate_communication_frequency(session)
            }
            
            # Engagement metrics
            metrics["engagement_metrics"] = {
                "active_participants": len([p for p in session.participants if self._is_agent_active(session, p)]),
                "participation_balance": self._calculate_participation_balance(session),
                "knowledge_sharing_rate": self._calculate_knowledge_sharing_rate(session_id),
                "context_update_frequency": len(session.shared_context)
            }
            
            # Productivity metrics
            metrics["productivity_metrics"] = {
                "objectives_progress": self._assess_objectives_progress(session),
                "decisions_made": self._count_decisions_made(session),
                "action_items_created": self._count_action_items(session),
                "blocking_issues_resolved": self._count_resolved_issues(session)
            }
            
            # Calculate overall collaboration effectiveness
            metrics["collaboration_effectiveness"] = self._calculate_collaboration_effectiveness(metrics)
            
            return {
                "success": True,
                "collaboration_metrics": metrics
            }
            
        except Exception as e:
            self.logger.error(f"Failed to track collaboration metrics: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def end_collaboration_session(self, session_id: str = Field(..., description="Session ID to end"),
                                session_summary: Dict[str, Any] = Field(..., description="Session summary and outcomes")) -> Dict[str, Any]:
        """
        End a collaboration session and generate final report.
        
        Args:
            session_id: Session identifier
            session_summary: Summary of session outcomes
            
        Returns:
            Session ending results
        """
        try:
            if session_id not in self.active_sessions:
                return {"success": False, "error": f"Session {session_id} not found"}
            
            session = self.active_sessions[session_id]
            
            # Generate final session report
            final_report = {
                "session_id": session_id,
                "session_name": session.session_name,
                "ended_at": datetime.utcnow().isoformat(),
                "duration": self._calculate_session_duration(session),
                "participants": [p.value for p in session.participants],
                "objective": session.objective,
                "outcomes": session_summary.get("outcomes", []),
                "achievements": session_summary.get("achievements", []),
                "challenges": session_summary.get("challenges", []),
                "lessons_learned": session_summary.get("lessons_learned", []),
                "follow_up_actions": session_summary.get("follow_up_actions", []),
                "knowledge_artifacts": list(self.shared_knowledge_base.get(session_id, {}).keys()),
                "communication_summary": {
                    "total_messages": len(session.communication_log),
                    "key_decisions": session_summary.get("key_decisions", []),
                    "unresolved_issues": session_summary.get("unresolved_issues", [])
                }
            }
            
            # End the session
            session.end_session("system")
            
            # Archive session data
            self._archive_session_data(session_id, final_report)
            
            # Clean up communication channels
            self._cleanup_communication_channels(session_id)
            
            # Move session to history
            self.collaboration_history.append(final_report)
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            self.logger.info(f"Collaboration session ended: {session_id}")
            
            return {
                "success": True,
                "final_report": final_report,
                "session_archived": True,
                "knowledge_artifacts_preserved": len(final_report["knowledge_artifacts"])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to end collaboration session: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _initialize_collaboration_system(self):
        """Initialize the collaboration system infrastructure."""
        # Default coordination rules
        self.default_coordination_rules = {
            "communication_protocol": "async_with_sync_checkpoints",
            "decision_making": "consensus_based",
            "conflict_resolution": "escalate_to_coordinator",
            "knowledge_sharing": "open_within_session",
            "context_sync_frequency": "real_time"
        }
        
        # Communication channel templates
        self.channel_templates = {
            "general": {"type": "broadcast", "persistence": "session"},
            "direct": {"type": "peer_to_peer", "persistence": "temporary"},
            "knowledge": {"type": "shared_repository", "persistence": "permanent"},
            "alerts": {"type": "priority_broadcast", "persistence": "session"}
        }
    
    def _get_default_coordination_rules(self, session_type: str) -> Dict[str, Any]:
        """Get default coordination rules based on session type."""
        rules = self.default_coordination_rules.copy()
        
        if session_type == "investigation":
            rules.update({
                "evidence_sharing": "immediate",
                "finding_validation": "peer_review",
                "timeline_coordination": "strict"
            })
        elif session_type == "assessment":
            rules.update({
                "result_aggregation": "automated",
                "quality_assurance": "cross_validation",
                "reporting_coordination": "lead_agent"
            })
        elif session_type == "development":
            rules.update({
                "code_review": "mandatory",
                "integration_testing": "continuous",
                "deployment_approval": "unanimous"
            })
        
        return rules
    
    def _get_communication_preferences(self, participants: List[AgentRole]) -> Dict[str, Any]:
        """Get communication preferences for session participants."""
        preferences = {
            "default_channels": ["general", "knowledge"],
            "notification_settings": {
                "real_time": True,
                "email_digest": False,
                "priority_alerts": True
            },
            "message_formatting": "structured",
            "attachment_support": True
        }
        
        # Customize based on participant types
        if AgentRole.BURPSUITE_OPERATOR in participants:
            preferences["default_channels"].append("scan_results")
        
        if AgentRole.DAEDELU5 in participants:
            preferences["default_channels"].append("compliance_updates")
        
        return preferences
    
    def _setup_communication_channels(self, session_id: str, participants: List[AgentRole]):
        """Setup communication channels for session participants."""
        channels = {}
        
        for channel_name, template in self.channel_templates.items():
            channels[channel_name] = {
                "channel_id": f"{session_id}-{channel_name}",
                "participants": [p.value for p in participants],
                "created_at": datetime.utcnow().isoformat(),
                **template
            }
        
        self.communication_channels[session_id] = channels
    
    def _initialize_shared_knowledge_space(self, session_id: str):
        """Initialize shared knowledge space for session."""
        self.shared_knowledge_base[session_id] = {
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "knowledge_count": 0,
                "categories": [],
                "access_control": "session_participants"
            }
        }
    
    def _calculate_relevance_score(self, knowledge_item: Dict[str, Any], 
                                 session: CollaborationSession) -> float:
        """Calculate relevance score for knowledge item."""
        base_score = 50.0
        
        # Check relevance to session objective
        objective_keywords = session.objective.lower().split()
        content = str(knowledge_item.get("content", "")).lower()
        title = knowledge_item.get("title", "").lower()
        
        keyword_matches = sum(1 for keyword in objective_keywords if keyword in content or keyword in title)
        relevance_bonus = min(30.0, keyword_matches * 10)
        
        # Knowledge type relevance
        knowledge_type = knowledge_item.get("type", "general")
        type_bonuses = {
            "vulnerability": 20.0,
            "exploit": 25.0,
            "configuration": 15.0,
            "compliance": 15.0,
            "tool_output": 10.0
        }
        type_bonus = type_bonuses.get(knowledge_type, 0.0)
        
        final_score = min(100.0, base_score + relevance_bonus + type_bonus)
        return round(final_score, 2)
    
    def _distribute_knowledge_to_agents(self, session: CollaborationSession, 
                                      knowledge: Dict[str, Any], sharing_agent: AgentRole) -> Dict[str, Any]:
        """Distribute knowledge to relevant agents."""
        distribution = {
            "distributed_to": [],
            "distribution_method": "push",
            "relevance_filtering": True
        }
        
        for participant in session.participants:
            if participant != sharing_agent:
                # Check if knowledge is relevant to this agent
                relevance = self._assess_knowledge_relevance_for_agent(knowledge, participant)
                
                if relevance["relevant"]:
                    distribution["distributed_to"].append({
                        "agent": participant.value,
                        "relevance_score": relevance["score"],
                        "delivery_method": "context_update"
                    })
        
        return distribution
    
    def _assess_knowledge_relevance_for_agent(self, knowledge: Dict[str, Any], 
                                            agent: AgentRole) -> Dict[str, Any]:
        """Assess if knowledge is relevant for a specific agent."""
        # Agent-specific relevance rules
        relevance_rules = {
            AgentRole.RT_DEV: ["configuration", "deployment", "infrastructure"],
            AgentRole.BUG_HUNTER: ["vulnerability", "exploit", "security_finding"],
            AgentRole.BURPSUITE_OPERATOR: ["web_vulnerability", "scan_result", "api_security"],
            AgentRole.DAEDELU5: ["compliance", "policy", "infrastructure", "hardening"],
            AgentRole.NEXUS_KAMUY: ["workflow", "coordination", "summary", "metrics"]
        }
        
        knowledge_type = knowledge.get("knowledge_type", "general")
        knowledge_tags = knowledge.get("tags", [])
        
        agent_interests = relevance_rules.get(agent, [])
        
        # Check direct type match
        type_relevant = knowledge_type in agent_interests
        
        # Check tag matches
        tag_matches = sum(1 for tag in knowledge_tags if any(interest in tag for interest in agent_interests))
        
        # Calculate relevance score
        relevance_score = 0.0
        if type_relevant:
            relevance_score += 50.0
        
        relevance_score += min(30.0, tag_matches * 10)
        
        return {
            "relevant": relevance_score > 30.0,
            "score": relevance_score,
            "reasons": {
                "type_match": type_relevant,
                "tag_matches": tag_matches,
                "agent_interests": agent_interests
            }
        }
    
    def _validate_context_update(self, key: str, value: Any, session: CollaborationSession) -> Dict[str, Any]:
        """Validate context update before applying."""
        validation = {
            "valid": True,
            "key": key,
            "warnings": [],
            "error": None
        }
        
        # Check key format
        if not key or not isinstance(key, str):
            validation["valid"] = False
            validation["error"] = "Invalid context key format"
            return validation
        
        # Check for reserved keys
        reserved_keys = ["session_id", "participants", "created_at"]
        if key in reserved_keys:
            validation["valid"] = False
            validation["error"] = f"Key '{key}' is reserved and cannot be updated"
            return validation
        
        # Check value size (prevent excessive memory usage)
        try:
            value_size = len(json.dumps(value, default=str))
            if value_size > 1048576:  # 1MB limit
                validation["valid"] = False
                validation["error"] = "Context value exceeds size limit (1MB)"
                return validation
        except Exception:
            validation["warnings"].append("Could not calculate value size")
        
        return validation
    
    def _synchronize_context_across_platforms(self, session_id: str, context_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronize context updates across platforms."""
        sync_operations = []
        
        # Sync with MCP-Nexus
        try:
            mcp_result = self.mcp_client.update_session_context(session_id, context_updates)
            sync_operations.append({
                "platform": "mcp_nexus",
                "success": True,
                "updates_synced": len(context_updates)
            })
        except Exception as e:
            sync_operations.append({
                "platform": "mcp_nexus",
                "success": False,
                "error": str(e)
            })
        
        return {
            "sync_operations": sync_operations,
            "overall_success": all(op["success"] for op in sync_operations)
        }
    
    def _deliver_message_to_agent(self, session_id: str, sender: AgentRole, 
                                recipient: AgentRole, message: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver message to specific agent."""
        # Simulate message delivery
        return {
            "delivered": True,
            "delivery_time": datetime.utcnow().isoformat(),
            "recipient": recipient.value,
            "delivery_method": "direct_api",
            "acknowledgment_received": True
        }
    
    def _update_communication_statistics(self, session_id: str, communication_result: Dict[str, Any]):
        """Update communication statistics for session."""
        # In a real implementation, this would update various metrics
        pass
    
    def _sync_with_mcp_nexus(self, session: CollaborationSession) -> Dict[str, Any]:
        """Synchronize session with MCP-Nexus platform."""
        try:
            # Simulate sync operation
            return {
                "platform": "mcp_nexus",
                "success": True,
                "sync_time": datetime.utcnow().isoformat(),
                "data_synced": ["shared_context", "communication_log"]
            }
        except Exception as e:
            return {"platform": "mcp_nexus", "success": False, "error": str(e)}
    
    def _sync_with_rtpi_pen(self, session: CollaborationSession) -> Dict[str, Any]:
        """Synchronize session with rtpi-pen platform."""
        try:
            # Simulate sync operation
            return {
                "platform": "rtpi_pen",
                "success": True,
                "sync_time": datetime.utcnow().isoformat(),
                "data_synced": ["session_state", "healing_rules"]
            }
        except Exception as e:
            return {"platform": "rtpi_pen", "success": False, "error": str(e)}
    
    def _sync_with_attack_node(self, session: CollaborationSession) -> Dict[str, Any]:
        """Synchronize session with attack-node platform."""
        try:
            # Simulate sync operation
            return {
                "platform": "attack_node",
                "success": True,
                "sync_time": datetime.utcnow().isoformat(),
                "data_synced": ["scan_results", "exploit_data"]
            }
        except Exception as e:
            return {"platform": "attack_node", "success": False, "error": str(e)}
    
    def _calculate_session_duration(self, session: CollaborationSession) -> Dict[str, Any]:
        """Calculate session duration metrics."""
        if session.end_time:
            duration = session.end_time - session.start_time
        else:
            duration = datetime.utcnow() - session.start_time
        
        return {
            "total_minutes": duration.total_seconds() / 60,
            "total_hours": duration.total_seconds() / 3600,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None
        }
    
    def _analyze_messages_by_agent(self, session: CollaborationSession) -> Dict[str, int]:
        """Analyze message count by agent."""
        message_counts = {}
        
        for message in session.communication_log:
            sender = message.get("sender", "unknown")
            message_counts[sender] = message_counts.get(sender, 0) + 1
        
        return message_counts
    
    def _analyze_message_types(self, session: CollaborationSession) -> Dict[str, int]:
        """Analyze distribution of message types."""
        type_counts = {}
        
        for message in session.communication_log:
            msg_type = message.get("type", "general")
            type_counts[msg_type] = type_counts.get(msg_type, 0) + 1
        
        return type_counts
    
    def _calculate_average_response_time(self, session: CollaborationSession) -> float:
        """Calculate average response time between messages."""
        if len(session.communication_log) < 2:
            return 0.0
        
        response_times = []
        for i in range(1, len(session.communication_log)):
            current_time = datetime.fromisoformat(session.communication_log[i]["timestamp"])
            previous_time = datetime.fromisoformat(session.communication_log[i-1]["timestamp"])
            
            response_time = (current_time - previous_time).total_seconds() / 60  # minutes
            response_times.append(response_time)
        
        return sum(response_times) / len(response_times) if response_times else 0.0
    
    def _calculate_communication_frequency(self, session: CollaborationSession) -> float:
        """Calculate communication frequency (messages per hour)."""
        duration = self._calculate_session_duration(session)
        hours = duration["total_hours"]
        
        if hours > 0:
            return len(session.communication_log) / hours
        return 0.0
    
    def _is_agent_active(self, session: CollaborationSession, agent: AgentRole) -> bool:
        """Check if agent is actively participating."""
        # Check if agent has sent messages in last hour
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        for message in session.communication_log:
            if (message.get("sender") == agent.value and 
                datetime.fromisoformat(message["timestamp"]) > cutoff_time):
                return True
        
        return False
    
    def _calculate_participation_balance(self, session: CollaborationSession) -> float:
        """Calculate how balanced participation is across agents."""
        message_counts = self._analyze_messages_by_agent(session)
        
        if not message_counts:
            return 0.0
        
        # Calculate standard deviation of message counts
        values = list(message_counts.values())
        mean_count = sum(values) / len(values)
        variance = sum((x - mean_count) ** 2 for x in values) / len(values)
        
        # Convert to balance score (0-100, where 100 is perfectly balanced)
        balance_score = max(0, 100 - (variance ** 0.5))
        return round(balance_score, 2)
    
    def _calculate_knowledge_sharing_rate(self, session_id: str) -> float:
        """Calculate rate of knowledge sharing in session."""
        knowledge_base = self.shared_knowledge_base.get(session_id, {})
        knowledge_items = [k for k in knowledge_base.keys() if k != "metadata"]
        
        # Calculate knowledge items per hour
        if session_id in self.active_sessions:
            duration = self._calculate_session_duration(self.active_sessions[session_id])
            hours = duration["total_hours"]
            
            if hours > 0:
                return len(knowledge_items) / hours
        
        return 0.0
    
    def _assess_objectives_progress(self, session: CollaborationSession) -> Dict[str, Any]:
        """Assess progress toward session objectives."""
        # Simplified objective progress assessment
        return {
            "completion_percentage": 75.0,  # Simulated
            "milestones_reached": 3,
            "remaining_objectives": 1,
            "progress_trend": "positive"
        }
    
    def _count_decisions_made(self, session: CollaborationSession) -> int:
        """Count decisions made during collaboration."""
        decision_keywords = ["decided", "agreed", "resolved", "chosen"]
        decision_count = 0
        
        for message in session.communication_log:
            content = message.get("message", "").lower()
            if any(keyword in content for keyword in decision_keywords):
                decision_count += 1
        
        return decision_count
    
    def _count_action_items(self, session: CollaborationSession) -> int:
        """Count action items created during collaboration."""
        action_keywords = ["action item", "todo", "follow up", "next step"]
        action_count = 0
        
        for message in session.communication_log:
            content = message.get("message", "").lower()
            if any(keyword in content for keyword in action_keywords):
                action_count += 1
        
        return action_count
    
    def _count_resolved_issues(self, session: CollaborationSession) -> int:
        """Count blocking issues resolved during collaboration."""
        resolution_keywords = ["resolved", "fixed", "solved", "unblocked"]
        resolution_count = 0
        
        for message in session.communication_log:
            content = message.get("message", "").lower()
            if any(keyword in content for keyword in resolution_keywords):
                resolution_count += 1
        
        return resolution_count
    
    def _calculate_collaboration_effectiveness(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall collaboration effectiveness score."""
        # Weight different factors
        communication_score = min(100, metrics["communication_metrics"]["total_messages"] * 2)
        engagement_score = metrics["engagement_metrics"]["participation_balance"]
        productivity_score = min(100, (
            metrics["productivity_metrics"]["decisions_made"] * 10 +
            metrics["productivity_metrics"]["action_items_created"] * 5
        ))
        
        # Weighted average
        effectiveness = (communication_score * 0.3 + engagement_score * 0.4 + productivity_score * 0.3)
        return round(effectiveness, 2)
    
    def _archive_session_data(self, session_id: str, final_report: Dict[str, Any]):
        """Archive session data for future reference."""
        # In a real implementation, this would save to persistent storage
        archive_entry = {
            "session_id": session_id,
            "archived_at": datetime.utcnow().isoformat(),
            "final_report": final_report,
            "knowledge_items": self.shared_knowledge_base.get(session_id, {}),
            "communication_channels": self.communication_channels.get(session_id, {})
        }
        
        # Add to collaboration history
        self.collaboration_history.append(archive_entry)
    
    def _cleanup_communication_channels(self, session_id: str):
        """Clean up communication channels for ended session."""
        if session_id in self.communication_channels:
            del self.communication_channels[session_id]
        
        # Clean up knowledge base (optionally preserve for archival)
        if session_id in self.shared_knowledge_base:
            # Move to archive instead of deleting
            archive_key = f"archived_{session_id}"
            # In real implementation, move to persistent archive storage

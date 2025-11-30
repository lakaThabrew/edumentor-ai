"""
Session Manager - Manages conversation sessions and state
Implements ADK InMemorySessionService concept
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict


class SessionManager:
    """
    Session management for maintaining conversation state.
    Implements in-memory session service pattern from ADK.
    """
    
    def __init__(self):
        """Initialize session manager"""
        # Store active sessions: session_id -> session_data
        self.sessions: Dict[str, Dict] = {}
        
        # Map student_id to current session_id
        self.student_sessions: Dict[str, str] = {}
        
        # Session history for analytics
        self.session_history: Dict[str, List[Dict]] = defaultdict(list)
    
    def create_session(self, student_id: str) -> str:
        """
        Create new session for student
        
        Args:
            student_id: Student identifier
            
        Returns:
            session_id: Unique session identifier
        """
        session_id = str(uuid.uuid4())
        
        session_data = {
            "session_id": session_id,
            "student_id": student_id,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "messages": [],
            "state": {},
            "context": {}
        }
        
        self.sessions[session_id] = session_data
        self.student_sessions[student_id] = session_id
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve session data
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if not found
        """
        return self.sessions.get(session_id)
    
    def get_current_session(self, student_id: str) -> Optional[str]:
        """
        Get current active session for student
        
        Args:
            student_id: Student identifier
            
        Returns:
            session_id or None
        """
        return self.student_sessions.get(student_id)
    
    def update_session(
        self,
        session_id: str,
        user_message: str,
        agent_response: str
    ) -> bool:
        """
        Update session with new interaction
        
        Args:
            session_id: Session identifier
            user_message: User's message
            agent_response: Agent's response
            
        Returns:
            True if successful
        """
        session = self.sessions.get(session_id)
        
        if not session:
            return False
        
        # Add message pair
        message_pair = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "agent": agent_response
        }
        
        session["messages"].append(message_pair)
        session["last_activity"] = datetime.now().isoformat()
        
        # Limit message history to prevent memory overflow
        if len(session["messages"]) > 50:
            session["messages"] = session["messages"][-50:]
        
        return True
    
    def set_session_state(
        self,
        session_id: str,
        key: str,
        value: any
    ) -> bool:
        """
        Set state variable for session
        
        Args:
            session_id: Session identifier
            key: State key
            value: State value
            
        Returns:
            True if successful
        """
        session = self.sessions.get(session_id)
        
        if not session:
            return False
        
        session["state"][key] = value
        return True
    
    def get_session_state(
        self,
        session_id: str,
        key: str,
        default: any = None
    ) -> any:
        """
        Get state variable from session
        
        Args:
            session_id: Session identifier
            key: State key
            default: Default value if not found
            
        Returns:
            State value or default
        """
        session = self.sessions.get(session_id)
        
        if not session:
            return default
        
        return session["state"].get(key, default)
    
    def get_conversation_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent conversation history from session
        
        Args:
            session_id: Session identifier
            limit: Maximum messages to return
            
        Returns:
            List of message pairs
        """
        session = self.sessions.get(session_id)
        
        if not session:
            return []
        
        return session["messages"][-limit:]
    
    def end_session(self, session_id: str) -> bool:
        """
        End session and move to history
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful
        """
        session = self.sessions.get(session_id)
        
        if not session:
            return False
        
        # Add to history
        student_id = session["student_id"]
        session["ended_at"] = datetime.now().isoformat()
        self.session_history[student_id].append(session)
        
        # Remove from active sessions
        del self.sessions[session_id]
        
        # Clear student's current session
        if self.student_sessions.get(student_id) == session_id:
            del self.student_sessions[student_id]
        
        return True
    
    def get_session_stats(self, session_id: str) -> Dict:
        """
        Get statistics for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session statistics
        """
        session = self.sessions.get(session_id)
        
        if not session:
            return {}
        
        # Calculate duration
        created = datetime.fromisoformat(session["created_at"])
        last_activity = datetime.fromisoformat(session["last_activity"])
        duration = (last_activity - created).total_seconds()
        
        return {
            "session_id": session_id,
            "student_id": session["student_id"],
            "message_count": len(session["messages"]),
            "duration_seconds": duration,
            "created_at": session["created_at"],
            "last_activity": session["last_activity"]
        }
    
    def get_student_session_history(
        self,
        student_id: str
    ) -> List[Dict]:
        """
        Get all past sessions for a student
        
        Args:
            student_id: Student identifier
            
        Returns:
            List of past sessions
        """
        return self.session_history.get(student_id, [])
    
    def cleanup_inactive_sessions(self, max_age_hours: int = 24):
        """
        Clean up sessions inactive for more than max_age_hours
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
        """
        current_time = datetime.now()
        inactive_sessions = []
        
        for session_id, session in self.sessions.items():
            last_activity = datetime.fromisoformat(session["last_activity"])
            age_hours = (current_time - last_activity).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                inactive_sessions.append(session_id)
        
        # End inactive sessions
        for session_id in inactive_sessions:
            self.end_session(session_id)
        
        return len(inactive_sessions)
    
    def get_context_for_llm(self, session_id: str, max_messages: int = 5) -> str:
        """
        Format recent conversation for LLM context
        
        Args:
            session_id: Session identifier
            max_messages: Maximum recent messages to include
            
        Returns:
            Formatted conversation context
        """
        history = self.get_conversation_history(session_id, max_messages)
        
        if not history:
            return "No prior conversation in this session."
        
        formatted = []
        for msg in history:
            formatted.append(f"Student: {msg['user']}")
            formatted.append(f"EduMentor: {msg['agent'][:200]}...")  # Truncate long responses
        
        return "\n".join(formatted)
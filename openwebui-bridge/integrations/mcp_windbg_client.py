"""
MCP WinDBG Client Integration

Wrapper client for integrating with mcp-windbg server for Windows crash dump analysis
and remote debugging capabilities within the RT-Dev agent toolkit.
"""

import asyncio
import subprocess
import logging
import os
import tempfile
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("MCPWinDBGClient")

class MCPWinDBGClient:
    """
    Client wrapper for mcp-windbg integration
    Provides Windows crash dump analysis and remote debugging capabilities
    """
    
    def __init__(self, cdb_path: Optional[str] = None, symbols_path: Optional[str] = None, timeout: int = 30):
        """
        Initialize the MCP WinDBG client
        
        Args:
            cdb_path: Path to cdb.exe (optional, will auto-detect)
            symbols_path: Symbol server path (optional)
            timeout: Command timeout in seconds
        """
        self.cdb_path = cdb_path or self._find_cdb_executable()
        self.symbols_path = symbols_path or "SRV*C:\\Symbols*https://msdl.microsoft.com/download/symbols"
        self.timeout = timeout
        self.active_sessions = {}
        self.session_counter = 0
        
        logger.info(f"Initialized MCP WinDBG Client with CDB: {self.cdb_path}")
    
    def _find_cdb_executable(self) -> Optional[str]:
        """Auto-detect CDB executable location"""
        possible_paths = [
            r"C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\cdb.exe",
            r"C:\Program Files\Windows Kits\10\Debuggers\x64\cdb.exe",
            r"C:\Program Files (x86)\Windows Kits\8.1\Debuggers\x64\cdb.exe",
            r"C:\Program Files\Windows Kits\8.1\Debuggers\x64\cdb.exe",
        ]
        
        # Check in PATH first
        try:
            result = subprocess.run(["where", "cdb.exe"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except Exception:
            pass
        
        # Check known installation paths
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        logger.warning("CDB executable not found in standard locations")
        return None
    
    async def open_crash_dump(self, dump_path: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Open and analyze a Windows crash dump file
        
        Args:
            dump_path: Path to the crash dump file
            session_id: Optional session identifier
            
        Returns:
            Dictionary with session info and initial analysis
        """
        if not self.cdb_path:
            return {
                "success": False,
                "error": "CDB executable not found. Please install Windows Debugging Tools."
            }
        
        if not os.path.exists(dump_path):
            return {
                "success": False,
                "error": f"Dump file not found: {dump_path}"
            }
        
        try:
            session_id = session_id or f"dump_session_{self.session_counter}"
            self.session_counter += 1
            
            # Build CDB command
            cmd = [
                self.cdb_path,
                "-z", dump_path,  # Open dump file
                "-c", "!analyze -v; k; q"  # Run initial analysis and quit
            ]
            
            # Set symbol path environment
            env = os.environ.copy()
            if self.symbols_path:
                env["_NT_SYMBOL_PATH"] = self.symbols_path
            
            # Execute CDB
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await asyncio.wait_for(
                result.communicate(), timeout=self.timeout
            )
            
            # Parse output
            output = stdout.decode('utf-8', errors='ignore') if stdout else ""
            error_output = stderr.decode('utf-8', errors='ignore') if stderr else ""
            
            # Store session info
            session_info = {
                "session_id": session_id,
                "type": "crash_dump",
                "dump_path": dump_path,
                "opened_at": datetime.utcnow(),
                "initial_output": output,
                "errors": error_output if error_output else None
            }
            
            self.active_sessions[session_id] = session_info
            
            return {
                "success": True,
                "session_id": session_id,
                "dump_path": dump_path,
                "initial_analysis": self._parse_crash_analysis(output),
                "raw_output": output
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Analysis timed out after {self.timeout} seconds"
            }
        except Exception as e:
            logger.error(f"Failed to open crash dump: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to open crash dump: {str(e)}"
            }
    
    async def open_remote_session(self, connection_string: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Connect to a remote debugging session
        
        Args:
            connection_string: Remote connection string (e.g., "tcp:Port=5005,Server=192.168.1.100")
            session_id: Optional session identifier
            
        Returns:
            Dictionary with session info and connection status
        """
        if not self.cdb_path:
            return {
                "success": False,
                "error": "CDB executable not found. Please install Windows Debugging Tools."
            }
        
        try:
            session_id = session_id or f"remote_session_{self.session_counter}"
            self.session_counter += 1
            
            # Build CDB command for remote debugging
            cmd = [
                self.cdb_path,
                "-remote", connection_string,
                "-c", "k; ~*k; q"  # Show call stacks and quit for initial test
            ]
            
            # Set symbol path environment
            env = os.environ.copy()
            if self.symbols_path:
                env["_NT_SYMBOL_PATH"] = self.symbols_path
            
            # Execute CDB
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await asyncio.wait_for(
                result.communicate(), timeout=self.timeout
            )
            
            # Parse output
            output = stdout.decode('utf-8', errors='ignore') if stdout else ""
            error_output = stderr.decode('utf-8', errors='ignore') if stderr else ""
            
            # Store session info
            session_info = {
                "session_id": session_id,
                "type": "remote_debug",
                "connection_string": connection_string,
                "opened_at": datetime.utcnow(),
                "initial_output": output,
                "errors": error_output if error_output else None
            }
            
            self.active_sessions[session_id] = session_info
            
            return {
                "success": True,
                "session_id": session_id,
                "connection_string": connection_string,
                "initial_status": self._parse_remote_status(output),
                "raw_output": output
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Connection timed out after {self.timeout} seconds"
            }
        except Exception as e:
            logger.error(f"Failed to connect to remote session: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to connect to remote session: {str(e)}"
            }
    
    async def execute_command(self, session_id: str, command: str) -> Dict[str, Any]:
        """
        Execute a WinDBG command in an active session
        
        Args:
            session_id: Session identifier
            command: WinDBG command to execute
            
        Returns:
            Dictionary with command output and execution info
        """
        if session_id not in self.active_sessions:
            return {
                "success": False,
                "error": f"Session {session_id} not found or not active"
            }
        
        session = self.active_sessions[session_id]
        
        try:
            # Build command based on session type
            if session["type"] == "crash_dump":
                cmd = [
                    self.cdb_path,
                    "-z", session["dump_path"],
                    "-c", f"{command}; q"
                ]
            elif session["type"] == "remote_debug":
                cmd = [
                    self.cdb_path,
                    "-remote", session["connection_string"],
                    "-c", f"{command}; q"
                ]
            else:
                return {
                    "success": False,
                    "error": f"Unknown session type: {session['type']}"
                }
            
            # Set symbol path environment
            env = os.environ.copy()
            if self.symbols_path:
                env["_NT_SYMBOL_PATH"] = self.symbols_path
            
            # Execute command
            start_time = datetime.utcnow()
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await asyncio.wait_for(
                result.communicate(), timeout=self.timeout
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Parse output
            output = stdout.decode('utf-8', errors='ignore') if stdout else ""
            error_output = stderr.decode('utf-8', errors='ignore') if stderr else ""
            
            return {
                "success": True,
                "session_id": session_id,
                "command": command,
                "output": output,
                "errors": error_output if error_output else None,
                "execution_time_seconds": execution_time,
                "timestamp": datetime.utcnow()
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Command timed out after {self.timeout} seconds"
            }
        except Exception as e:
            logger.error(f"Failed to execute command: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to execute command: {str(e)}"
            }
    
    def close_session(self, session_id: str) -> Dict[str, Any]:
        """
        Close an active debugging session
        
        Args:
            session_id: Session identifier to close
            
        Returns:
            Dictionary with closure status
        """
        if session_id not in self.active_sessions:
            return {
                "success": False,
                "error": f"Session {session_id} not found"
            }
        
        session = self.active_sessions.pop(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "session_type": session["type"],
            "closed_at": datetime.utcnow(),
            "duration_seconds": (datetime.utcnow() - session["opened_at"]).total_seconds()
        }
    
    def list_crash_dumps(self, directory: str) -> Dict[str, Any]:
        """
        List Windows crash dump files in a directory
        
        Args:
            directory: Directory to search for dump files
            
        Returns:
            Dictionary with list of found dump files
        """
        try:
            if not os.path.exists(directory):
                return {
                    "success": False,
                    "error": f"Directory not found: {directory}"
                }
            
            dump_files = []
            dump_extensions = ['.dmp', '.mdmp', '.hdmp']
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in dump_extensions):
                        file_path = os.path.join(root, file)
                        file_stat = os.stat(file_path)
                        
                        dump_files.append({
                            "filename": file,
                            "path": file_path,
                            "size_bytes": file_stat.st_size,
                            "modified_time": datetime.fromtimestamp(file_stat.st_mtime),
                            "created_time": datetime.fromtimestamp(file_stat.st_ctime)
                        })
            
            # Sort by modification time (newest first)
            dump_files.sort(key=lambda x: x["modified_time"], reverse=True)
            
            return {
                "success": True,
                "directory": directory,
                "dump_files": dump_files,
                "count": len(dump_files)
            }
            
        except Exception as e:
            logger.error(f"Failed to list crash dumps: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to list crash dumps: {str(e)}"
            }
    
    def get_active_sessions(self) -> Dict[str, Any]:
        """
        Get information about active debugging sessions
        
        Returns:
            Dictionary with active session information
        """
        sessions_info = {}
        
        for session_id, session in self.active_sessions.items():
            sessions_info[session_id] = {
                "session_id": session_id,
                "type": session["type"],
                "opened_at": session["opened_at"],
                "duration_seconds": (datetime.utcnow() - session["opened_at"]).total_seconds(),
                "target": session.get("dump_path") or session.get("connection_string")
            }
        
        return {
            "active_sessions": sessions_info,
            "session_count": len(sessions_info),
            "cdb_available": self.cdb_path is not None,
            "symbols_path": self.symbols_path
        }
    
    def _parse_crash_analysis(self, output: str) -> Dict[str, Any]:
        """Parse crash dump analysis output"""
        analysis = {
            "exception_type": None,
            "exception_code": None,
            "faulting_module": None,
            "call_stack_depth": 0,
            "probable_cause": None
        }
        
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Look for exception information
            if "EXCEPTION_RECORD" in line or "ExceptionCode" in line:
                if ":" in line:
                    analysis["exception_code"] = line.split(':')[-1].strip()
            
            # Look for faulting module
            if "FAULTING_MODULE" in line or "IMAGE_NAME" in line:
                if ":" in line:
                    analysis["faulting_module"] = line.split(':')[-1].strip()
            
            # Look for probable cause
            if "PROBABLE_CAUSE" in line or "FAILURE_BUCKET_ID" in line:
                if ":" in line:
                    analysis["probable_cause"] = line.split(':')[-1].strip()
            
            # Count call stack frames
            if line.startswith('0') and '!' in line:
                analysis["call_stack_depth"] += 1
        
        return analysis
    
    def _parse_remote_status(self, output: str) -> Dict[str, Any]:
        """Parse remote debugging session status"""
        status = {
            "connected": False,
            "thread_count": 0,
            "current_thread": None,
            "process_name": None
        }
        
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check if connection was successful
            if "Connected to" in line or "Debuggee connected" in line:
                status["connected"] = True
            
            # Look for thread information
            if line.startswith('~') or 'Thread' in line:
                status["thread_count"] += 1
                
                if '*' in line:  # Current thread marker
                    status["current_thread"] = line
            
            # Look for process information
            if "process" in line.lower() and ".exe" in line:
                status["process_name"] = line
        
        return status

# Global instance for the bridge API
windbg_client = None

def get_windbg_client() -> MCPWinDBGClient:
    """Get or create the global WinDBG client instance"""
    global windbg_client
    if windbg_client is None:
        windbg_client = MCPWinDBGClient()
    return windbg_client

"""
Enhanced Tools Package for OpenWebUI Integration

This package provides the Tools class that integrates with OpenWebUI,
offering both original functionality and enhanced research capabilities
through the multi-agent research orchestration platform.
"""

# Import the main Tools class
try:
    from .tools import Tools
    __all__ = ['Tools']
except ImportError as e:
    print(f"Warning: Could not import Tools class: {e}")
    # Create a fallback Tools class if import fails
    class Tools:
        def __init__(self):
            self.enhanced_available = False
            print("Warning: Using fallback Tools class - enhanced features not available")
        
        def get_current_time(self):
            from datetime import datetime
            now = datetime.now()
            return f"Current Date and Time = {now.strftime('%A, %B %d, %Y')}, {now.strftime('%I:%M:%S %p')}"
        
        def calculator(self, equation: str):
            try:
                allowed_chars = set("0123456789+-*/()., ")
                if not all(c in allowed_chars for c in equation):
                    return "Invalid equation - only basic math operations allowed"
                result = eval(equation)
                return f"{equation} = {result}"
            except Exception as e:
                return f"Invalid equation: {str(e)}"
    
    __all__ = ['Tools']

# Version information
__version__ = "2.0.0"
__author__ = "attck.nexus"
__description__ = "Enhanced research tools with multi-agent orchestration"

# Also import agent modules for compatibility
try:
    from . import rt_dev
    from . import bug_hunter
    from . import burpsuite_operator
    from . import daedelu5
    from . import nexus_kamuy
    from . import shared
    
    # Add to __all__ if successfully imported
    __all__.extend([
        "rt_dev",
        "bug_hunter", 
        "burpsuite_operator",
        "daedelu5",
        "nexus_kamuy",
        "shared"
    ])
except ImportError:
    # Agent modules not available, continue with just Tools
    pass

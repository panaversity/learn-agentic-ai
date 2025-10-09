from typing import Dict, Any

# Custom theme configuration
CUSTOM_THEME: Dict[str, Any] = {
    # Color scheme
    "primary": "#007AFF",
    "secondary": "#6C757D",
    "background": "#F8F9FA",
    "accent": "#5856D6",
    
    # Typography
    "font": {
        "family": "'Inter', sans-serif",
        "size": {
            "base": "16px",
            "small": "14px",
            "large": "18px"
        }
    },
    
    # Component specific
    "message": {
        "user": {
            "background": "#E1F5FE",
            "text": "#01579B"
        },
        "assistant": {
            "background": "#F3E5F5",
            "text": "#4A148C"
        }
    },
    
    # Layout
    "spacing": {
        "small": "8px",
        "medium": "16px",
        "large": "24px"
    },
    
    # Dark mode colors
    "dark": {
        "background": "#1A1A1A",
        "text": "#FFFFFF",
        "primary": "#0A84FF",
        "secondary": "#86868B"
    }
}

# Theme application helper
def apply_theme(chainlit_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply custom theme to Chainlit configuration
    
    Args:
        chainlit_config: Base Chainlit configuration
        
    Returns:
        Dict[str, Any]: Updated configuration with custom theme
    """
    chainlit_config["theme"] = CUSTOM_THEME
    return chainlit_config 
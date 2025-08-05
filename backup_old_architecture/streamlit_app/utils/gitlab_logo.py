"""
GitLab Logo Utility
Provides the official GitLab logo as base64 encoded SVG for use throughout the application.
"""

def get_gitlab_logo_base64():
    """
    Returns the official GitLab logo as a base64 encoded SVG string.
    
    Returns:
        str: Base64 encoded GitLab logo SVG
    """
    return "PHN2ZyB3aWR0aD0iMjUwMCIgaGVpZ2h0PSIyMzA1IiB2aWV3Qm94PSIwIDAgMjU2IDIzNiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBwcmVzZXJ2ZUFzcGVjdFJhdGlvPSJ4TWluWU1pbiBtZWV0Ij48cGF0aCBkPSJNMTI4LjA3NSAyMzYuMDc1bDQ3LjEwNC0xNDQuOTdIODAuOTdsNDcuMTA0IDE0NC45N3oiIGZpbGw9IiNFMjQzMjkiLz48cGF0aCBkPSJNMTI4LjA3NSAyMzYuMDc0TDgwLjk3IDkxLjEwNEgxNC45NTZsMTEzLjExOSAxNDQuOTd6IiBmaWxsPSIjRkM2RDI2Ii8+PHBhdGggZD0iTTE0Ljk1NiA5MS4xMDRMLjY0MiAxMzUuMTZhOS43NTIgOS43NTIgMCAwIDAgMy41NDIgMTAuOTAzbDEyMy44OTEgOTAuMDEyLTExMy4xMi0xNDQuOTd6IiBmaWxsPSIjRkNBMzI2Ii8+PHBhdGggZD0iTTE0Ljk1NiA5MS4xMDVIODAuOTdMNTIuNjAxIDMuNzljLTEuNDYtNC40OTMtNy44MTYtNC40OTItOS4yNzUgMGwtMjguMzcgODcuMzE1eiIgZmlsbD0iI0UyNDMyOSIvPjxwYXRoIGQ9Ik0xMjguMDc1IDIzNi4wNzRsNDcuMTA0LTE0NC45N2g2Ni4wMTVsLTExMy4xMiAxNDQuOTd6IiBmaWxsPSIjRkM2RDI2Ci8+PHBhdGggZD0iTTI0MS4xOTQgOTEuMTA0bDE0LjMxNCA0NC4wNTZhOS43NTIgOS43NTIgMCAwIDEtMy41NDMgMTAuOTAzbC0xMjMuODkgOTAuMDEyIDExMy4xMTktMTQ0Ljk3eiIgZmlsbD0iI0ZDQTMyNiIvPjxwYXRoIGQ9Ik0yNDEuMTk0IDkxLjEwNWgtNjYuMDE1bDI4LjM3LTg3LjMxNWMxLjQ2LTQuNDkzIDcuODE2LTQuNDkyIDkuMjc1IDBsMjguMzcgODcuMzE1eiIgZmlsbD0iI0UyNDMyOSIvPjwvc3ZnPg=="

def get_gitlab_logo_html(size="32px", margin_right="12px", filter_style="brightness(0) invert(1)"):
    """
    Returns HTML img tag for the GitLab logo with customizable styling.
    
    Args:
        size (str): CSS size for width and height (default: "32px")
        margin_right (str): CSS margin-right value (default: "12px")
        filter_style (str): CSS filter for logo styling (default: "brightness(0) invert(1)" for white logo)
    
    Returns:
        str: HTML img tag with GitLab logo
    """
    logo_base64 = get_gitlab_logo_base64()
    return f'''<img src="data:image/svg+xml;base64,{logo_base64}" 
             style="width: {size}; height: {size}; margin-right: {margin_right}; filter: {filter_style};" 
             alt="GitLab Logo">'''

def get_gitlab_header_html(title="GitLab Integration", color="#FC6D26"):
    """
    Returns a complete GitLab header with logo and title.
    
    Args:
        title (str): Header title text (default: "GitLab Integration")
        color (str): Title color (default: "#FC6D26" - GitLab orange)
    
    Returns:
        str: Complete HTML header with GitLab logo and title
    """
    logo_html = get_gitlab_logo_html(size="32px", margin_right="12px", filter_style="none")
    return f'''
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        {logo_html}
        <h2 style="margin: 0; color: {color};">{title}</h2>
    </div>
    '''

# GitLab brand colors
GITLAB_ORANGE = "#FC6D26"
GITLAB_DARK_ORANGE = "#E24329"
GITLAB_LIGHT_ORANGE = "#FCA326"
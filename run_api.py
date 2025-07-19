#!/usr/bin/env python3
"""
Run the FastAPI server
"""

import uvicorn
from core.api_service import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
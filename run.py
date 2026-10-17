#!/usr/bin/env python3
"""
MudFlow OS - Application Launcher
"""
import uvicorn
import os
import sys

if __name__ == "__main__":
    print("=" * 70)
    print("  MUDFLOW OS - DRILLING MUD ENGINEERING & HYDRAULICS SUITE")
    print("=" * 70)
    print("  Version: v2.4.0-PROD")
    print("  Starting local FastAPI server...")
    print("  URL: http://127.0.0.1:9001")
    print("  API Docs: http://127.0.0.1:9001/docs")
    print("=" * 70)
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=9001, reload=True)

#!/usr/bin/env python3
"""
Another fallback entry point (some systems expect index.py)
"""
from server import start_server

if __name__ == '__main__':
    start_server()
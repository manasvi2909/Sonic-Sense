import sys
import os

# Vercel runs from the api/ directory — add the repo root so `src.*` imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# This file serves as the entry point for Vercel Serverless Functions
# It simply imports the FastAPI app from main.py

# app/memory_middleware.py - Memory usage tracking
import os
import psutil
from flask import request, g
import time

class MemoryMiddleware:
    def __init__(self, app, memory_limit_mb=400):
        self.app = app
        self.memory_limit_mb = memory_limit_mb  # Leave 100MB buffer
    
    def __call__(self, environ, start_response):
        # Check memory before request
        memory_before = self.get_memory_mb()
        
        if memory_before > self.memory_limit_mb:
            print(f"⚠️ HIGH MEMORY USAGE: {memory_before}MB (limit: {self.memory_limit_mb}MB)")
            print("🔄 Consider restarting worker...")
        
        # Process request
        return self.app(environ, start_response)
    
    def get_memory_mb(self):
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
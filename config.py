import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tt-data-management-system'
    
    # Supabase 配置
    SUPABASE_URL = os.environ.get('SUPABASE_URL') or 'https://tbxxhmtqufzzhshivija.supabase.co'
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY') or \
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRieHhobXRxdWZ6emhzaGl2aWphIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MjcxMDY1MCwiZXhwIjoyMDk4Mjg2NjUwfQ.uYnFvitNn_CrqXCvXu0xGLEF994uxMrUeINYwjPf8Eg'
    
    # 上传文件配置
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
    
    ITEMS_PER_PAGE = 50

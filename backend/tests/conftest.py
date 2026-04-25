import sys
import os

# Thêm thư mục backend vào path để nhận diện module 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
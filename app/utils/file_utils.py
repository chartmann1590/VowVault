import subprocess
import os
from flask import current_app

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in (current_app.config['ALLOWED_IMAGE_EXTENSIONS'] | current_app.config['ALLOWED_VIDEO_EXTENSIONS'])

def is_video(filename):
    """Check if file is a video"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_VIDEO_EXTENSIONS']

def is_image(filename):
    """Check if file is an image"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_IMAGE_EXTENSIONS']

def get_video_duration(filepath):
    """Get video duration using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
            filepath
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting video duration: {e}")
    return None

def create_video_thumbnail(video_path, thumbnail_path):
    """Create thumbnail from video using ffmpeg"""
    try:
        cmd = [
            'ffmpeg', '-i', video_path, '-ss', '00:00:01.000',
            '-vframes', '1', '-vf', 'scale=400:-1', thumbnail_path,
            '-y'  # Overwrite output file
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
    return False 
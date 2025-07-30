"""
Security utilities for the wedding gallery application
"""

import hashlib
import os
import re
import magic
import mimetypes
from datetime import datetime, timedelta
from flask import request, current_app
from werkzeug.utils import secure_filename
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityUtils:
    """Security utilities for file validation, rate limiting, and audit logging"""
    
    # Dangerous file extensions that should be blocked
    DANGEROUS_EXTENSIONS = {
        'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar', 'war',
        'php', 'asp', 'aspx', 'jsp', 'py', 'pl', 'sh', 'cgi', 'htaccess',
        'htpasswd', 'ini', 'log', 'tmp', 'temp', 'bak', 'backup'
    }
    
    # Suspicious file signatures (magic bytes)
    SUSPICIOUS_SIGNATURES = [
        b'MZ',  # Windows executables
        b'PK\x03\x04',  # ZIP files (could contain executables)
        b'PK\x05\x06',  # ZIP files
        b'PK\x07\x08',  # ZIP files
        b'\x7fELF',  # Linux executables
        b'\xfe\xed\xfa\xce',  # Mach-O files (macOS)
        b'\xce\xfa\xed\xfe',  # Mach-O files (macOS)
    ]
    
    @staticmethod
    def calculate_file_hash(file_path):
        """Calculate SHA-256 hash of a file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return None
    
    @staticmethod
    def validate_file_extension(filename):
        """Validate file extension against allowed and dangerous extensions"""
        if not filename or '.' not in filename:
            return False, "No file extension found"
        
        extension = filename.rsplit('.', 1)[1].lower()
        
        # Check for dangerous extensions
        if extension in SecurityUtils.DANGEROUS_EXTENSIONS:
            return False, f"Dangerous file extension: {extension}"
        
        # Check against allowed extensions
        allowed_extensions = (current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', set()) | 
                            current_app.config.get('ALLOWED_VIDEO_EXTENSIONS', set()))
        
        if extension not in allowed_extensions:
            return False, f"File extension not allowed: {extension}"
        
        return True, "Valid file extension"
    
    @staticmethod
    def validate_file_content(file_path):
        """Validate file content using magic bytes and MIME type detection"""
        try:
            # Check file size
            file_size = os.path.getsize(file_path)
            max_size = current_app.config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024)
            
            if file_size > max_size:
                return False, f"File too large: {file_size} bytes"
            
            # Read first 4KB for magic byte detection
            with open(file_path, 'rb') as f:
                header = f.read(4096)
            
            # Check for suspicious signatures
            for signature in SecurityUtils.SUSPICIOUS_SIGNATURES:
                if header.startswith(signature):
                    return False, f"Suspicious file signature detected"
            
            # Use python-magic to detect MIME type
            try:
                mime_type = magic.from_file(file_path, mime=True)
                allowed_mime_types = {
                    'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
                    'image/webp', 'video/mp4', 'video/quicktime', 'video/x-msvideo',
                    'video/webm', 'video/x-ms-wmv'
                }
                
                if mime_type not in allowed_mime_types:
                    return False, f"Unsupported MIME type: {mime_type}"
                
            except ImportError:
                # python-magic not available, fall back to extension check
                logger.warning("python-magic not available, using extension-based validation")
            
            return True, "File content validated"
            
        except Exception as e:
            logger.error(f"Error validating file content: {e}")
            return False, f"Error validating file: {str(e)}"
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename and ensure it's secure"""
        # Use werkzeug's secure_filename
        safe_filename = secure_filename(filename)
        
        # Additional sanitization
        # Remove any remaining dangerous characters
        safe_filename = re.sub(r'[^\w\-_.]', '', safe_filename)
        
        # Ensure it's not empty
        if not safe_filename:
            safe_filename = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return safe_filename
    
    @staticmethod
    def log_security_event(event_type, user_identifier=None, details=None, severity='info'):
        """Log security events to the database"""
        try:
            db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
            if not db_path:
                db_path = 'instance/wedding_photos.db'
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO security_audit_log 
                (event_type, user_identifier, ip_address, user_agent, details, severity)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                event_type,
                user_identifier,
                request.remote_addr if request else None,
                request.headers.get('User-Agent') if request else None,
                details,
                severity
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
    
    @staticmethod
    def check_rate_limit(identifier, endpoint, max_requests=10, window_minutes=1):
        """Check if request is within rate limits"""
        try:
            db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
            if not db_path:
                db_path = 'instance/wedding_photos.db'
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Clean old rate limit entries
            window_start = datetime.now() - timedelta(minutes=window_minutes)
            cursor.execute("""
                DELETE FROM rate_limit 
                WHERE window_start < ?
            """, (window_start,))
            
            # Check current rate limit
            current_window = datetime.now().replace(second=0, microsecond=0)
            cursor.execute("""
                SELECT request_count FROM rate_limit 
                WHERE identifier = ? AND endpoint = ? AND window_start = ?
            """, (identifier, endpoint, current_window))
            
            result = cursor.fetchone()
            
            if result:
                request_count = result[0]
                if request_count >= max_requests:
                    conn.close()
                    return False, f"Rate limit exceeded: {max_requests} requests per {window_minutes} minute(s)"
                
                # Update existing entry
                cursor.execute("""
                    UPDATE rate_limit 
                    SET request_count = request_count + 1 
                    WHERE identifier = ? AND endpoint = ? AND window_start = ?
                """, (identifier, endpoint, current_window))
            else:
                # Create new entry
                cursor.execute("""
                    INSERT INTO rate_limit (identifier, endpoint, request_count, window_start)
                    VALUES (?, ?, 1, ?)
                """, (identifier, endpoint, current_window))
            
            conn.commit()
            conn.close()
            
            return True, "Rate limit check passed"
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True, "Rate limit check failed, allowing request"  # Fail open for safety
    
    @staticmethod
    def get_client_identifier():
        """Get a unique identifier for the client (IP + User-Agent hash)"""
        if not request:
            return "unknown"
        
        client_info = f"{request.remote_addr}:{request.headers.get('User-Agent', '')}"
        return hashlib.md5(client_info.encode()).hexdigest()
    
    @staticmethod
    def validate_upload_request():
        """Comprehensive upload validation"""
        # Check rate limiting
        client_id = SecurityUtils.get_client_identifier()
        rate_ok, rate_msg = SecurityUtils.check_rate_limit(
            client_id, 'upload', max_requests=5, window_minutes=5
        )
        
        if not rate_ok:
            SecurityUtils.log_security_event(
                'rate_limit_exceeded', 
                client_id, 
                f"Upload rate limit exceeded: {rate_msg}",
                'warning'
            )
            return False, rate_msg
        
        # Log upload attempt
        SecurityUtils.log_security_event(
            'upload_attempt',
            client_id,
            f"Upload attempt from {request.remote_addr}",
            'info'
        )
        
        return True, "Upload validation passed"
    
    @staticmethod
    def secure_file_save(file, upload_folder, filename=None):
        """Securely save an uploaded file with validation"""
        try:
            # Validate the upload request
            valid, msg = SecurityUtils.validate_upload_request()
            if not valid:
                return False, msg
            
            # Validate file extension
            if filename is None:
                filename = file.filename
            
            ext_valid, ext_msg = SecurityUtils.validate_file_extension(filename)
            if not ext_valid:
                SecurityUtils.log_security_event(
                    'invalid_file_extension',
                    SecurityUtils.get_client_identifier(),
                    f"Invalid extension: {filename}",
                    'warning'
                )
                return False, ext_msg
            
            # Sanitize filename
            safe_filename = SecurityUtils.sanitize_filename(filename)
            
            # Ensure unique filename
            counter = 1
            base_name, ext = os.path.splitext(safe_filename)
            final_filename = safe_filename
            
            while os.path.exists(os.path.join(upload_folder, final_filename)):
                final_filename = f"{base_name}_{counter}{ext}"
                counter += 1
            
            # Save file
            file_path = os.path.join(upload_folder, final_filename)
            file.save(file_path)
            
            # Validate file content after saving
            content_valid, content_msg = SecurityUtils.validate_file_content(file_path)
            if not content_valid:
                # Remove the file if validation fails
                os.remove(file_path)
                SecurityUtils.log_security_event(
                    'invalid_file_content',
                    SecurityUtils.get_client_identifier(),
                    f"Invalid content: {final_filename} - {content_msg}",
                    'error'
                )
                return False, content_msg
            
            # Calculate file hash for integrity
            file_hash = SecurityUtils.calculate_file_hash(file_path)
            file_size = os.path.getsize(file_path)
            
            # Log successful upload
            SecurityUtils.log_security_event(
                'file_uploaded',
                SecurityUtils.get_client_identifier(),
                f"File uploaded: {final_filename} (size: {file_size}, hash: {file_hash})",
                'info'
            )
            
            return True, {
                'filename': final_filename,
                'file_path': file_path,
                'file_hash': file_hash,
                'file_size': file_size
            }
            
        except Exception as e:
            logger.error(f"Error in secure_file_save: {e}")
            SecurityUtils.log_security_event(
                'upload_error',
                SecurityUtils.get_client_identifier(),
                f"Upload error: {str(e)}",
                'error'
            )
            return False, f"Upload error: {str(e)}"
    
    @staticmethod
    def verify_file_integrity(file_path, expected_hash=None):
        """Verify file integrity using hash"""
        try:
            current_hash = SecurityUtils.calculate_file_hash(file_path)
            
            if expected_hash and current_hash != expected_hash:
                SecurityUtils.log_security_event(
                    'file_integrity_failed',
                    None,
                    f"File integrity check failed: {file_path}",
                    'error'
                )
                return False, "File integrity check failed"
            
            return True, current_hash
            
        except Exception as e:
            logger.error(f"Error verifying file integrity: {e}")
            return False, f"Error verifying file: {str(e)}"
    
    @staticmethod
    def cleanup_old_logs(days=30):
        """Clean up old security audit logs"""
        try:
            db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
            if not db_path:
                db_path = 'instance/wedding_photos.db'
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            cursor.execute("""
                DELETE FROM security_audit_log 
                WHERE created_at < ?
            """, (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_count} old security audit logs")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old logs: {e}")
            return 0 
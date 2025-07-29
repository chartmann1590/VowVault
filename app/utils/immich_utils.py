import os
import requests
from datetime import datetime
from pathlib import Path
from flask import current_app
from app import db
from app.models.photo import Photo
from app.models.guestbook import GuestbookEntry
from app.models.messages import Message
from app.models.email import ImmichSyncLog
from app.utils.settings_utils import get_immich_settings

def sync_file_to_immich(file_path, filename, description=""):
    """Sync a file to Immich server"""
    try:
        immich_settings = get_immich_settings()
        if not immich_settings['enabled'] or not immich_settings['server_url'] or not immich_settings['api_key']:
            return False, "Immich sync not configured"
        
        # Check if file exists
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        # Prepare headers for Immich API
        headers = {
            'x-api-key': immich_settings['api_key'],
            'Content-Type': 'application/octet-stream'
        }
        
        # Upload file to Immich
        upload_url = f"{immich_settings['server_url'].rstrip('/')}/api/asset/upload"
        
        with open(file_path, 'rb') as f:
            files = {'assetData': (filename, f, 'application/octet-stream')}
            data = {
                'deviceAssetId': filename,
                'deviceId': 'wedding-gallery',
                'fileCreatedAt': datetime.now().isoformat(),
                'fileModifiedAt': datetime.now().isoformat(),
                'isFavorite': False,
                'fileExtension': Path(filename).suffix.lower().lstrip('.'),
                'description': description
            }
            
            response = requests.post(upload_url, headers=headers, files=files, data=data, timeout=30)
            
            if response.status_code == 201:
                asset_data = response.json()
                asset_id = asset_data.get('id')
                
                # Add to album if specified
                if immich_settings['album_name']:
                    album_url = f"{immich_settings['server_url'].rstrip('/')}/api/album/{immich_settings['album_name']}/assets"
                    album_data = {'ids': [asset_id]}
                    album_response = requests.put(album_url, headers=headers, json=album_data, timeout=10)
                
                return True, asset_id
            else:
                return False, f"Immich API error: {response.status_code} - {response.text}"
                
    except Exception as e:
        return False, f"Error syncing to Immich: {str(e)}"

def sync_all_to_immich():
    """Sync all eligible files to Immich"""
    try:
        immich_settings = get_immich_settings()
        if not immich_settings['enabled']:
            return False, "Immich sync not enabled"
        
        synced_count = 0
        error_count = 0
        
        # Sync photos
        if immich_settings['sync_photos']:
            photos = Photo.query.filter_by(media_type='image').all()
            for photo in photos:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
                description = f"Wedding photo by {photo.uploader_name}"
                if photo.description:
                    description += f" - {photo.description}"
                
                success, result = sync_file_to_immich(file_path, photo.filename, description)
                
                # Log sync attempt
                sync_log = ImmichSyncLog(
                    filename=photo.filename,
                    file_path=file_path,
                    status='success' if success else 'error',
                    immich_asset_id=result if success else None,
                    error_message=str(result) if not success else None
                )
                db.session.add(sync_log)
                
                if success:
                    synced_count += 1
                else:
                    error_count += 1
        
        # Sync videos
        if immich_settings['sync_videos']:
            videos = Photo.query.filter_by(media_type='video').all()
            for video in videos:
                file_path = os.path.join(current_app.config['VIDEO_FOLDER'], video.filename)
                description = f"Wedding video by {video.uploader_name}"
                if video.description:
                    description += f" - {video.description}"
                
                success, result = sync_file_to_immich(file_path, video.filename, description)
                
                sync_log = ImmichSyncLog(
                    filename=video.filename,
                    file_path=file_path,
                    status='success' if success else 'error',
                    immich_asset_id=result if success else None,
                    error_message=str(result) if not success else None
                )
                db.session.add(sync_log)
                
                if success:
                    synced_count += 1
                else:
                    error_count += 1
        
        # Sync guestbook photos
        if immich_settings['sync_guestbook']:
            guestbook_entries = GuestbookEntry.query.filter(GuestbookEntry.photo_filename.isnot(None)).all()
            for entry in guestbook_entries:
                file_path = os.path.join(current_app.config['GUESTBOOK_UPLOAD_FOLDER'], entry.photo_filename)
                description = f"Guestbook photo by {entry.name} from {entry.location}"
                if entry.message:
                    description += f" - {entry.message[:100]}"
                
                success, result = sync_file_to_immich(file_path, entry.photo_filename, description)
                
                sync_log = ImmichSyncLog(
                    filename=entry.photo_filename,
                    file_path=file_path,
                    status='success' if success else 'error',
                    immich_asset_id=result if success else None,
                    error_message=str(result) if not success else None
                )
                db.session.add(sync_log)
                
                if success:
                    synced_count += 1
                else:
                    error_count += 1
        
        # Sync message photos
        if immich_settings['sync_messages']:
            messages = Message.query.filter(Message.photo_filename.isnot(None)).all()
            for message in messages:
                file_path = os.path.join(current_app.config['MESSAGE_UPLOAD_FOLDER'], message.photo_filename)
                description = f"Message photo by {message.author_name}"
                if message.content:
                    description += f" - {message.content[:100]}"
                
                success, result = sync_file_to_immich(file_path, message.photo_filename, description)
                
                sync_log = ImmichSyncLog(
                    filename=message.photo_filename,
                    file_path=file_path,
                    status='success' if success else 'error',
                    immich_asset_id=result if success else None,
                    error_message=str(result) if not success else None
                )
                db.session.add(sync_log)
                
                if success:
                    synced_count += 1
                else:
                    error_count += 1
        
        # Sync photobooth photos
        if immich_settings['sync_photobooth']:
            photobooth_photos = Photo.query.filter_by(is_photobooth=True).all()
            for photo in photobooth_photos:
                file_path = os.path.join(current_app.config['PHOTOBOOTH_FOLDER'], photo.filename)
                description = f"Photobooth photo by {photo.uploader_name}"
                if photo.description:
                    description += f" - {photo.description}"
                
                success, result = sync_file_to_immich(file_path, photo.filename, description)
                
                sync_log = ImmichSyncLog(
                    filename=photo.filename,
                    file_path=file_path,
                    status='success' if success else 'error',
                    immich_asset_id=result if success else None,
                    error_message=str(result) if not success else None
                )
                db.session.add(sync_log)
                
                if success:
                    synced_count += 1
                else:
                    error_count += 1
        
        db.session.commit()
        return True, f"Synced {synced_count} files, {error_count} errors"
        
    except Exception as e:
        return False, f"Error during sync: {str(e)}" 
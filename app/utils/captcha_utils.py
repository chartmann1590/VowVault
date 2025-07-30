import random
import hashlib
import time
from flask import session

def generate_captcha():
    """Generate a simple math CAPTCHA challenge"""
    # Generate two random numbers between 1 and 20
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 20)
    
    # Choose a random operation
    operations = ['+', '-', '*']
    operation = random.choice(operations)
    
    # Calculate the correct answer
    if operation == '+':
        answer = num1 + num2
    elif operation == '-':
        answer = num1 - num2
    else:  # multiplication
        answer = num1 * num2
    
    # Create a unique challenge ID
    challenge_id = hashlib.md5(f"{num1}{operation}{num2}{time.time()}".encode()).hexdigest()[:8]
    
    # Store the answer in session
    session[f'captcha_{challenge_id}'] = answer
    session[f'captcha_time_{challenge_id}'] = time.time()
    
    return {
        'challenge_id': challenge_id,
        'question': f"{num1} {operation} {num2} = ?",
        'num1': num1,
        'num2': num2,
        'operation': operation
    }

def validate_captcha(challenge_id, user_answer):
    """Validate the CAPTCHA answer"""
    if not challenge_id or not user_answer:
        return False
    
    # Get the stored answer
    stored_answer = session.get(f'captcha_{challenge_id}')
    stored_time = session.get(f'captcha_time_{challenge_id}')
    
    if not stored_answer or not stored_time:
        return False
    
    # Check if CAPTCHA has expired (5 minutes)
    if time.time() - stored_time > 300:
        # Clean up expired CAPTCHA
        session.pop(f'captcha_{challenge_id}', None)
        session.pop(f'captcha_time_{challenge_id}', None)
        return False
    
    try:
        user_answer = int(user_answer.strip())
        is_correct = user_answer == stored_answer
    except (ValueError, TypeError):
        is_correct = False
    
    # Clean up the CAPTCHA after validation (one-time use)
    session.pop(f'captcha_{challenge_id}', None)
    session.pop(f'captcha_time_{challenge_id}', None)
    
    return is_correct

def is_captcha_enabled():
    """Check if CAPTCHA is enabled in settings"""
    from app.models.settings import Settings
    return Settings.get('captcha_enabled', 'false').lower() == 'true'

def get_captcha_settings():
    """Get CAPTCHA settings"""
    from app.models.settings import Settings
    return {
        'enabled': Settings.get('captcha_enabled', 'false').lower() == 'true',
        'upload_enabled': Settings.get('captcha_upload_enabled', 'true').lower() == 'true',
        'guestbook_enabled': Settings.get('captcha_guestbook_enabled', 'true').lower() == 'true',
        'message_enabled': Settings.get('captcha_message_enabled', 'true').lower() == 'true'
    } 
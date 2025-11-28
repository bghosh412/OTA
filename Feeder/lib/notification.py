# Notification handler using ntfy
import json
import gc

# Default topic (will be overridden by config if available)
ntfy_topic = 'FF0x98854'

# MicroPython-compatible notification sender
# Try urequests (MicroPython) first, fall back to requests (standard Python)
try:
    import urequests
except ImportError:
    try:
        import requests as urequests
    except ImportError:
        urequests = None

def send_ntfy_notification(message):
    if urequests is None:
        print('urequests not available, skipping notification')
        return
    
    # Free up memory before HTTPS request
    try:
        gc.collect()
    except:
        pass
    
    # Get topic from config at runtime (avoids circular import at module load)
    topic = ntfy_topic
    try:
        import config
        if hasattr(config, 'NTFY_TOPIC'):
            topic = config.NTFY_TOPIC
    except:
        pass  # Use default if config unavailable
    
    url = 'https://ntfy.sh/' + topic
    headers = {'Title': 'Auto Feeder'}
    try:
        r = urequests.post(url, data=message, headers=headers)
        r.close()
        print('Notification sent:', message)
    except Exception as e:
        print('ntfy notification error:', e)
        # Log error to event log
        try:
            import event_log_service
            event_log_service.log_event(event_log_service.EVENT_ERROR, 'Notification failed: {}'.format(str(e)))
        except:
            pass
    finally:
        # Clean up after notification
        try:
            gc.collect()
        except:
            pass

class NotificationService:
    """Send push notifications via ntfy.sh"""
    
    def __init__(self, server, topic=ntfy_topic):
        """
        Initialize notification service
        server: ntfy server URL (e.g., "https://ntfy.sh")
        topic: unique topic name for your device
        """
        self.server = server.rstrip('/')
        self.topic = topic
        self.url = f"{self.server}/{self.topic}"
    
    def send(self, message, title="Fish Feeder", priority=3):
        """
        Send notification
        priority: 1=min, 3=default, 5=max
        """
        # Free up memory before request
        try:
            gc.collect()
        except:
            pass

        try:
            headers = {
                'Title': title,
                'Priority': str(priority),
                'Tags': 'fish,food'
            }
            
            response = urequests.post(
                self.url,
                data=message.encode('utf-8'),
                headers=headers
            )
            
            success = response.status_code == 200
            response.close()
            
            # Clean up after request
            try:
                gc.collect()
            except:
                pass
                
            return success
            
        except Exception as e:
            print(f"Notification failed: {e}")
            
            # Log error to event log
            try:
                import event_log_service
                error_msg = str(e)
                if 'MemoryError' in error_msg or 'memory' in error_msg.lower():
                    event_log_service.log_event(event_log_service.EVENT_ERROR, 'Notification MemoryError')
                else:
                    event_log_service.log_event(event_log_service.EVENT_ERROR, f'Notification failed: {error_msg}')
            except:
                pass
                
            # Clean up after error
            try:
                gc.collect()
            except:
                pass
                
            return False
    
    def send_feeding_notification(self, time_str):
        """Send notification after successful feeding"""
        message = f"Fish fed successfully at {time_str}"
        return self.send(message, title="🐟 Feeding Complete")
    
    def send_error_notification(self, error):
        """Send notification on error"""
        message = f"Feeding error: {error}"
        return self.send(message, title="⚠️ Feeder Error", priority=4)

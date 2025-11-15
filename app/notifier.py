import httpx
import time

def notify_evaluation(evaluation_url, payload, max_retries=5):
    """Notify evaluation server with exponential backoff"""
    if not evaluation_url:
        print("⚠️ No evaluation URL provided")
        return False
    
    headers = {"Content-Type": "application/json"}
    delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"📨 Notification attempt {attempt + 1}/{max_retries}...")
            response = httpx.post(
                evaluation_url,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                print(f"✅ Evaluation server notified successfully")
                return True
            else:
                print(f"⚠️ Server responded with {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Notification attempt {attempt + 1} failed: {e}")
        
        if attempt < max_retries - 1:
            print(f"⏳ Waiting {delay}s before retry...")
            time.sleep(delay)
            delay *= 2
    
    print("❌ Failed to notify evaluation server after all retries")
    return False

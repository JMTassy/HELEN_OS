import pytest
import requests
import json
import os


@pytest.mark.skip(reason="manual integration test — requires live server at localhost:3333")
def test_chat_api():
    url = "http://localhost:3333/api/chat"
    payload = {
        "message": "HELEN, what is the current state of the system and what wisdom have you gathered recently?"
    }
    headers = {
        "Content-Type": "application/json"
    }

    print(f"Testing HELEN Chat API at {url}...")
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nHELEN Response:")
            print(json.dumps(data.get("helen", {}), indent=2))
            
            text = data.get("helen", {}).get("text", "")
            if "[HELEN]:" in text or len(text) > 100:
                print("\n✅ Verification SUCCESS: HELEN responded with complex text.")
            else:
                print("\n⚠️ Verification WARNING: Response seems short or unexpected.")
        else:
            print(f"\n❌ Verification FAILED: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Verification ERROR: {str(e)}")

if __name__ == "__main__":
    test_chat_api()

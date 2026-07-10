import subprocess
import time
import urllib.request
import urllib.error
import json
import sys
import os

BASE_URL = "http://127.0.0.1:8000"
SERVER_PROCESS = None

def make_request(url, method="GET", data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("Content-Type", "application/json")
    
    body = None
    if data:
        body = json.dumps(data).encode("utf-8")
        
    try:
        with urllib.request.urlopen(req, data=body, timeout=5) as response:
            res_body = response.read().decode("utf-8")
            return response.status, json.loads(res_body)
    except urllib.error.HTTPError as e:
        res_body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(res_body)
        except:
            return e.code, {"message": res_body}
    except Exception as e:
        return 0, {"message": str(e)}

def test_api():
    global SERVER_PROCESS
    print("--------------------------------------------------")
    print("STARTING FULL STACK API AUTOMATED VERIFICATION")
    print("--------------------------------------------------")
    
    # 1. Start Django Server
    print("[1] Launching Django Local Development Server...")
    manage_path = os.path.join(os.path.dirname(__file__), "manage.py")
    SERVER_PROCESS = subprocess.Popen(
        [sys.executable, manage_path, "runserver", "127.0.0.1:8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    # Wait for Django to start
    time.sleep(3)
    
    # Check if server is running
    status, res = make_request(f"{BASE_URL}/users/")
    if status == 0:
        print("ERROR: Django server failed to start or bind to port 8000.")
        if SERVER_PROCESS:
            SERVER_PROCESS.kill()
        sys.exit(1)
    
    print("Django Server running successfully.")
    print("MongoDB Atlas Ping status:", "CONNECTED" if status == 200 else f"UNAVAILABLE ({res.get('message')})")

    # Generate unique test username to avoid collision
    ts = int(time.time())
    user1 = f"test_alice_{ts}"
    user2 = f"test_bob_{ts}"
    
    # 2. Test User Registration
    print(f"\n[2] Registering test user '{user1}'...")
    reg_data = {
        "full_name": "Test Alice",
        "username": user1,
        "email": f"{user1}@example.com",
        "password": "supersecurepassword123",
        "profile_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    }
    status, data = make_request(f"{BASE_URL}/users/register/", "POST", reg_data)
    assert status == 201, f"Registration failed with status {status}: {data}"
    user1_id = data["user"]["user_id"]
    print(f"Success! Registered {user1} with User ID {user1_id}")

    # Test Duplicate Register Validation
    print("[2.1] Testing duplicate username registration validation...")
    status, data = make_request(f"{BASE_URL}/users/register/", "POST", reg_data)
    assert status == 400, "Validation failed: Duplicate user registered!"
    print("Success! Duplicate validation rejected duplicate registration as expected.")

    # Register second user for conversation partner
    print(f"[2.2] Registering conversation partner '{user2}'...")
    reg_data2 = {
        "full_name": "Test Bob",
        "username": user2,
        "email": f"{user2}@example.com",
        "password": "supersecurepassword456",
        "profile_image": ""
    }
    status, data = make_request(f"{BASE_URL}/users/register/", "POST", reg_data2)
    assert status == 201, "Partner registration failed"
    user2_id = data["user"]["user_id"]
    print(f"Success! Registered partner {user2}")

    # 3. Test Login
    print(f"\n[3] Logging in as user '{user1}'...")
    login_payload = {
        "username": user1,
        "password": "supersecurepassword123"
    }
    status, data = make_request(f"{BASE_URL}/users/login/", "POST", login_payload)
    assert status == 200, f"Login failed: {data}"
    print(f"Success! Token authentication user details: {data['user']['full_name']}")

    # 4. Test Get Users List
    print("\n[4] Requesting complete users list...")
    status, data = make_request(f"{BASE_URL}/users/")
    assert status == 200, "Failed to retrieve user directory"
    usernames = [u["username"] for u in data["users"]]
    assert user1 in usernames and user2 in usernames, "Users list is missing registered test users"
    print(f"Success! Retrieved {len(data['users'])} users from collection.")

    # 5. Test Update User Profile
    print(f"\n[5] Updating profile details for User ID '{user1_id}'...")
    update_payload = {
        "full_name": "Alice Cooper (Updated)",
        "email": f"{user1}_new@example.com"
    }
    status, data = make_request(f"{BASE_URL}/users/update/{user1_id}/", "PUT", update_payload)
    assert status == 200, f"Profile update failed: {data}"
    assert data["user"]["full_name"] == "Alice Cooper (Updated)", "Profile fields did not update successfully"
    print("Success! Full Name and Email updated.")

    # 6. Test Send Message
    print(f"\n[6] Sending chat message from '{user1}' to '{user2}'...")
    msg_payload = {
        "sender": user1,
        "receiver": user2,
        "message": "Hello Bob! How are you doing today?"
    }
    status, data = make_request(f"{BASE_URL}/chats/send/", "POST", msg_payload)
    assert status == 201, f"Message send failed: {data}"
    chat_id = data["chat"]["chat_id"]
    print(f"Success! Message sent with Chat ID {chat_id}")

    # 7. Test Conversations Endpoint
    print(f"\n[7] Checking active conversation listing for user '{user2}'...")
    status, data = make_request(f"{BASE_URL}/conversation/?logged_in_user={user2}")
    assert status == 200, "Conversations fetch failed"
    conversations = data["conversations"]
    assert len(conversations) > 0, "No active conversation summary returned"
    assert conversations[0]["partner_username"] == user1, "Conversation partner mismatch"
    assert conversations[0]["unread_count"] == 1, "Unread count indicator failed"
    print(f"Success! Conversation summary found. Unread count: {conversations[0]['unread_count']}")

    # 8. Test Retrieve Message details (will mark Bob's unread message as seen)
    print(f"\n[8] Loading chat messages between '{user2}' and '{user1}'...")
    status, data = make_request(f"{BASE_URL}/conversation/{user1}/{user2}/")
    assert status == 200, "Failed to load chronological messages"
    messages = data["messages"]
    assert len(messages) > 0, "Chronological message trace is empty"
    assert messages[0]["chat_id"] == chat_id, "Message content mismatch"
    print(f"Success! Chronological thread successfully loaded. Total messages: {len(messages)}")

    # Check that reading message marked unread counts as seen
    status, data = make_request(f"{BASE_URL}/conversation/?logged_in_user={user2}")
    assert data["conversations"][0]["unread_count"] == 0, "Message was not marked seen on fetch!"
    print("Verified: Message read automatically marked seen state to true.")

    # 9. Test Edit Message (Chat Update CRUD)
    print(f"\n[9] Modifying message content for Chat ID '{chat_id}'...")
    edit_payload = {
        "message": "Hello Bob! This is an updated message test."
    }
    status, data = make_request(f"{BASE_URL}/chats/update/{chat_id}/", "PUT", edit_payload)
    assert status == 200, "Message update failed"
    assert data["chat"]["message"] == "Hello Bob! This is an updated message test.", "Message text failed to update"
    print("Success! Message text updated.")

    # 10. Test Delete Message (Chat Delete CRUD)
    print(f"\n[10] Deleting message '{chat_id}'...")
    status, data = make_request(f"{BASE_URL}/chats/delete/{chat_id}/", "DELETE")
    assert status == 200, "Message delete request failed"
    print("Success! Message deleted successfully.")

    # 11. Test Delete User
    print(f"\n[11] Cleaning up and deleting User IDs '{user1_id}' and '{user2_id}'...")
    status, data = make_request(f"{BASE_URL}/users/delete/{user1_id}/", "DELETE")
    assert status == 200, "Failed to delete user 1"
    status, data = make_request(f"{BASE_URL}/users/delete/{user2_id}/", "DELETE")
    assert status == 200, "Failed to delete user 2"
    print("Success! Cleaned up test users from MongoDB cluster.")

    print("\n--------------------------------------------------")
    print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY! (100% PASS)")
    print("--------------------------------------------------")

if __name__ == "__main__":
    try:
        test_api()
    finally:
        if SERVER_PROCESS:
            print("Shutting down Django Server...")
            SERVER_PROCESS.kill()
            SERVER_PROCESS.wait()

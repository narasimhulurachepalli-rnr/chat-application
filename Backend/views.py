import json
import uuid
import datetime
import time
import random
import threading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password

try:
    from db import users_collection, chats_collection
except ImportError:
    from .db import users_collection, chats_collection

# --- Helper Functions for Serialization ---

def serialize_user(user):
    if not user:
        return None
    return {
        "user_id": user.get("user_id"),
        "full_name": user.get("full_name"),
        "username": user.get("username"),
        "email": user.get("email"),
        "profile_image": user.get("profile_image", ""),
        "last_seen": user.get("last_seen").isoformat() if isinstance(user.get("last_seen"), datetime.datetime) else user.get("last_seen"),
        "typing_to": user.get("typing_to", "")
    }

def serialize_chat(chat):
    if not chat:
        return None
    return {
        "chat_id": chat.get("chat_id"),
        "sender": chat.get("sender"),
        "receiver": chat.get("receiver"),
        "message": chat.get("message"),
        "sent_at": chat.get("sent_at").isoformat() if isinstance(chat.get("sent_at"), datetime.datetime) else chat.get("sent_at"),
        "seen": chat.get("seen", False)
    }

def db_unavailable_response():
    return JsonResponse({
        "status": "error",
        "message": "Database service is currently unavailable. Please check your MongoDB connection."
    }, status=503)


def seed_sample_data_if_empty():
    if users_collection is None:
        return
    try:
        # Check if individual sample users are missing, and insert them
        if not users_collection.find_one({"username": "nandini"}):
            users_collection.insert_one({
                "user_id": "4b6c31bf-4b47-4950-86ad-0648c6913c9e",
                "full_name": "Nandini Rachepalli",
                "username": "nandini",
                "email": "nandini@example.com",
                "password": make_password("password123"),
                "profile_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='100' height='100'><rect width='100%' height='100%' fill='%23128c7e'/><text x='50%' y='55%' font-size='30' fill='white' font-family='sans-serif' text-anchor='middle' dy='10'>N</text></svg>",
                "last_seen": datetime.datetime.utcnow(),
                "typing_to": ""
            })
            
        if not users_collection.find_one({"username": "rahul"}):
            users_collection.insert_one({
                "user_id": "9a38f38d-8a21-4f1e-9277-c99df602bbcc",
                "full_name": "Rahul Sharma",
                "username": "rahul",
                "email": "rahul@example.com",
                "password": make_password("password123"),
                "profile_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='100' height='100'><rect width='100%' height='100%' fill='%23075e54'/><text x='50%' y='55%' font-size='30' fill='white' font-family='sans-serif' text-anchor='middle' dy='10'>R</text></svg>",
                "last_seen": datetime.datetime.utcnow(),
                "typing_to": ""
            })
            
        if not users_collection.find_one({"username": "sneha"}):
            users_collection.insert_one({
                "user_id": "8a38f38d-8a21-4f1e-9277-c99df602bbcd",
                "full_name": "Sneha Patel",
                "username": "sneha",
                "email": "sneha@example.com",
                "password": make_password("password123"),
                "profile_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='100' height='100'><rect width='100%' height='100%' fill='%2334b7f1'/><text x='50%' y='55%' font-size='30' fill='white' font-family='sans-serif' text-anchor='middle' dy='10'>S</text></svg>",
                "last_seen": datetime.datetime.utcnow(),
                "typing_to": ""
            })
            
        if not users_collection.find_one({"username": "harshi"}):
            users_collection.insert_one({
                "user_id": "a238f38d-8a21-4f1e-9277-c99df602bbce",
                "full_name": "Harshi Reddy",
                "username": "harshi",
                "email": "harshi@example.com",
                "password": make_password("password123"),
                "profile_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='100' height='100'><rect width='100%' height='100%' fill='%239c27b0'/><text x='50%' y='55%' font-size='30' fill='white' font-family='sans-serif' text-anchor='middle' dy='10'>H</text></svg>",
                "last_seen": datetime.datetime.utcnow(),
                "typing_to": ""
            })
            
        if not users_collection.find_one({"username": "jyoshna"}):
            users_collection.insert_one({
                "user_id": "b238f38d-8a21-4f1e-9277-c99df602bbcf",
                "full_name": "Jyoshna Rao",
                "username": "jyoshna",
                "email": "jyoshna@example.com",
                "password": make_password("password123"),
                "profile_image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='100' height='100'><rect width='100%' height='100%' fill='%23e91e63'/><text x='50%' y='55%' font-size='30' fill='white' font-family='sans-serif' text-anchor='middle' dy='10'>J</text></svg>",
                "last_seen": datetime.datetime.utcnow(),
                "typing_to": ""
            })
            
        # Seed welcome messages if chats are empty
        if chats_collection is not None and chats_collection.count_documents({}) == 0:
            sample_chats = [
                {
                    "chat_id": "e4b6c31b-4b47-4950-86ad-0648c6913c9e",
                    "sender": "nandini",
                    "receiver": "rahul",
                    "message": "Hi Rahul! Welcome to our new Real-Time Chat App!",
                    "sent_at": datetime.datetime.utcnow() - datetime.timedelta(minutes=5),
                    "seen": True
                },
                {
                    "chat_id": "7c9df602-8a21-4f1e-9277-c99df602bbcc",
                    "sender": "rahul",
                    "receiver": "nandini",
                    "message": "Hello Nandini! The application looks absolutely stunning!",
                    "sent_at": datetime.datetime.utcnow() - datetime.timedelta(minutes=4),
                    "seen": False
                }
            ]
            chats_collection.insert_many(sample_chats)
    except Exception as e:
        print(f"Error seeding sample data: {e}")


# --- User Module APIs ---

@csrf_exempt
def register_user(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST method is allowed"}, status=405)
    
    if users_collection is None:
        return db_unavailable_response()

    seed_sample_data_if_empty()

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)


    full_name = data.get("full_name", "").strip()
    username = data.get("username", "").strip().lower()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    profile_image = data.get("profile_image", "").strip()

    # Required field validation
    if not all([full_name, username, email, password]):
        return JsonResponse({"status": "error", "message": "full_name, username, email, and password are required fields"}, status=400)

    # Password length validation
    if len(password) < 6:
        return JsonResponse({"status": "error", "message": "Password must be at least 6 characters long"}, status=400)

    # Duplicate username validation
    if users_collection.find_one({"username": username}):
        return JsonResponse({"status": "error", "message": "Username already exists"}, status=400)

    # Duplicate email validation
    if users_collection.find_one({"email": email}):
        return JsonResponse({"status": "error", "message": "Email already exists"}, status=400)

    hashed_password = make_password(password)
    user_id = str(uuid.uuid4())

    new_user = {
        "user_id": user_id,
        "full_name": full_name,
        "username": username,
        "email": email,
        "password": hashed_password,
        "profile_image": profile_image,
        "last_seen": datetime.datetime.utcnow()
    }

    users_collection.insert_one(new_user)
    return JsonResponse({
        "status": "success",
        "message": "User registered successfully",
        "user": serialize_user(new_user)
    }, status=201)


@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST method is allowed"}, status=405)

    if users_collection is None:
        return db_unavailable_response()

    seed_sample_data_if_empty()

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

    username = data.get("username", "").strip().lower()
    password = data.get("password", "")

    if not username or not password:
        return JsonResponse({"status": "error", "message": "Username and password are required"}, status=400)

    user = users_collection.find_one({"username": username})
    if not user:
        return JsonResponse({"status": "error", "message": "Invalid username or password"}, status=400)

    if not check_password(password, user["password"]):
        return JsonResponse({"status": "error", "message": "Invalid username or password"}, status=400)

    # Update last_seen on login
    users_collection.update_one({"username": username}, {"$set": {"last_seen": datetime.datetime.utcnow()}})
    user["last_seen"] = datetime.datetime.utcnow()

    return JsonResponse({
        "status": "success",
        "message": "Login successful",
        "user": serialize_user(user)
    }, status=200)


@csrf_exempt
def list_users(request):
    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Only GET method is allowed"}, status=405)

    if users_collection is None:
        return db_unavailable_response()

    seed_sample_data_if_empty()

    logged_in_user = request.GET.get("logged_in_user", "").strip().lower()
    try:
        if logged_in_user:
            users = list(users_collection.find({"username": {"$ne": logged_in_user}}))
        else:
            users = list(users_collection.find())
        serialized_users = [serialize_user(user) for user in users]
        return JsonResponse({
            "status": "success",
            "users": serialized_users
        }, status=200)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Database query failed: {e}"
        }, status=500)



@csrf_exempt
def update_user(request, user_id):
    if request.method != "PUT":
        return JsonResponse({"status": "error", "message": "Only PUT method is allowed"}, status=405)

    if users_collection is None:
        return db_unavailable_response()

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

    user = users_collection.find_one({"user_id": user_id})
    if not user:
        return JsonResponse({"status": "error", "message": "User not found"}, status=404)

    # Check if this is just a typing state heartbeat or full profile update
    if "typing_to" in data and len(data) == 1:
        update_fields = {
            "typing_to": data.get("typing_to", ""),
            "last_seen": datetime.datetime.utcnow()
        }
        users_collection.update_one({"user_id": user_id}, {"$set": update_fields})
        updated_user = users_collection.find_one({"user_id": user_id})
        return JsonResponse({
            "status": "success",
            "message": "Typing status updated",
            "user": serialize_user(updated_user)
        }, status=200)

    full_name = data.get("full_name", user.get("full_name")).strip()
    email = data.get("email", user.get("email")).strip().lower()
    profile_image = data.get("profile_image", user.get("profile_image"))
    typing_to = data.get("typing_to", user.get("typing_to", ""))

    if not full_name or not email:
        return JsonResponse({"status": "error", "message": "full_name and email cannot be empty"}, status=400)

    # Email uniqueness check
    existing_user_email = users_collection.find_one({"email": email, "user_id": {"$ne": user_id}})
    if existing_user_email:
        return JsonResponse({"status": "error", "message": "Email is already in use by another user"}, status=400)

    update_fields = {
        "full_name": full_name,
        "email": email,
        "profile_image": profile_image,
        "typing_to": typing_to,
        "last_seen": datetime.datetime.utcnow()
    }

    users_collection.update_one({"user_id": user_id}, {"$set": update_fields})
    updated_user = users_collection.find_one({"user_id": user_id})

    return JsonResponse({
        "status": "success",
        "message": "User updated successfully",
        "user": serialize_user(updated_user)
    }, status=200)


@csrf_exempt
def delete_user(request, user_id):
    if request.method != "DELETE":
        return JsonResponse({"status": "error", "message": "Only DELETE method is allowed"}, status=405)

    if users_collection is None:
        return db_unavailable_response()

    user = users_collection.find_one({"user_id": user_id})
    if not user:
        return JsonResponse({"status": "error", "message": "User not found"}, status=404)

    # Delete the user
    users_collection.delete_one({"user_id": user_id})

    # Delete all chats involving this user (either as sender or receiver)
    username = user.get("username")
    if chats_collection is not None and username:
        chats_collection.delete_many({"$or": [{"sender": username}, {"receiver": username}]})

    return JsonResponse({
        "status": "success",
        "message": f"User {username} and their related chat history have been deleted."
    }, status=200)


def simulate_bot_reply(sender_username, receiver_username, original_message):
    time.sleep(1.5)
    if chats_collection is None:
        return
    
    # Do not reply if the receiver has been online in the last 15 seconds
    if users_collection is not None:
        receiver = users_collection.find_one({"username": receiver_username})
        if receiver and receiver.get("last_seen"):
            last_seen = receiver.get("last_seen")
            if isinstance(last_seen, datetime.datetime):
                diff = (datetime.datetime.utcnow() - last_seen).total_seconds()
                if diff <= 15:
                    return

    msg_lower = original_message.lower().strip()
    words = msg_lower.split()
    
    # Check bot identities and contextual matching
    if receiver_username == "harshi":
        # Harshi Reddy persona: energetic, friendly, sweet friend
        if any(x in words for x in ["hi", "hello", "hey", "yo", "heyy", "heyyy", "hii", "hiii"]):
            bot_message = "Heyyy! Omg hello!! So glad you texted me, what's up? how are you?? 🥰"
        elif any(x in msg_lower for x in ["how are you", "how r u", "how is it going", "hru"]):
            bot_message = "I'm doing great! Just finished eating some snacks, hbu?? everything good? 🌸"
        elif any(x in msg_lower for x in ["what are you doing", "what's up", "sup", "what r u doing", "what are u doing"]):
            bot_message = "Nothing much, just listening to some music and scrolling on reels lol. what are you up to? 🎶"
        elif any(x in msg_lower for x in ["where are you from", "where do you live", "where are u from", "where u from"]):
            bot_message = "I'm from Hyderabad! Where are you from? 🌍✨"
        elif any(x in msg_lower for x in ["bye", "goodnight", "see ya", "tc"]):
            bot_message = "Aww okay, talk to you later then! tc, bye bye! ❤️"
        elif any(x in msg_lower for x in ["nice", "good", "great", "cool"]):
            bot_message = "Awesome! Glad to hear that haha, ikr! 🎉"
        else:
            bot_message = "Aww that's so nice! Tell me more about it, I'm listening! 💬"
            
    elif receiver_username == "jyoshna":
        # Jyoshna Rao persona: cool, chill friend
        if any(x in words for x in ["hi", "hello", "hey", "yo", "heyy", "heyyy", "hii", "hiii"]):
            bot_message = "Hey! What's up? how have you been? glad you pinged! 😊"
        elif any(x in msg_lower for x in ["how are you", "how r u", "how is it going", "hru"]):
            bot_message = "I'm good, thanks! Just got back from college, you tell? how is life treating you?"
        elif any(x in msg_lower for x in ["what are you doing", "what's up", "sup", "what r u doing", "what are u doing"]):
            bot_message = "just having some tea and doing some homework. hbu? doing anything fun? ☕"
        elif any(x in msg_lower for x in ["where are you from", "where do you live", "where are u from", "where u from"]):
            bot_message = "I live in Bangalore! What about you? where do you stay? 🏡"
        elif any(x in msg_lower for x in ["bye", "goodnight", "see ya", "tc"]):
            bot_message = "Okay catch you later! take care and have a good one, bye! 👋"
        elif any(x in msg_lower for x in ["nice", "good", "great", "cool"]):
            bot_message = "cool, glad to hear that! standard stuff haha"
        else:
            bot_message = "damn really? that's crazy! let me know how it goes! 👍"

    else:
        # Default bots (rahul, sneha, or other manually added contacts)
        if any(x in words for x in ["hi", "hello", "hey", "yo"]):
            bot_message = f"Hey friend! What's up? how are you? - {receiver_username.capitalize()} 👋"
        elif any(x in msg_lower for x in ["how are you", "how r u", "hru"]):
            bot_message = "I'm doing good! How are you doing today? everything fine?"
        elif any(x in msg_lower for x in ["what are you doing", "what's up", "sup"]):
            bot_message = "just chilling at home and chatting with you. what about you?"
        elif any(x in msg_lower for x in ["where are you from", "where do you live"]):
            bot_message = f"I'm from Delhi! Where are you from?"
        elif any(x in msg_lower for x in ["bye", "goodnight"]):
            bot_message = "Bye! Talk to you later, take care! 👋"
        else:
            bot_message = "Oh nice! That sounds cool. Let's talk more later!"

    chat_id = str(uuid.uuid4())
    new_chat = {
        "chat_id": chat_id,
        "sender": receiver_username,
        "receiver": sender_username,
        "message": bot_message,
        "sent_at": datetime.datetime.utcnow(),
        "seen": False
    }
    chats_collection.insert_one(new_chat)


# --- Chat Module APIs ---

@csrf_exempt
def send_message(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST method is allowed"}, status=405)

    if chats_collection is None:
        return db_unavailable_response()

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

    sender = data.get("sender", "").strip().lower()
    receiver = data.get("receiver", "").strip().lower()
    message = data.get("message", "").strip()

    if not sender or not receiver or not message:
        return JsonResponse({"status": "error", "message": "sender, receiver, and message are required fields"}, status=400)

    # Verify sender and receiver exist
    if users_collection is not None:
        if not users_collection.find_one({"username": sender}):
            return JsonResponse({"status": "error", "message": f"Sender '{sender}' does not exist"}, status=400)
        if not users_collection.find_one({"username": receiver}):
            return JsonResponse({"status": "error", "message": f"Receiver '{receiver}' does not exist"}, status=400)

    chat_id = str(uuid.uuid4())
    new_chat = {
        "chat_id": chat_id,
        "sender": sender,
        "receiver": receiver,
        "message": message,
        "sent_at": datetime.datetime.utcnow(),
        "seen": False
    }

    chats_collection.insert_one(new_chat)
    
    # Spawn background thread to simulate reply
    threading.Thread(target=simulate_bot_reply, args=(sender, receiver, message), daemon=True).start()

    return JsonResponse({
        "status": "success",
        "message": "Message sent successfully",
        "chat": serialize_chat(new_chat)
    }, status=201)


@csrf_exempt
def list_chats(request):
    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Only GET method is allowed"}, status=405)

    if chats_collection is None:
        return db_unavailable_response()

    chats = list(chats_collection.find().sort("sent_at", 1))
    serialized_chats = [serialize_chat(chat) for chat in chats]
    return JsonResponse({
        "status": "success",
        "chats": serialized_chats
    }, status=200)


@csrf_exempt
def update_message(request, chat_id):
    if request.method != "PUT":
        return JsonResponse({"status": "error", "message": "Only PUT method is allowed"}, status=405)

    if chats_collection is None:
        return db_unavailable_response()

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

    new_message = data.get("message", "").strip()
    if not new_message:
        return JsonResponse({"status": "error", "message": "message field cannot be empty"}, status=400)

    chat = chats_collection.find_one({"chat_id": chat_id})
    if not chat:
        return JsonResponse({"status": "error", "message": "Message not found"}, status=404)

    chats_collection.update_one({"chat_id": chat_id}, {"$set": {"message": new_message, "updated_at": datetime.datetime.utcnow()}})
    updated_chat = chats_collection.find_one({"chat_id": chat_id})

    return JsonResponse({
        "status": "success",
        "message": "Message updated successfully",
        "chat": serialize_chat(updated_chat)
    }, status=200)


@csrf_exempt
def delete_message(request, chat_id):
    if request.method != "DELETE":
        return JsonResponse({"status": "error", "message": "Only DELETE method is allowed"}, status=405)

    if chats_collection is None:
        return db_unavailable_response()

    chat = chats_collection.find_one({"chat_id": chat_id})
    if not chat:
        return JsonResponse({"status": "error", "message": "Message not found"}, status=404)

    chats_collection.delete_one({"chat_id": chat_id})
    return JsonResponse({
        "status": "success",
        "message": "Message deleted successfully"
    }, status=200)


# --- Conversation Module APIs ---

@csrf_exempt
def list_conversations(request):
    """
    GET /conversation/
    Returns a summary of all active conversations involving the logged-in user.
    Pass username via query param: /conversation/?logged_in_user=username
    """
    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Only GET method is allowed"}, status=405)

    if chats_collection is None or users_collection is None:
        return db_unavailable_response()

    logged_in_user = request.GET.get("logged_in_user", "").strip().lower()
    if not logged_in_user:
        return JsonResponse({"status": "error", "message": "logged_in_user query parameter is required"}, status=400)

    # Find all chats involving the logged_in_user
    pipeline = [
        {
            "$match": {
                "$or": [
                    {"sender": logged_in_user},
                    {"receiver": logged_in_user}
                ]
            }
        },
        {
            "$sort": {"sent_at": -1}
        },
        {
            "$group": {
                "_id": {
                    "$cond": [
                        {"$eq": ["$sender", logged_in_user]},
                        "$receiver",
                        "$sender"
                    ]
                },
                "last_message": {"$first": "$message"},
                "sent_at": {"$first": "$sent_at"},
                "chat_id": {"$first": "$chat_id"},
                "sender": {"$first": "$sender"},
                "receiver": {"$first": "$receiver"},
                "seen": {"$first": "$seen"}
            }
        },
        {
            "$sort": {"sent_at": -1}
        }
    ]

    grouped_conversations = list(chats_collection.aggregate(pipeline))
    conversations = []

    for conv in grouped_conversations:
        partner_username = conv["_id"]
        partner = users_collection.find_one({"username": partner_username})
        
        # Calculate unread count for messages from partner to logged_in_user
        unread_count = chats_collection.count_documents({
            "sender": partner_username,
            "receiver": logged_in_user,
            "seen": False
        })

        conversations.append({
            "partner_username": partner_username,
            "partner_full_name": partner.get("full_name") if partner else partner_username,
            "partner_profile_image": partner.get("profile_image") if partner else "",
            "partner_last_seen": partner.get("last_seen").isoformat() if partner and isinstance(partner.get("last_seen"), datetime.datetime) else None,
            "last_message": conv["last_message"],
            "sent_at": conv["sent_at"].isoformat() if isinstance(conv["sent_at"], datetime.datetime) else conv["sent_at"],
            "unread_count": unread_count,
            "chat_id": conv["chat_id"],
            "last_sender": conv["sender"]
        })

    return JsonResponse({
        "status": "success",
        "conversations": conversations
    }, status=200)


@csrf_exempt
def conversation_detail(request, username):
    """
    GET /conversation/<username>/
    Returns the message exchange between logged_in_user and <username> in chronological order.
    Sets all incoming messages from <username> to the logged_in_user to "seen: true".
    Pass logged_in_user via query param: /conversation/<username>/?logged_in_user=username
    """
    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Only GET method is allowed"}, status=405)

    if chats_collection is None:
        return db_unavailable_response()

    logged_in_user = request.GET.get("logged_in_user", "").strip().lower()
    partner_username = username.strip().lower()

    if not logged_in_user:
        return JsonResponse({"status": "error", "message": "logged_in_user query parameter is required"}, status=400)

    # Set incoming messages from partner to logged_in_user to seen
    chats_collection.update_many(
        {"sender": partner_username, "receiver": logged_in_user, "seen": False},
        {"$set": {"seen": True}}
    )

    # Fetch messages between logged_in_user and partner_username
    query = {
        "$or": [
            {"sender": logged_in_user, "receiver": partner_username},
            {"sender": partner_username, "receiver": logged_in_user}
        ]
    }
    messages = list(chats_collection.find(query).sort("sent_at", 1))
    serialized_messages = [serialize_chat(msg) for msg in messages]

    # Get partner info for status/last seen
    partner_info = {}
    if users_collection is not None:
        partner = users_collection.find_one({"username": partner_username})
        if partner:
            partner_info = serialize_user(partner)

    return JsonResponse({
        "status": "success",
        "partner": partner_info,
        "messages": serialized_messages
    }, status=200)


@csrf_exempt
def conversation_detail_two_users(request, sender, receiver):
    """
    GET /conversation/<sender>/<receiver>/
    Returns messages between sender and receiver in chronological order.
    Marks messages from sender to receiver as seen (seen = True).
    """
    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Only GET method is allowed"}, status=405)

    if chats_collection is None:
        return db_unavailable_response()

    sender_username = sender.strip().lower()
    receiver_username = receiver.strip().lower()

    # Mark incoming messages from sender to receiver as seen
    chats_collection.update_many(
        {"sender": sender_username, "receiver": receiver_username, "seen": False},
        {"$set": {"seen": True}}
    )

    # Fetch all messages between sender and receiver
    query = {
        "$or": [
            {"sender": sender_username, "receiver": receiver_username},
            {"sender": receiver_username, "receiver": sender_username}
        ]
    }
    messages = list(chats_collection.find(query).sort("sent_at", 1))
    serialized_messages = [serialize_chat(msg) for msg in messages]

    # Get partner info (from sender parameter, which represents the other user)
    partner_info = {}
    if users_collection is not None:
        partner = users_collection.find_one({"username": sender_username})
        if partner:
            partner_info = serialize_user(partner)

    return JsonResponse({
        "status": "success",
        "partner": partner_info,
        "messages": serialized_messages
    }, status=200)


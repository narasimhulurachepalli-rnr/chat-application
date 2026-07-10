<<<<<<< HEAD
# Real-Time Full Stack Chat Application

A high-performance, real-time chat application built with a **Django 4.2.7 REST API** backend, a **MongoDB Atlas (PyMongo)** database, and an ultra-premium, **Vanilla Glassmorphic HTML5/CSS3/ES6 JavaScript** frontend. 

No frameworks (No React, Angular, Vue, Tailwind, or Bootstrap) were used in the client layer, achieving maximum speed, micro-animations, and complete device compatibility (from 320px to 1440px+ viewports).

---

## Folder Structure

```
RealTimeChat/
│
├── Backend/
│   ├── config.py             # MongoDB connection URI configurations
│   ├── db.py                 # PyMongo connection initialization & ping checks
│   ├── manage.py             # Django project administration entrypoint
│   ├── requirements.txt      # PyPI backend dependencies
│   ├── settings.py           # Django environment configurations & CORS setups
│   ├── urls.py               # API route maps mapping endpoints to views
│   ├── views.py              # Function-based CRUD views and validation checkers
│   ├── wsgi.py               # WSGI server loader configuration
│   ├── test_api.py           # Automated full stack REST verification script
│   ├── sample_data.json      # Pre-formatted sample MongoDB documents
│   └── postman_collection.json # Ready-to-import Postman JSON collection
│
└── Frontend/
    ├── index.html            # Landing page (Welcome banner, hero, details, action links)
    ├── login.html            # Glassmorphic Login card & actions
    ├── register.html         # User registration form with profile image uploads
    ├── dashboard.html        # WhatsApp style sidebar/chat panels & settings modals
    ├── style.css             # Fluid responsive layout & theme variables
    └── script.js             # Client core engine, polling, typing triggers, CRUD helpers
```

---

## Features

- **Real-Time Polling Engine**: Automatically fetches new chats, updates read metrics, and reviews online status flags every 3 seconds.
- **Full User & Message CRUD**: Supports registering user accounts, editing credentials, deleting profiles, transmitting messages, editing content, and deleting logs.
- **Glassmorphic WhatsApp-Style UI**: Sleek, modern, and immersive responsive layouts featuring soft blurs, green accents, and card shadows.
- **Database-Backed Live Typing Indicator**: Instantly alerts users when contacts are active and typing to them.
- **Dynamic Seen/Unseen Tick Indicators**: Renders single grey checkmark for successfully sent chats, and double blue checkmarks when messages are read.
- **Dark & Light Themes**: Responsive toggle instantly transitions styles and saves choices locally.
- **In-Browser Image Encoder**: Converted profile image selections into Base64 format for server transmission.
- **Emoji Picker Grid**: Quick picker inputs popular emojis into messages instantly.
- **Automatic Form Validation & Toasting**: Informative prompts and alert overlays display process states.

---

## Installation & Setups

### Prerequisites
- Python 3.9+
- Modern Web Browser
- MongoDB Atlas Cluster Access

---

### 1. MongoDB Atlas Setup
This application is configured with a live MongoDB Atlas connection string:
`mongodb+srv://rachepallinandini_db_user:Nandini2005@cluster0.dli41nw.mongodb.net/`

If you need to change this database path:
1. Open [config.py](file:///c:/Users/Sivalakshmi/Documents/full%20stack/chat%20application/Backend/config.py).
2. Modify `MONGO_URI` to point to your new connection string.
3. Modify `DB_NAME` to specify your collection namespace.

---

### 2. Django Setup

1. Open your terminal and navigate to the `Backend` directory:
   ```bash
   cd Backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```
   Django will check the database connection and report:
   `Database connection successfully established with MongoDB Atlas.`

---

### 3. Frontend Setup

The frontend connects directly to `http://127.0.0.1:8000` via AJAX/Fetch. 
1. Open [index.html](file:///c:/Users/Sivalakshmi/Documents/full%20stack/chat%20application/Frontend/index.html) in any browser (by double-clicking or hosting locally on a static server).
2. You can register accounts, log in, and open chats. Use multiple browser profiles or incognito sessions to simulate multiple concurrent users chatting in real-time.

---

## API Endpoints Reference

### User Module
| Endpoint | Method | Payload / Action |
| :--- | :--- | :--- |
| `/users/register/` | `POST` | Registers profile. Requires: `full_name`, `username`, `email`, `password`, `profile_image` |
| `/users/login/` | `POST` | Log in. Requires: `username`, `password` |
| `/users/` | `GET` | Directory list of all registered users (excluding password) |
| `/users/update/<id>/` | `PUT` | Updates profile name, email, avatar, or sends typing heartbeat |
| `/users/delete/<id>/` | `DELETE` | Permanently deletes user profile and associated chat records |

### Chat Module
| Endpoint | Method | Payload / Action |
| :--- | :--- | :--- |
| `/chats/send/` | `POST` | Send a new message. Requires: `sender`, `receiver`, `message` |
| `/chats/` | `GET` | List all global messages sorted chronologically |
| `/chats/update/<id>/` | `PUT` | Edit message content |
| `/chats/delete/<id>/` | `DELETE` | Remove message |

### Conversation Module
| Endpoint | Method | Payload / Action |
| :--- | :--- | :--- |
| `/conversation/?logged_in_user=<username>` | `GET` | Summary list of user's active contacts, last message, and unread counts |
| `/conversation/<username>/?logged_in_user=<my_username>` | `GET` | Chronological chat history between two users (marks incoming as read) |

---

## Running Automated Verification Suite

To verify the REST layer, a testing suite is included:
```bash
cd Backend
python test_api.py
```
This script boots up the local server, creates test profiles, verifies validations, sends messages, updates texts, retrieves threads, and cleans up database states automatically.

---

## Author
Senior Full Stack Developer

## License
MIT License. Open for development and educational use.
=======
# chat-application
>>>>>>> 79d1c6b63391d5e1755c9c07fcd341170983793a

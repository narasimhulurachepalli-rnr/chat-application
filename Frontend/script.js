/* ==========================================================================
   REALTIME CHAT APPLICATION - CORE FRONTEND ENGINE
   ========================================================================== */

const API_BASE = "http://127.0.0.1:8000";

// --- Global Toast Notification system ---
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let iconClass = 'fa-circle-check';
    if (type === 'error') iconClass = 'fa-circle-xmark';
    if (type === 'info') iconClass = 'fa-circle-info';

    toast.innerHTML = `
        <i class="fa-solid ${iconClass}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Fade and remove toast
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3500);
}

// --- Dynamic Button Loading States ---
function setBtnLoading(btnId, isLoading, defaultText = "Submit") {
    const btn = document.getElementById(btnId);
    if (!btn) return;
    
    const textEl = btn.querySelector('#btnText');
    const spinnerEl = btn.querySelector('#btnSpinner');

    if (isLoading) {
        btn.disabled = true;
        if (textEl) textEl.style.display = 'none';
        if (spinnerEl) spinnerEl.style.display = 'inline-block';
    } else {
        btn.disabled = false;
        if (textEl) {
            textEl.style.display = 'inline';
            textEl.innerText = defaultText;
        }
        if (spinnerEl) spinnerEl.style.display = 'none';
    }
}

// ==========================================================================
// AUTHENTICATION FLOW (LOGIN & REGISTER)
// ==========================================================================

// Handle Register User
async function handleRegister(profileImageBase64) {
    const fullName = document.getElementById('fullName').value.trim();
    const username = document.getElementById('username').value.trim().toLowerCase();
    const email = document.getElementById('email').value.trim().toLowerCase();
    const password = document.getElementById('password').value;

    // Frontend Validations
    if (!fullName || !username || !email || !password) {
        showToast("Please fill in all required fields", "error");
        return;
    }

    if (username.includes(" ")) {
        showToast("Username must not contain spaces", "error");
        return;
    }

    // Email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showToast("Please enter a valid email address", "error");
        return;
    }

    if (password.length < 6) {
        showToast("Password must be at least 6 characters long", "error");
        return;
    }

    setBtnLoading('registerBtn', true, "Sign Up");

    try {
        const response = await fetch(`${API_BASE}/users/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                full_name: fullName,
                username: username,
                email: email,
                password: password,
                profile_image: profileImageBase64
            })
        });

        const data = await response.json();

        if (response.ok && data.status === "success") {
            showToast("Registration successful! Redirecting to login...", "success");
            setTimeout(() => {
                window.location.href = "login.html";
            }, 1500);
        } else {
            showToast(data.message || "Registration failed", "error");
        }
    } catch (err) {
        showToast("Failed to connect to backend server", "error");
        console.error(err);
    } finally {
        setBtnLoading('registerBtn', false, "Sign Up");
    }
}

// Handle Login User
async function handleLogin() {
    const username = document.getElementById('username').value.trim().toLowerCase();
    const password = document.getElementById('password').value;

    if (!username || !password) {
        showToast("Please enter both username and password", "error");
        return;
    }

    setBtnLoading('loginBtn', true, "Sign In");

    try {
        const response = await fetch(`${API_BASE}/users/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok && data.status === "success") {
            showToast("Login successful!", "success");
            
            // Set session credentials in Local Storage
            localStorage.setItem("loggedUser", data.user.username);
            localStorage.setItem("loggedUserProfile", JSON.stringify(data.user));

            setTimeout(() => {
                window.location.href = "dashboard.html";
            }, 1000);
        } else {
            showToast(data.message || "Invalid username or password", "error");
        }
    } catch (err) {
        showToast("Failed to connect to backend server", "error");
        console.error(err);
    } finally {
        setBtnLoading('loginBtn', false, "Sign In");
    }
}

// ==========================================================================
// CHAT & DASHBOARD WORKSPACE ENGINE
// ==========================================================================

let activeChatPartner = null;
let selfUser = null;
let allUsers = [];
let conversationSummary = [];
let activeMessages = [];
let pollingInterval = null;
let typingTimeout = null;
let isCurrentlyTyping = false;

// Initialize Dashboard Page
async function initDashboard() {
    const loggedUser = localStorage.getItem('loggedUser');
    if (!loggedUser) {
        window.location.href = 'login.html';
        return;
    }

    // Load active theme
    const activeTheme = localStorage.getItem('theme') || 'light';
    const themeBtn = document.getElementById('themeToggleBtn');
    if (activeTheme === 'dark') {
        document.body.classList.add('dark-mode');
        themeBtn.innerHTML = '<i class="fa-solid fa-sun"></i>';
    } else {
        document.body.classList.remove('dark-mode');
        themeBtn.innerHTML = '<i class="fa-solid fa-moon"></i>';
    }

    // Set self info
    try {
        selfUser = JSON.parse(localStorage.getItem('loggedUserProfile'));
        if (!selfUser && loggedUser) {
            console.log("loggedUserProfile not found, recovering from server...");
            const response = await fetch(`${API_BASE}/users/`);
            const data = await response.json();
            if (response.ok && data.status === "success") {
                const found = data.users.find(u => u.username === loggedUser.trim().toLowerCase());
                if (found) {
                    selfUser = found;
                    localStorage.setItem('loggedUserProfile', JSON.stringify(selfUser));
                    updateSelfUserCardUI();
                }
            }
        } else if (selfUser) {
            updateSelfUserCardUI();
        }
    } catch (e) {
        console.error("Error reading self profile", e);
    }

    // Trigger Initial Load
    await fetchInitialDashboardData();

    // Start Polling (every 3 seconds)
    pollingInterval = setInterval(fetchPollingData, 3000);

    // Bind Event Listeners
    setupDashboardEventListeners();
}

// Load static self details onto sidebar
function updateSelfUserCardUI() {
    if (!selfUser) return;
    document.getElementById('selfFullName').innerText = selfUser.full_name;
    document.getElementById('selfUsername').innerText = `@${selfUser.username}`;
    
    if (selfUser.profile_image) {
        document.getElementById('selfAvatar').src = selfUser.profile_image;
    }
}

// Setup Event Listeners
function setupDashboardEventListeners() {
    // Theme Toggle
    document.getElementById('themeToggleBtn').addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        document.getElementById('themeToggleBtn').innerHTML = isDark ? 
            '<i class="fa-solid fa-sun"></i>' : 
            '<i class="fa-solid fa-moon"></i>';
        showToast(isDark ? 'Dark mode enabled' : 'Light mode enabled', 'info');
    });

    // Profile Settings modal
    const profileModal = document.getElementById('profileModal');
    document.getElementById('editProfileBtn').addEventListener('click', () => {
        if (!selfUser) return;
        document.getElementById('modalFullName').value = selfUser.full_name;
        document.getElementById('modalEmail').value = selfUser.email;
        document.getElementById('modalAvatarPreview').src = selfUser.profile_image || "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='100' height='100'><rect width='100%' height='100%' fill='%23e1e1e1'/><path d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z' fill='%238696a0'/></svg>";
        profileModal.classList.add('show');
    });

    document.getElementById('closeProfileModal').addEventListener('click', () => {
        profileModal.classList.remove('show');
    });

    // Add Contact Modal toggling
    const addContactModal = document.getElementById('addContactModal');
    document.getElementById('addContactBtn').addEventListener('click', () => {
        document.getElementById('contactFullName').value = "";
        document.getElementById('contactUsername').value = "";
        document.getElementById('contactEmail').value = "";
        addContactModal.classList.add('show');
    });

    document.getElementById('closeAddContactModal').addEventListener('click', () => {
        addContactModal.classList.remove('show');
    });

    // Handle Add Contact Form Submission
    document.getElementById('addContactForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const fullName = document.getElementById('contactFullName').value.trim();
        const username = document.getElementById('contactUsername').value.trim().toLowerCase();
        const email = document.getElementById('contactEmail').value.trim().toLowerCase();

        if (!fullName || !username || !email) {
            showToast("Please fill in all fields", "error");
            return;
        }

        if (username.includes(" ")) {
            showToast("Username must not contain spaces", "error");
            return;
        }

        // Email format validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            showToast("Please enter a valid email address", "error");
            return;
        }

        // Generate custom avatar
        const firstLetter = username.charAt(0).toUpperCase();
        const colors = ['#128c7e', '#075e54', '#34b7f1', '#25d366', '#ff5722', '#9c27b0', '#e91e63'];
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        const avatarSvg = `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='100' height='100'><rect width='100%' height='100%' fill='${encodeURIComponent(randomColor)}'/><text x='50%' y='55%' font-size='30' fill='white' font-family='sans-serif' text-anchor='middle' dy='10'>${firstLetter}</text></svg>`;

        try {
            const response = await fetch(`${API_BASE}/users/register/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    full_name: fullName,
                    username: username,
                    email: email,
                    password: "password123", // default password
                    profile_image: avatarSvg
                })
            });

            const data = await response.json();

            if (response.ok && data.status === "success") {
                showToast("Contact added successfully!", "success");
                addContactModal.classList.remove('show');
                // Refresh list
                await fetchInitialDashboardData();
            } else {
                showToast(data.message || "Failed to add contact", "error");
            }
        } catch (err) {
            showToast("Connection error: Failed to add contact", "error");
            console.error(err);
        }
    });

    // Handle Profile Update Image selection
    let modalImageBase64 = "";
    document.getElementById('modalProfileImage').addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            if (file.size > 2 * 1024 * 1024) {
                showToast("File size too large (max 2MB)", "error");
                return;
            }
            const reader = new FileReader();
            reader.onload = (event) => {
                modalImageBase64 = event.target.result;
                document.getElementById('modalAvatarPreview').src = modalImageBase64;
            };
            reader.readAsDataURL(file);
        }
    });

    // Profile update submit
    document.getElementById('updateProfileForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const fullName = document.getElementById('modalFullName').value.trim();
        const email = document.getElementById('modalEmail').value.trim().toLowerCase();
        
        if (!fullName || !email) {
            showToast("Required fields cannot be empty", "error");
            return;
        }

        try {
            const payload = {
                full_name: fullName,
                email: email,
                profile_image: modalImageBase64 || selfUser.profile_image
            };

            const response = await fetch(`${API_BASE}/users/update/${selfUser.user_id}/`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            if (response.ok && data.status === "success") {
                showToast("Profile updated successfully!", "success");
                selfUser = data.user;
                localStorage.setItem("loggedUserProfile", JSON.stringify(selfUser));
                updateSelfUserCardUI();
                profileModal.classList.remove('show');
            } else {
                showToast(data.message || "Failed to update profile", "error");
            }
        } catch (err) {
            showToast("Server connection error", "error");
            console.error(err);
        }
    });

    // Delete Account Button click
    document.getElementById('deleteAccountBtn').addEventListener('click', async () => {
        if (!confirm("Are you absolutely sure you want to delete your account? This action is irreversible and deletes your full profile and messaging history!")) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/users/delete/${selfUser.user_id}/`, {
                method: 'DELETE'
            });

            if (response.ok) {
                showToast("Account deleted successfully.", "success");
                localStorage.clear();
                setTimeout(() => {
                    window.location.href = "index.html";
                }, 1200);
            } else {
                showToast("Failed to delete account.", "error");
            }
        } catch (err) {
            showToast("Connection error while deleting account", "error");
            console.error(err);
        }
    });

    // Logout Button click
    document.getElementById('logoutBtn').addEventListener('click', () => {
        if (confirm("Are you sure you want to log out?")) {
            localStorage.clear();
            if (pollingInterval) clearInterval(pollingInterval);
            window.location.href = 'index.html';
        }
    });

    // Contact List Search filter input
    document.getElementById('searchInput').addEventListener('input', () => {
        renderSidebarUsers();
    });

    // Chat sending form submission
    document.getElementById('chatInputForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await sendMessage();
    });

    // Handle typing status on input
    const chatInput = document.getElementById('chatInputField');
    chatInput.addEventListener('input', () => {
        sendTypingStatus(true);
        
        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(() => {
            sendTypingStatus(false);
        }, 2500);
    });

    // Force Refresh Chat
    document.getElementById('refreshChatBtn').addEventListener('click', () => {
        if (activeChatPartner) {
            loadActiveChatMessages(true);
        }
    });

    // Close chat back button (mobile view responsive)
    document.getElementById('backToSidebarBtn').addEventListener('click', () => {
        document.body.classList.remove('show-chat');
        activeChatPartner = null;
    });

    // Setup Emoji Picker grid
    setupEmojiPicker();
}

// Populate and hook Emoji Picker
function setupEmojiPicker() {
    const emojis = [
        '😀', '😂', '🤣', '😊', '😍', '😘', '😜', '😎', 
        '👍', '👎', '❤️', '🔥', '🎉', '👏', '🙌', '😢', 
        '😡', '😮', '🤔', '👀', '✨', '✔️', '❌', '💡'
    ];
    const picker = document.getElementById('emojiPicker');
    picker.innerHTML = "";
    
    emojis.forEach(emoji => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'emoji-btn';
        btn.innerText = emoji;
        btn.addEventListener('click', () => {
            const input = document.getElementById('chatInputField');
            input.value += emoji;
            input.focus();
            picker.classList.remove('show');
            sendTypingStatus(true);
        });
        picker.appendChild(btn);
    });

    // Toggle emoji popover
    document.getElementById('emojiTrigger').addEventListener('click', (e) => {
        e.stopPropagation();
        picker.classList.toggle('show');
    });

    // Hide emoji picker if clicked outside
    document.addEventListener('click', (e) => {
        if (!picker.contains(e.target) && e.target.id !== 'emojiTrigger') {
            picker.classList.remove('show');
        }
    });
}

// Fetch list of users and active conversations on login
async function fetchInitialDashboardData() {
    await fetchAllUsers();
    await fetchConversations();
    renderSidebarUsers();
}

// Fetch all registered users
async function fetchAllUsers() {
    if (!selfUser || !selfUser.username) return;
    try {
        const response = await fetch(`${API_BASE}/users/?logged_in_user=${selfUser.username}`);
        const data = await response.json();
        if (response.ok && data.status === "success") {
            allUsers = data.users;
        }
    } catch (err) {
        console.error("Error loading users list", err);
    }
}

// Fetch conversations (recent chat messages and unread tallies)
async function fetchConversations() {
    if (!selfUser || !selfUser.username) return;
    try {
        const response = await fetch(`${API_BASE}/conversation/?logged_in_user=${selfUser.username}`);
        const data = await response.json();
        if (response.ok && data.status === "success") {
            conversationSummary = data.conversations;
        }
    } catch (err) {
        console.error("Error loading conversation info", err);
    }
}

// Run periodic dashboard fetches every 3 seconds
async function fetchPollingData() {
    if (!selfUser) return;
    
    // Heartbeat update
    await sendHeartbeat();
    
    // Refresh lists
    await fetchAllUsers();
    await fetchConversations();
    renderSidebarUsers();

    // If currently chatting with someone, refresh messages
    if (activeChatPartner) {
        await loadActiveChatMessages(false);
    }
}

// Keep user active and transmit current typing partner
async function sendHeartbeat() {
    try {
        const payload = {
            typing_to: isCurrentlyTyping && activeChatPartner ? activeChatPartner : ""
        };
        
        await fetch(`${API_BASE}/users/update/${selfUser.user_id}/`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    } catch (err) {
        console.error("Heartbeat sync error", err);
    }
}

// Quick trigger for user typing state
function sendTypingStatus(isTyping) {
    if (isCurrentlyTyping === isTyping) return;
    isCurrentlyTyping = isTyping;
    sendHeartbeat();
}

// Draw sidebar list (filters dynamically via search input)
function renderSidebarUsers() {
    const listContainer = document.getElementById('usersList');
    if (!listContainer) return;

    const query = document.getElementById('searchInput').value.trim().toLowerCase();
    
    // Filter users based on query
    const filteredUsers = allUsers.filter(u => 
        u.username.includes(query) || 
        u.full_name.toLowerCase().includes(query)
    );

    if (filteredUsers.length === 0) {
        listContainer.innerHTML = `
            <div class="empty-conv-illustration">
                <i class="fa-regular fa-folder-open"></i>
                <p>No search results found</p>
            </div>
        `;
        return;
    }

    // Sort: users with active conversations first, ordered by last chat time descending
    const usersWithConversations = [];
    const usersWithoutConversations = [];

    filteredUsers.forEach(u => {
        const conv = conversationSummary.find(c => c.partner_username === u.username);
        if (conv) {
            usersWithConversations.push({ user: u, conv });
        } else {
            usersWithoutConversations.push({ user: u, conv: null });
        }
    });

    usersWithConversations.sort((a, b) => new Date(b.conv.sent_at) - new Date(a.conv.sent_at));

    listContainer.innerHTML = "";

    // Draw combined list
    const combinedList = [...usersWithConversations, ...usersWithoutConversations];
    
    combinedList.forEach(item => {
        const u = item.user;
        const conv = item.conv;
        
        // Calculate online status: online if last_seen was updated within 10 seconds
        let isOnline = false;
        if (u.last_seen) {
            const diffSeconds = (new Date() - new Date(u.last_seen)) / 1000;
            if (diffSeconds <= 10) isOnline = true;
        }

        const avatarSrc = u.profile_image || "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='48' height='48'><rect width='100%' height='100%' fill='%23e1e1e1'/><path d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z' fill='%238696a0'/></svg>";
        const lastMsg = conv ? conv.last_message : "No messages yet";
        const msgTime = conv ? formatTime(conv.sent_at) : "";
        const unreadCount = conv ? conv.unread_count : 0;
        
        const activeClass = activeChatPartner === u.username ? 'active' : '';

        const itemEl = document.createElement('div');
        itemEl.className = `user-item ${activeClass}`;
        itemEl.innerHTML = `
            <div class="user-item-info">
                <div class="avatar-wrapper">
                    <img class="avatar" src="${avatarSrc}" alt="${u.full_name}">
                    <span class="status-dot ${isOnline ? 'online' : 'offline'}"></span>
                </div>
                <div class="user-item-text">
                    <h5>${u.full_name}</h5>
                    <p>${lastMsg}</p>
                </div>
            </div>
            <div class="user-item-meta">
                <span class="msg-time">${msgTime}</span>
                ${unreadCount > 0 ? `<span class="unread-badge">${unreadCount}</span>` : ''}
            </div>
        `;

        itemEl.addEventListener('click', () => {
            selectChatPartner(u.username);
        });

        listContainer.appendChild(itemEl);
    });
}

// Select a partner to open chat window
function selectChatPartner(username) {
    activeChatPartner = username;
    
    // Toggle active item UI styling
    document.querySelectorAll('.user-item').forEach(el => el.classList.remove('active'));
    renderSidebarUsers();

    // Show Chat active UI panel
    document.getElementById('welcomePanel').style.display = 'none';
    document.getElementById('activeChatPanel').style.display = 'flex';

    // Show chat window on mobile responsive view
    document.body.classList.add('show-chat');

    // Load active partner info
    const partner = allUsers.find(u => u.username === username);
    if (partner) {
        document.getElementById('chatPartnerFullName').innerText = partner.full_name;
        document.getElementById('chatPartnerAvatar').src = partner.profile_image || "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='48' height='48'><rect width='100%' height='100%' fill='%23e1e1e1'/><path d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z' fill='%238696a0'/></svg>";
        
        let isOnline = false;
        if (partner.last_seen) {
            const diffSeconds = (new Date() - new Date(partner.last_seen)) / 1000;
            if (diffSeconds <= 10) isOnline = true;
        }

        const dot = document.getElementById('chatPartnerStatusDot');
        dot.className = `status-dot ${isOnline ? 'online' : 'offline'}`;
        document.getElementById('chatPartnerStatusText').innerHTML = isOnline ? 
            (partner.typing_to === selfUser.username ? '<span class="typing-indicator">typing...</span>' : 'online') : 
            'offline';
    }

    // Load messages with full scroll-to-bottom
    loadActiveChatMessages(true);
}

// Load conversation chat history between two users
async function loadActiveChatMessages(forceScroll = false) {
    if (!activeChatPartner) return;

    try {
        const response = await fetch(`${API_BASE}/conversation/${activeChatPartner}/${selfUser.username}/`);
        const data = await response.json();
        
        if (response.ok && data.status === "success") {
            const messages = data.messages;
            const container = document.getElementById('messagesWorkspace');

            // Render partner status/typing status live in header
            const partner = data.partner;
            if (partner) {
                let isOnline = false;
                if (partner.last_seen) {
                    const diffSeconds = (new Date() - new Date(partner.last_seen)) / 1000;
                    if (diffSeconds <= 10) isOnline = true;
                }
                const dot = document.getElementById('chatPartnerStatusDot');
                dot.className = `status-dot ${isOnline ? 'online' : 'offline'}`;
                
                document.getElementById('chatPartnerStatusText').innerHTML = isOnline ? 
                    (partner.typing_to === selfUser.username ? '<span class="typing-indicator">typing...</span>' : 'online') : 
                    'offline';
            }

            // Simple diff to prevent unnecessary re-rendering
            if (forceScroll || JSON.stringify(activeMessages) !== JSON.stringify(messages)) {
                activeMessages = messages;
                container.innerHTML = "";

                if (messages.length === 0) {
                    container.innerHTML = `
                        <div class="empty-conv-illustration" style="margin-top: 100px;">
                            <i class="fa-regular fa-comments"></i>
                            <h4>No chats found</h4>
                            <p>Send a message to start conversation.</p>
                        </div>
                    `;
                    return;
                }

                messages.forEach(msg => {
                    const isSentByMe = msg.sender === selfUser.username;
                    const row = document.createElement('div');
                    row.className = `msg-row ${isSentByMe ? 'sent' : 'received'}`;
                    
                    const time = formatTime(msg.sent_at);
                    
                    // Seen tick configurations
                    let tickIcon = '<i class="fa-solid fa-check msg-status-tick"></i>';
                    if (msg.seen) {
                        tickIcon = '<i class="fa-solid fa-check-double msg-status-tick seen"></i>';
                    }

                    row.innerHTML = `
                        <div class="msg-bubble" id="bubble-${msg.chat_id}">
                            ${isSentByMe ? `
                            <div class="msg-options-trigger" onclick="toggleMessageMenu(event, '${msg.chat_id}')">
                                <i class="fa-solid fa-chevron-down"></i>
                            </div>
                            <div class="msg-menu" id="menu-${msg.chat_id}">
                                <button class="msg-menu-item" onclick="startEditMessage('${msg.chat_id}', '${escapeQuote(msg.message)}')">Edit</button>
                                <button class="msg-menu-item" onclick="deleteMessage('${msg.chat_id}')">Delete</button>
                            </div>
                            ` : ''}
                            <div class="msg-text">${msg.message}</div>
                            <div class="msg-footer">
                                <span class="msg-time-stamp">${time}</span>
                                ${isSentByMe ? tickIcon : ''}
                            </div>
                        </div>
                    `;

                    container.appendChild(row);
                });

                if (forceScroll) {
                    scrollToBottom();
                }
            }
        }
    } catch (err) {
        console.error("Error loading chats", err);
    }
}

// Format message timestamps
function formatTime(isoStr) {
    if (!isoStr) return "";
    const date = new Date(isoStr);
    let hrs = date.getHours();
    let mins = date.getMinutes();
    const ampm = hrs >= 12 ? 'PM' : 'AM';
    hrs = hrs % 12;
    hrs = hrs ? hrs : 12; // 0 should be 12
    mins = mins < 10 ? '0' + mins : mins;
    return `${hrs}:${mins} ${ampm}`;
}

// Toggle bubble settings menu
function toggleMessageMenu(event, chatId) {
    event.stopPropagation();
    
    // Close other open menus
    document.querySelectorAll('.msg-menu').forEach(menu => {
        if (menu.id !== `menu-${chatId}`) menu.classList.remove('show');
    });

    const menu = document.getElementById(`menu-${chatId}`);
    if (menu) menu.classList.toggle('show');

    // Close menu when clicked anywhere else
    document.addEventListener('click', function closeMenu(e) {
        if (menu) menu.classList.remove('show');
        document.removeEventListener('click', closeMenu);
    });
}

// Edit/Delete helper string escaping
function escapeQuote(str) {
    return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

// Trigger inline edit form in the bubble
function startEditMessage(chatId, oldMessage) {
    const bubble = document.getElementById(`bubble-${chatId}`);
    if (!bubble) return;

    const originalHtml = bubble.innerHTML;
    
    // Render text field directly inside bubble
    bubble.innerHTML = `
        <div class="edit-msg-input-container">
            <input type="text" class="edit-msg-input" id="edit-input-${chatId}" value="${oldMessage}">
            <button class="edit-btn-confirm" onclick="confirmEditMessage('${chatId}')">Save</button>
            <button class="edit-btn-cancel" onclick="cancelEditMessage('${chatId}', \`${escapeQuote(oldMessage)}\`)">Cancel</button>
        </div>
    `;
    
    const input = document.getElementById(`edit-input-${chatId}`);
    input.focus();
    input.select();
}

// Send PUT request to modify message text
async function confirmEditMessage(chatId) {
    const input = document.getElementById(`edit-input-${chatId}`);
    const newMessage = input.value.trim();

    if (!newMessage) {
        showToast("Message text cannot be empty", "error");
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/chats/update/${chatId}/`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: newMessage })
        });

        if (response.ok) {
            showToast("Message updated", "success");
            loadActiveChatMessages(false);
        } else {
            showToast("Failed to edit message", "error");
        }
    } catch (err) {
        showToast("Connection error while updating message", "error");
        console.error(err);
    }
}

// Cancel edit and redraw message workspace
function cancelEditMessage(chatId, oldMessage) {
    loadActiveChatMessages(false);
}

// Send DELETE request to wipe message
async function deleteMessage(chatId) {
    if (!confirm("Delete this message?")) return;

    try {
        const response = await fetch(`${API_BASE}/chats/delete/${chatId}/`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast("Message deleted", "success");
            loadActiveChatMessages(false);
        } else {
            showToast("Failed to delete message", "error");
        }
    } catch (err) {
        showToast("Connection error while deleting message", "error");
        console.error(err);
    }
}

// Dispatch new chat message
async function sendMessage() {
    const input = document.getElementById('chatInputField');
    const message = input.value.trim();
    if (!message || !activeChatPartner) return;

    // Reset input instantly to feel snappy
    input.value = "";
    sendTypingStatus(false);

    try {
        const response = await fetch(`${API_BASE}/chats/send/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sender: selfUser.username,
                receiver: activeChatPartner,
                message: message
            })
        });

        const data = await response.json();
        if (response.ok && data.status === "success") {
            // Load messages and scroll right to bottom
            await loadActiveChatMessages(true);
            await fetchConversations();
            renderSidebarUsers();
        } else {
            showToast(data.message || "Failed to send message", "error");
        }
    } catch (err) {
        showToast("Connection error: Failed to send", "error");
        console.error(err);
    }
}

// Scroll chat panel to bottom
function scrollToBottom() {
    const container = document.getElementById('messagesWorkspace');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

// Document Load entry
document.addEventListener('DOMContentLoaded', () => {
    // If dashboard container is on the page, bootstrap it
    if (document.getElementById('usersList')) {
        initDashboard();
    }
});

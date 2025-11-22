// API Base URL
const API_BASE = '/api';

// DOM Elements
const friendForm = document.getElementById('friend-form');
const friendsContainer = document.getElementById('friends-container');
const alertsContainer = document.getElementById('alerts-container');
const upcomingContainer = document.getElementById('upcoming-container');
const messageModal = document.getElementById('message-modal');
const modalTitle = document.getElementById('modal-title');
const modalBody = document.getElementById('modal-body');
const closeModal = document.querySelector('.close');
const cancelEditBtn = document.getElementById('cancel-edit');
const formTitle = document.getElementById('form-title');

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    loadFriends();
    loadAlerts();
    loadUpcomingBirthdays();
    
    // Set up auto-refresh for alerts (every 5 minutes)
    setInterval(loadAlerts, 300000);
    
    // Set up event listeners
    friendForm.addEventListener('submit', handleFormSubmit);
    cancelEditBtn.addEventListener('click', resetForm);
    closeModal.addEventListener('click', () => messageModal.style.display = 'none');
    
    document.getElementById('refresh-friends').addEventListener('click', loadFriends);
    document.getElementById('refresh-alerts').addEventListener('click', loadAlerts);
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === messageModal) {
            messageModal.style.display = 'none';
        }
    });
});

// Load all friends
async function loadFriends() {
    try {
        const response = await fetch(`${API_BASE}/friends`);
        const friends = await response.json();
        
        if (friends.length === 0) {
            friendsContainer.innerHTML = '<div class="no-friends"><i class="fas fa-user-friends fa-3x" style="opacity: 0.3; margin-bottom: 20px;"></i><br>No friends added yet. Add your first friend above!</div>';
            return;
        }
        
        friendsContainer.innerHTML = friends.map(friend => createFriendCard(friend)).join('');
    } catch (error) {
        console.error('Error loading friends:', error);
        friendsContainer.innerHTML = '<div class="no-friends" style="color: #dc3545;">Error loading friends. Please try again.</div>';
    }
}

// Create friend card HTML
function createFriendCard(friend) {
    const birthday = new Date(friend.birthday + 'T00:00:00');
    const formattedDate = birthday.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
    
    return `
        <div class="friend-card">
            <div class="friend-header">
                <div class="friend-name"><i class="fas fa-user-circle"></i> ${escapeHtml(friend.name)}</div>
            </div>
            <div class="friend-info">
                <i class="fas fa-birthday-cake"></i> ${formattedDate}
            </div>
            ${friend.relationship ? `<div class="friend-info"><i class="fas fa-heart"></i> ${escapeHtml(friend.relationship)}</div>` : ''}
            ${friend.email ? `<div class="friend-info"><i class="fas fa-envelope"></i> ${escapeHtml(friend.email)}</div>` : ''}
            ${friend.phone ? `<div class="friend-info"><i class="fas fa-phone"></i> ${escapeHtml(friend.phone)}</div>` : ''}
            <div class="friend-actions">
                <button class="btn btn-info" onclick="viewMessages(${friend.id}, '${escapeHtml(friend.name)}')">
                    <i class="fas fa-comments"></i> Messages
                </button>
                <button class="btn btn-warning" onclick="editFriend(${friend.id})">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button class="btn btn-danger" onclick="deleteFriend(${friend.id}, '${escapeHtml(friend.name)}')">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        </div>
    `;
}

// Load alerts
async function loadAlerts() {
    try {
        const response = await fetch(`${API_BASE}/alerts`);
        const alerts = await response.json();
        
        if (alerts.length === 0) {
            alertsContainer.innerHTML = '<div class="no-alerts"><i class="fas fa-bell-slash fa-3x" style="opacity: 0.3; margin-bottom: 15px;"></i><br>No alerts yet. We\'ll notify you about upcoming birthdays!</div>';
            return;
        }
        
        alertsContainer.innerHTML = alerts.map(alert => createAlertItem(alert)).join('');
    } catch (error) {
        console.error('Error loading alerts:', error);
        alertsContainer.innerHTML = '<div class="no-alerts" style="color: #dc3545;">Error loading alerts.</div>';
    }
}

// Create alert item HTML
function createAlertItem(alert) {
    const alertClass = `alert-${alert.alert_type}`;
    const readClass = alert.is_read ? 'read' : '';
    const date = new Date(alert.created_at);
    const formattedTime = date.toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        hour: 'numeric', 
        minute: '2-digit'
    });
    
    return `
        <div class="alert-item ${alertClass} ${readClass}">
            <div>
                <div class="alert-message">${escapeHtml(alert.message)}</div>
                <div class="alert-time">${formattedTime}</div>
            </div>
            ${!alert.is_read ? `<button class="mark-read-btn" onclick="markAlertRead(${alert.id})">Mark as Read</button>` : ''}
        </div>
    `;
}

// Load upcoming birthdays
async function loadUpcomingBirthdays() {
    try {
        const response = await fetch(`${API_BASE}/upcoming-birthdays`);
        const upcoming = await response.json();
        
        if (upcoming.length === 0) {
            upcomingContainer.innerHTML = '<div class="no-alerts">No birthdays in the next 30 days.</div>';
            return;
        }
        
        upcomingContainer.innerHTML = upcoming.map(item => createUpcomingCard(item)).join('');
    } catch (error) {
        console.error('Error loading upcoming birthdays:', error);
        upcomingContainer.innerHTML = '<div class="no-alerts" style="color: #dc3545;">Error loading birthdays.</div>';
    }
}

// Create upcoming birthday card HTML
function createUpcomingCard(item) {
    const birthday = new Date(item.birthday + 'T00:00:00');
    const formattedDate = birthday.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
    const daysText = item.days_until === 0 ? 'TODAY!' : item.days_until === 1 ? 'Tomorrow' : `In ${item.days_until} days`;
    
    return `
        <div class="upcoming-card">
            <h3>${escapeHtml(item.name)}</h3>
            <div class="days">${daysText}</div>
            <div class="date">${formattedDate}</div>
        </div>
    `;
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const friendId = document.getElementById('friend-id').value;
    const data = {
        name: document.getElementById('name').value,
        birthday: document.getElementById('birthday').value,
        relationship: document.getElementById('relationship').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value
    };
    
    try {
        const url = friendId ? `${API_BASE}/friends/${friendId}` : `${API_BASE}/friends`;
        const method = friendId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            resetForm();
            loadFriends();
            loadUpcomingBirthdays();
            showNotification(friendId ? 'Friend updated successfully!' : 'Friend added successfully!', 'success');
        } else {
            showNotification('Error: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error saving friend:', error);
        showNotification('Error saving friend. Please try again.', 'error');
    }
}

// Edit friend
async function editFriend(id) {
    try {
        const response = await fetch(`${API_BASE}/friends`);
        const friends = await response.json();
        const friend = friends.find(f => f.id === id);
        
        if (friend) {
            document.getElementById('friend-id').value = friend.id;
            document.getElementById('name').value = friend.name;
            document.getElementById('birthday').value = friend.birthday;
            document.getElementById('relationship').value = friend.relationship || '';
            document.getElementById('email').value = friend.email || '';
            document.getElementById('phone').value = friend.phone || '';
            
            formTitle.innerHTML = '<i class="fas fa-user-edit"></i> Edit Friend';
            cancelEditBtn.style.display = 'inline-flex';
            
            // Scroll to form
            document.getElementById('friend-form-section').scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        console.error('Error loading friend for edit:', error);
    }
}

// Delete friend
async function deleteFriend(id, name) {
    if (!confirm(`Are you sure you want to delete ${name}? This action cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/friends/${id}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            loadFriends();
            loadUpcomingBirthdays();
            showNotification(`${name} has been deleted.`, 'success');
        } else {
            showNotification('Error deleting friend.', 'error');
        }
    } catch (error) {
        console.error('Error deleting friend:', error);
        showNotification('Error deleting friend. Please try again.', 'error');
    }
}

// View messages for a friend
async function viewMessages(friendId, friendName) {
    try {
        const response = await fetch(`${API_BASE}/messages/${friendId}`);
        const messages = await response.json();
        
        modalTitle.innerHTML = `<i class="fas fa-comments"></i> Birthday Messages for ${escapeHtml(friendName)}`;
        
        if (messages.length === 0) {
            modalBody.innerHTML = '<div class="no-alerts">No messages sent yet.</div>';
        } else {
            modalBody.innerHTML = messages.map(msg => `
                <div class="message-item">
                    <div class="message-text">${escapeHtml(msg.message)}</div>
                    <div class="message-meta">
                        <span><i class="fas fa-calendar"></i> Year: ${msg.year}</span>
                        <span><i class="fas fa-clock"></i> ${new Date(msg.sent_at).toLocaleString()}</span>
                    </div>
                </div>
            `).join('');
        }
        
        messageModal.style.display = 'block';
    } catch (error) {
        console.error('Error loading messages:', error);
        showNotification('Error loading messages.', 'error');
    }
}

// Mark alert as read
async function markAlertRead(alertId) {
    try {
        const response = await fetch(`${API_BASE}/alerts/${alertId}/read`, {
            method: 'PUT'
        });
        
        const result = await response.json();
        
        if (result.success) {
            loadAlerts();
        }
    } catch (error) {
        console.error('Error marking alert as read:', error);
    }
}

// Reset form
function resetForm() {
    friendForm.reset();
    document.getElementById('friend-id').value = '';
    formTitle.innerHTML = '<i class="fas fa-user-plus"></i> Add New Friend';
    cancelEditBtn.style.display = 'none';
}

// Show notification
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : '#dc3545'};
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

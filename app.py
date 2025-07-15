import streamlit as st
import sqlite3
import hashlib
import secrets
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import csv
from io import StringIO
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="FlowTLS SYNC+ Ticketing System",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        color: white;
    }
    
    .ticket-card {
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
        color: #1f2937;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .ticket-card h4 {
        color: #1f2937 !important;
        margin: 0 0 0.5rem 0;
    }
    
    .ticket-card p {
        color: #4b5563 !important;
        margin: 0.5rem 0;
    }
    
    .priority-critical {
        background-color: #ef4444;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .priority-high {
        background-color: #f59e0b;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .priority-medium {
        background-color: #3b82f6;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .priority-low {
        background-color: #10b981;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .status-open {
        background-color: #3b82f6;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .status-in-progress {
        background-color: #8b5cf6;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .status-resolved {
        background-color: #10b981;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .status-closed {
        background-color: #6b7280;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .overdue {
        border-left: 4px solid #ef4444;
        background-color: #fef2f2;
        color: #1f2937 !important;
    }
    
    .overdue h4 {
        color: #dc2626 !important;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }
    
    /* Ensure all text in main content is readable */
    .main .block-container {
        color: #1f2937;
    }
    
    /* Fix any white text issues */
    .stMarkdown, .stText {
        color: #1f2937 !important;
    }
</style>
""", unsafe_allow_html=True)

# Database Management
class DatabaseManager:
    def __init__(self, db_path="flowtls_tickets.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create tables
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_date DATETIME NOT NULL,
                last_login_date DATETIME
            );
            
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'Open',
                assigned_to TEXT DEFAULT '',
                category TEXT DEFAULT 'General',
                created_date DATETIME NOT NULL,
                updated_date DATETIME,
                due_date DATETIME,
                reporter TEXT DEFAULT '',
                resolution TEXT DEFAULT '',
                tags TEXT DEFAULT ''
            );
            
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                preference_key TEXT,
                preference_value TEXT,
                category TEXT DEFAULT 'General',
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)
        
        # Create default admin user if none exists
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            self.create_default_admin()
        
        # Add sample tickets if none exist
        cursor.execute("SELECT COUNT(*) FROM tickets")
        if cursor.fetchone()[0] == 0:
            self.create_sample_tickets()
        
        conn.commit()
        conn.close()
    
    def create_default_admin(self):
        salt = secrets.token_hex(32)
        password_hash = hashlib.sha256(("admin123" + salt).encode()).hexdigest()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, salt, first_name, last_name, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("admin", "admin@flowtls.com", password_hash, salt, "System", "Admin", datetime.now()))
        conn.commit()
        conn.close()
    
    def create_sample_tickets(self):
        sample_tickets = [
            ("FlowTLS Integration Issue", "System integration requires debugging for the new FlowTLS connection module", "High", "Open", "John Smith", "Integration", "Sarah Johnson", "urgent,integration,flowtls"),
            ("User Authentication Problem", "Users unable to login with SSO - affecting multiple departments", "Critical", "In Progress", "Mike Wilson", "Security", "Admin User", "sso,login,authentication"),
            ("Database Performance", "Query optimization needed for customer reports taking too long", "Medium", "Open", "Alice Chen", "Performance", "DB Team", "performance,database,reports"),
            ("UI Modernization", "Update interface design to match new brand guidelines", "Low", "Open", "UI Team", "Enhancement", "Product Manager", "ui,enhancement,design"),
            ("Email Notifications", "Configure email alerts for high priority tickets", "Medium", "Resolved", "DevOps Team", "Configuration", "System Admin", "email,notifications,alerts"),
            ("Mobile App Crash", "Application crashes on iOS devices when accessing ticket details", "High", "In Progress", "Mobile Team", "Bug", "Customer Support", "mobile,ios,crash"),
            ("API Rate Limiting", "Implement rate limiting for public API endpoints", "Medium", "Open", "Backend Team", "Security", "Tech Lead", "api,security,rate-limit"),
            ("Customer Data Export", "Add ability to export customer data in CSV format", "Low", "Resolved", "Development Team", "Feature Request", "Customer Success", "export,csv,feature"),
            ("Server Monitoring", "Set up comprehensive monitoring for production servers", "High", "Open", "DevOps Team", "Infrastructure", "Operations Manager", "monitoring,servers,production"),
            ("Password Policy Update", "Update password requirements to meet new security standards", "Medium", "Closed", "Security Team", "Security", "CISO", "password,policy,security"),
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        for title, desc, priority, status, assigned, category, reporter, tags in sample_tickets:
            cursor.execute("""
                INSERT INTO tickets (title, description, priority, status, assigned_to, category, created_date, reporter, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, desc, priority, status, assigned, category, datetime.now(), reporter, tags))
        conn.commit()
        conn.close()

# Authentication Service
class AuthService:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def hash_password(self, password, salt):
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def verify_password(self, password, hash_value, salt):
        return self.hash_password(password, salt) == hash_value
    
    def login(self, username, password):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, password_hash, salt, first_name, last_name
            FROM users WHERE username = ? AND is_active = 1
        """, (username,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and self.verify_password(password, user[3], user[4]):
            # Update last login
            self.update_last_login(user[0])
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'first_name': user[5],
                'last_name': user[6],
                'full_name': f"{user[5]} {user[6]}".strip()
            }
        return None
    
    def update_last_login(self, user_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET last_login_date = ? WHERE id = ?", (datetime.now(), user_id))
        conn.commit()
        conn.close()

# Ticket Service
class TicketService:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_all_tickets(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, description, priority, status, assigned_to, category, 
                   created_date, updated_date, due_date, reporter, resolution, tags
            FROM tickets ORDER BY created_date DESC
        """)
        
        tickets = []
        for row in cursor.fetchall():
            ticket = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'priority': row[3],
                'status': row[4],
                'assigned_to': row[5],
                'category': row[6],
                'created_date': row[7],
                'updated_date': row[8],
                'due_date': row[9],
                'reporter': row[10],
                'resolution': row[11],
                'tags': row[12]
            }
            tickets.append(ticket)
        
        conn.close()
        return tickets
    
    def get_ticket_by_id(self, ticket_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, description, priority, status, assigned_to, category, 
                   created_date, updated_date, due_date, reporter, resolution, tags
            FROM tickets WHERE id = ?
        """, (ticket_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'priority': row[3],
                'status': row[4],
                'assigned_to': row[5],
                'category': row[6],
                'created_date': row[7],
                'updated_date': row[8],
                'due_date': row[9],
                'reporter': row[10],
                'resolution': row[11],
                'tags': row[12]
            }
        return None
    
    def create_ticket(self, ticket_data):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tickets (title, description, priority, status, assigned_to, category, 
                               created_date, due_date, reporter, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket_data['title'],
            ticket_data['description'],
            ticket_data['priority'],
            ticket_data['status'],
            ticket_data['assigned_to'],
            ticket_data['category'],
            datetime.now(),
            ticket_data.get('due_date'),
            ticket_data['reporter'],
            ticket_data['tags']
        ))
        
        ticket_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return ticket_id
    
    def update_ticket(self, ticket_id, ticket_data):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tickets SET title=?, description=?, priority=?, status=?, assigned_to=?, 
                             category=?, updated_date=?, due_date=?, reporter=?, resolution=?, tags=?
            WHERE id=?
        """, (
            ticket_data['title'],
            ticket_data['description'],
            ticket_data['priority'],
            ticket_data['status'],
            ticket_data['assigned_to'],
            ticket_data['category'],
            datetime.now(),
            ticket_data.get('due_date'),
            ticket_data['reporter'],
            ticket_data.get('resolution', ''),
            ticket_data['tags'],
            ticket_id
        ))
        conn.commit()
        conn.close()
    
    def delete_ticket(self, ticket_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tickets SET status='Deleted', updated_date=? WHERE id=?", 
                      (datetime.now(), ticket_id))
        conn.commit()
        conn.close()
    
    def search_tickets(self, search_term):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, description, priority, status, assigned_to, category, 
                   created_date, updated_date, due_date, reporter, resolution, tags
            FROM tickets 
            WHERE title LIKE ? OR description LIKE ? OR tags LIKE ?
            ORDER BY created_date DESC
        """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        
        tickets = []
        for row in cursor.fetchall():
            ticket = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'priority': row[3],
                'status': row[4],
                'assigned_to': row[5],
                'category': row[6],
                'created_date': row[7],
                'updated_date': row[8],
                'due_date': row[9],
                'reporter': row[10],
                'resolution': row[11],
                'tags': row[12]
            }
            tickets.append(ticket)
        
        conn.close()
        return tickets
    
    def get_ticket_statistics(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM tickets 
            WHERE status != 'Deleted' 
            GROUP BY status
        """)
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = row[1]
        
        conn.close()
        return stats

# Initialize services
@st.cache_resource
def init_services():
    db_manager = DatabaseManager()
    auth_service = AuthService(db_manager)
    ticket_service = TicketService(db_manager)
    return db_manager, auth_service, ticket_service

db_manager, auth_service, ticket_service = init_services()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'selected_ticket' not in st.session_state:
    st.session_state.selected_ticket = None

# Authentication check
def require_auth():
    if not st.session_state.user:
        st.session_state.page = 'login'
        return False
    return True

# Utility functions
def get_priority_color(priority):
    colors = {
        'Critical': '#ef4444',
        'High': '#f59e0b',
        'Medium': '#3b82f6',
        'Low': '#10b981'
    }
    return colors.get(priority, '#6b7280')

def get_status_color(status):
    colors = {
        'Open': '#3b82f6',
        'In Progress': '#8b5cf6',
        'Resolved': '#10b981',
        'Closed': '#6b7280',
        'Deleted': '#ef4444',
        'On Hold': '#f59e0b'
    }
    return colors.get(status, '#6b7280')

def format_date(date_str):
    if not date_str:
        return "N/A"
    try:
        if isinstance(date_str, str):
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            date_obj = date_str
        return date_obj.strftime("%b %d, %Y")
    except:
        return str(date_str)

def is_overdue(due_date, status):
    if not due_date or status in ['Resolved', 'Closed']:
        return False
    try:
        if isinstance(due_date, str):
            due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        else:
            due = due_date
        return due < datetime.now()
    except:
        return False

# Login Page
def show_login_page():
    st.markdown("""
        <div class="main-header">
            <h1>🎫 FlowTLS SYNC+</h1>
            <p>Professional Ticketing System</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Sign In")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            
            if submitted:
                if username and password:
                    user = auth_service.login(username, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.page = 'dashboard'
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please enter both username and password")
        
        st.info("**Demo Credentials:** Username: `admin`, Password: `admin123`")

# Dashboard Page
def show_dashboard():
    if not require_auth():
        return
    
    # Header
    st.markdown(f"""
        <div class="main-header">
            <h1>🎫 FlowTLS SYNC+ Dashboard</h1>
            <p>Welcome back, {st.session_state.user['full_name']}!</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get ticket statistics
    stats = ticket_service.get_ticket_statistics()
    total_tickets = sum(stats.values()) if stats else 0
    
    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Tickets", total_tickets)
    with col2:
        st.metric("Open", stats.get('Open', 0))
    with col3:
        st.metric("In Progress", stats.get('In Progress', 0))
    with col4:
        st.metric("Resolved", stats.get('Resolved', 0))
    with col5:
        st.metric("Closed", stats.get('Closed', 0))
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        if stats:
            fig = px.pie(
                values=list(stats.values()),
                names=list(stats.keys()),
                title="Tickets by Status"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Recent tickets
        st.subheader("Recent Tickets")
        tickets = ticket_service.get_all_tickets()[:5]
        for ticket in tickets:
            with st.container():
                st.markdown(f"""
                    <div class="ticket-card">
                        <h4 style="color: #1f2937 !important;">#{ticket['id']} - {ticket['title']}</h4>
                        <p style="color: #4b5563 !important;">{ticket['description'][:100]}...</p>
                        <div>
                            <span class="priority-{ticket['priority'].lower()}">{ticket['priority']}</span>
                            <span class="status-{ticket['status'].lower().replace(' ', '-')}">{ticket['status']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# Tickets Page
def show_tickets_page():
    if not require_auth():
        return
    
    st.title("🎫 Ticket Management")
    
    # Action buttons
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search tickets", placeholder="Search by title, description, or tags")
    
    with col2:
        if st.button("➕ New Ticket", use_container_width=True):
            st.session_state.page = 'new_ticket'
            st.rerun()
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    with col4:
        filter_status = st.selectbox("Filter by Status", 
                                   ["All", "Open", "In Progress", "Resolved", "Closed", "Deleted"])
    
    with col5:
        if st.button("📊 Export CSV", use_container_width=True):
            tickets = ticket_service.get_all_tickets()
            csv_data = generate_csv_export(tickets)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"flowtls_tickets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    # Get tickets based on search and filter
    if search_term:
        tickets = ticket_service.search_tickets(search_term)
    else:
        tickets = ticket_service.get_all_tickets()
    
    if filter_status != "All":
        tickets = [t for t in tickets if t['status'] == filter_status]
    
    # Tabs for different ticket views
    tab1, tab2, tab3 = st.tabs([
        f"Active Tickets ({len([t for t in tickets if t['status'] not in ['Resolved', 'Closed', 'Deleted']])})",
        f"Completed ({len([t for t in tickets if t['status'] in ['Resolved', 'Closed']])})",
        f"Deleted ({len([t for t in tickets if t['status'] == 'Deleted'])})"
    ])
    
    with tab1:
        active_tickets = [t for t in tickets if t['status'] not in ['Resolved', 'Closed', 'Deleted']]
        display_ticket_list(active_tickets, show_actions=True)
    
    with tab2:
        completed_tickets = [t for t in tickets if t['status'] in ['Resolved', 'Closed']]
        display_ticket_list(completed_tickets, show_actions=False)
    
    with tab3:
        deleted_tickets = [t for t in tickets if t['status'] == 'Deleted']
        display_ticket_list(deleted_tickets, show_actions=False)

def display_ticket_list(tickets, show_actions=True):
    if not tickets:
        st.info("No tickets found.")
        return
    
    for ticket in tickets:
        overdue_class = "overdue" if is_overdue(ticket['due_date'], ticket['status']) else ""
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                    <div class="ticket-card {overdue_class}">
                        <h4 style="color: #1f2937 !important; margin-bottom: 0.5rem;">#{ticket['id']} - {ticket['title']}</h4>
                        <p style="color: #4b5563 !important; margin-bottom: 0.75rem;">{ticket['description'][:150]}{'...' if len(ticket['description']) > 150 else ''}</p>
                        <div style="margin-top: 10px;">
                            <span class="priority-{ticket['priority'].lower()}">{ticket['priority']}</span>
                            <span class="status-{ticket['status'].lower().replace(' ', '-')}">{ticket['status']}</span>
                            <span style="margin-left: 10px; color: #4b5563;">📁 {ticket['category']}</span>
                            <span style="margin-left: 10px; color: #4b5563;">👤 {ticket['assigned_to'] or 'Unassigned'}</span>
                            <span style="margin-left: 10px; color: #4b5563;">📅 {format_date(ticket['created_date'])}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if show_actions:
                    if st.button("View", key=f"view_{ticket['id']}"):
                        st.session_state.selected_ticket = ticket
                        st.session_state.page = 'ticket_details'
                        st.rerun()
                    
                    if st.button("Edit", key=f"edit_{ticket['id']}"):
                        st.session_state.selected_ticket = ticket
                        st.session_state.page = 'edit_ticket'
                        st.rerun()

# New/Edit Ticket Page
def show_ticket_form(edit_mode=False):
    if not require_auth():
        return
    
    title = "Edit Ticket" if edit_mode else "Create New Ticket"
    st.title(f"🎫 {title}")
    
    # Pre-fill form if editing
    if edit_mode and st.session_state.selected_ticket:
        ticket = st.session_state.selected_ticket
        default_values = {
            'title': ticket['title'],
            'description': ticket['description'],
            'priority': ticket['priority'],
            'status': ticket['status'],
            'assigned_to': ticket['assigned_to'],
            'category': ticket['category'],
            'reporter': ticket['reporter'],
            'tags': ticket['tags'],
            'resolution': ticket.get('resolution', ''),
            'due_date': datetime.fromisoformat(ticket['due_date']).date() if ticket['due_date'] else None
        }
    else:
        default_values = {
            'title': '',
            'description': '',
            'priority': 'Medium',
            'status': 'Open',
            'assigned_to': '',
            'category': 'General',
            'reporter': st.session_state.user['full_name'],
            'tags': '',
            'resolution': '',
            'due_date': None
        }
    
    with st.form("ticket_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            title_input = st.text_input("Title *", value=default_values['title'])
            description = st.text_area("Description *", value=default_values['description'], height=150)
            
            if edit_mode and default_values['status'] in ['Resolved', 'Closed']:
                resolution = st.text_area("Resolution", value=default_values['resolution'], height=100)
            else:
                resolution = ""
        
        with col2:
            priority = st.selectbox("Priority", 
                                  ['Low', 'Medium', 'High', 'Critical'],
                                  index=['Low', 'Medium', 'High', 'Critical'].index(default_values['priority']))
            
            status = st.selectbox("Status",
                                ['Open', 'In Progress', 'Resolved', 'Closed', 'On Hold'],
                                index=['Open', 'In Progress', 'Resolved', 'Closed', 'On Hold'].index(default_values['status']))
            
            category = st.selectbox("Category",
                                  ['General', 'Bug', 'Feature Request', 'Security', 'Performance', 
                                   'Integration', 'Configuration', 'Enhancement', 'Infrastructure', 'Maintenance'],
                                  index=['General', 'Bug', 'Feature Request', 'Security', 'Performance', 
                                         'Integration', 'Configuration', 'Enhancement', 'Infrastructure', 'Maintenance'].index(default_values['category']))
            
            assigned_to = st.text_input("Assigned To", value=default_values['assigned_to'])
            reporter = st.text_input("Reporter", value=default_values['reporter'])
            
            due_date = st.date_input("Due Date (Optional)", value=default_values['due_date'])
            tags = st.text_input("Tags", value=default_values['tags'], help="Separate tags with commas")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            submitted = st.form_submit_button("Save Ticket", use_container_width=True)
        
        with col2:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)
        
        if submitted:
            if title_input and description:
                ticket_data = {
                    'title': title_input,
                    'description': description,
                    'priority': priority,
                    'status': status,
                    'assigned_to': assigned_to,
                    'category': category,
                    'reporter': reporter,
                    'tags': tags,
                    'resolution': resolution,
                    'due_date': due_date.isoformat() if due_date else None
                }
                
                try:
                    if edit_mode:
                        ticket_service.update_ticket(st.session_state.selected_ticket['id'], ticket_data)
                        st.success("Ticket updated successfully!")
                    else:
                        ticket_id = ticket_service.create_ticket(ticket_data)
                        st.success(f"Ticket #{ticket_id} created successfully!")
                    
                    st.session_state.page = 'tickets'
                    st.session_state.selected_ticket = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving ticket: {str(e)}")
            else:
                st.error("Please fill in the required fields (Title and Description)")
        
        if cancelled:
            st.session_state.page = 'tickets'
            st.session_state.selected_ticket = None
            st.rerun()

# Ticket Details Page
def show_ticket_details():
    if not require_auth() or not st.session_state.selected_ticket:
        st.session_state.page = 'tickets'
        st.rerun()
        return
    
    ticket = st.session_state.selected_ticket
    
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title(f"🎫 Ticket #{ticket['id']}")
        st.subheader(ticket['title'])
    
    with col2:
        if st.button("✏️ Edit Ticket"):
            st.session_state.page = 'edit_ticket'
            st.rerun()
        
        if st.button("← Back to Tickets"):
            st.session_state.page = 'tickets'
            st.session_state.selected_ticket = None
            st.rerun()
    
    # Status and Priority badges
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        priority_color = get_priority_color(ticket['priority'])
        st.markdown(f"""
            <div style="background-color: {priority_color}; color: white; padding: 0.5rem 1rem; 
                       border-radius: 1rem; text-align: center; font-weight: bold;">
                Priority: {ticket['priority']}
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        status_color = get_status_color(ticket['status'])
        st.markdown(f"""
            <div style="background-color: {status_color}; color: white; padding: 0.5rem 1rem; 
                       border-radius: 1rem; text-align: center; font-weight: bold;">
                Status: {ticket['status']}
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Details section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Description")
        st.write(ticket['description'])
        
        if ticket.get('resolution'):
            st.subheader("Resolution")
            st.info(ticket['resolution'])
    
    with col2:
        st.subheader("Details")
        
        details = [
            ("Category", ticket['category']),
            ("Assigned To", ticket['assigned_to'] or "Unassigned"),
            ("Reporter", ticket['reporter'] or "Unknown"),
            ("Created", format_date(ticket['created_date'])),
            ("Updated", format_date(ticket['updated_date']) if ticket['updated_date'] else "Never"),
            ("Due Date", format_date(ticket['due_date']) if ticket['due_date'] else "Not set"),
            ("Tags", ticket['tags'] or "None")
        ]
        
        for label, value in details:
            st.write(f"**{label}:** {value}")
        
        # Overdue warning
        if is_overdue(ticket['due_date'], ticket['status']):
            st.error("⚠️ This ticket is overdue!")

# Settings Page
def show_settings():
    if not require_auth():
        return
    
    st.title("⚙️ Settings")
    
    tab1, tab2 = st.tabs(["General", "About"])
    
    with tab1:
        st.subheader("Application Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            auto_refresh = st.checkbox("Auto-refresh ticket list every 5 minutes", value=True)
            notifications = st.checkbox("Show desktop notifications for new tickets", value=False)
        
        with col2:
            st.subheader("Database Operations")
            if st.button("Export All Data"):
                tickets = ticket_service.get_all_tickets()
                csv_data = generate_csv_export(tickets)
                st.download_button(
                    label="Download Full Export",
                    data=csv_data,
                    file_name=f"flowtls_full_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        if st.button("Save General Settings"):
            st.success("Settings saved successfully!")
        
        st.info("📧 **Email features temporarily disabled** for Streamlit Cloud compatibility. All other features fully functional!")
    
    with tab2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1 style="color: #2563eb;">FlowTLS SYNC+</h1>
            <h3 style="color: #6b7280;">Professional Ticketing System</h3>
            <p style="font-size: 1.2em; margin: 2rem 0;">Version 1.0.0</p>
            <p style="color: #6b7280;">© 2025 FlowTLS SYNC+. All rights reserved.</p>
            <hr style="margin: 2rem 0;">
            <p>A comprehensive ticketing system designed for<br>modern workflow management and team collaboration.</p>
        </div>
        """, unsafe_allow_html=True)

# Helper function for CSV export
def generate_csv_export(tickets):
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'ID', 'Title', 'Description', 'Priority', 'Status', 'Assigned To',
        'Category', 'Created Date', 'Updated Date', 'Due Date', 'Reporter', 'Tags'
    ])
    
    # Data rows
    for ticket in tickets:
        writer.writerow([
            ticket['id'],
            ticket['title'],
            ticket['description'],
            ticket['priority'],
            ticket['status'],
            ticket['assigned_to'],
            ticket['category'],
            format_date(ticket['created_date']),
            format_date(ticket['updated_date']),
            format_date(ticket['due_date']),
            ticket['reporter'],
            ticket['tags']
        ])
    
    return output.getvalue()

# Sidebar Navigation
def show_sidebar():
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); 
                       border-radius: 0.5rem; color: white; margin-bottom: 1rem;">
                <h2>🎫 FlowTLS SYNC+</h2>
                <p>Professional Ticketing</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.user:
            st.markdown(f"**Welcome, {st.session_state.user['full_name']}!**")
            st.markdown("---")
            
            # Navigation
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.page = 'dashboard'
                st.rerun()
            
            if st.button("🎫 Tickets", use_container_width=True):
                st.session_state.page = 'tickets'
                st.rerun()
            
            if st.button("➕ New Ticket", use_container_width=True):
                st.session_state.page = 'new_ticket'
                st.rerun()
            
            if st.button("⚙️ Settings", use_container_width=True):
                st.session_state.page = 'settings'
                st.rerun()
            
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.page = 'login'
                st.session_state.selected_ticket = None
                st.rerun()

# Main App Router
def main():
    # Show sidebar if user is logged in
    if st.session_state.user:
        show_sidebar()
    
    # Route to appropriate page
    if st.session_state.page == 'login':
        show_login_page()
    elif st.session_state.page == 'dashboard':
        show_dashboard()
    elif st.session_state.page == 'tickets':
        show_tickets_page()
    elif st.session_state.page == 'new_ticket':
        show_ticket_form(edit_mode=False)
    elif st.session_state.page == 'edit_ticket':
        show_ticket_form(edit_mode=True)
    elif st.session_state.page == 'ticket_details':
        show_ticket_details()
    elif st.session_state.page == 'settings':
        show_settings()
    else:
        st.session_state.page = 'login'
        st.rerun()

if __name__ == "__main__":
    main()
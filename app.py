import streamlit as st
import sqlite3
import hashlib
import secrets
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple
import threading
import uuid
import time
import os
# if os.path.exists("flowtls_professional.db"):
    # os.remove("flowtls_professional.db")
    
st.set_page_config(
    page_title="FlowTLS SYNC+ Professional",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%);
        padding: 1.5rem 2rem;
        border-radius: 0.75rem;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
    }
    .priority-critical {
        background: linear-gradient(135deg, #dc2626, #b91c1c);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .priority-high {
        background: linear-gradient(135deg, #ea580c, #c2410c);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .priority-medium {
        background: linear-gradient(135deg, #ca8a04, #a16207);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .priority-low {
        background: linear-gradient(135deg, #059669, #047857);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .status-open {
        background: linear-gradient(135deg, #dc2626, #b91c1c);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .status-in-progress {
        background: linear-gradient(135deg, #ca8a04, #a16207);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .status-resolved {
        background: linear-gradient(135deg, #059669, #047857);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .status-closed {
        background: linear-gradient(135deg, #6b7280, #4b5563);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e5e7eb;
        border-radius: 0.75rem;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
        margin: 0.5rem 0;
    }
    .metric-label {
        color: #6b7280;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .user-role-admin {
        background: linear-gradient(135deg, #7c2d12, #ea580c);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .user-role-manager {
        background: linear-gradient(135deg, #1d4ed8, #2563eb);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .user-role-agent {
        background: linear-gradient(135deg, #059669, #047857);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .user-role-user {
        background: linear-gradient(135deg, #6b7280, #4b5563);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .overdue-indicator {
        background: linear-gradient(135deg, #dc2626, #b91c1c);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.5rem;
        font-size: 0.7rem;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    .ticket-card {
        border: 1px solid #e5e7eb;
        border-radius: 0.75rem;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .ticket-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-color: #3b82f6;
        transform: translateY(-1px);
    }
    .history-entry {
        border-left: 3px solid #3b82f6;
        padding-left: 1rem;
        margin-bottom: 1rem;
        background: #f8fafc;
        padding: 0.75rem;
        border-radius: 0.5rem;
    }
    .history-timestamp {
        color: #6b7280;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .history-user {
        color: #3b82f6;
        font-weight: 600;
    }
    .update-box {
        background: #f0f9ff;
        border: 1px solid #0ea5e9;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .stButton > button {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e5e7eb;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        color: #1f2937;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.2);
        border-color: #3b82f6;
        transform: translateY(-2px);
    }
    /* Default button style - for action buttons and pagination */
    .stButton > button {
        background: rgba(55, 65, 81, 0.8) !important;
        border: 1px solid rgba(75, 85, 99, 0.5) !important;
        border-radius: 0.375rem !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
        color: #e5e7eb !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        min-width: auto !important;
        width: auto !important;
        transition: all 0.2s ease !important;
        margin: 0.125rem !important;
    }

    .stButton > button:hover {
        background: rgba(75, 85, 99, 0.9) !important;
        border-color: rgba(156, 163, 175, 0.7) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4) !important;
        transform: translateY(-1px) !important;
        color: #f3f4f6 !important;
    }

    .stButton > button:disabled {
        background: rgba(31, 41, 55, 0.3) !important;
        border-color: rgba(55, 65, 81, 0.3) !important;
        color: rgba(156, 163, 175, 0.5) !important;
        box-shadow: none !important;
        cursor: not-allowed !important;
        transform: none !important;
    }

    /* Larger style for dashboard metric buttons and main action buttons */
    .stButton > button[data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%) !important;
        border: 1px solid rgba(75, 85, 99, 0.7) !important;
        border-radius: 0.75rem !important;
        padding: 1.5rem 2rem !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3) !important;
        color: #f3f4f6 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }

    .stButton > button[data-testid="baseButton-secondary"]:hover {
        background: linear-gradient(135deg, #4b5563 0%, #6b7280 100%) !important;
        border-color: rgba(156, 163, 175, 0.8) !important;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4) !important;
        transform: translateY(-2px) !important;
        color: #ffffff !important;
    }
    /* Large dashboard metric buttons ONLY - using specific container targeting */
    div[data-testid="column"] .metric-button {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%) !important;
        border: 2px solid rgba(75, 85, 99, 0.7) !important;
        border-radius: 1rem !important;
        padding: 2rem 1.5rem !important;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.25) !important;
        color: #f3f4f6 !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        line-height: 1.4 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        min-height: 120px !important;
        text-align: center !important;
        cursor: pointer !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
    }

    div[data-testid="column"] .metric-button:hover {
        background: linear-gradient(135deg, #4b5563 0%, #6b7280 100%) !important;
        border-color: rgba(156, 163, 175, 0.9) !important;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4) !important;
        transform: translateY(-3px) scale(1.02) !important;
        color: #ffffff !important;
    }

    /* Hide the actual streamlit buttons for metric cards */
    .metric-button-hidden {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

db_lock = threading.Lock()

class DatabaseManager:
    def __init__(self, db_path="flowtls_professional.db"):
        self.db_path = db_path
        self._init_database()
    
    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
            conn.execute("PRAGMA synchronous=NORMAL")
            return conn
        except Exception as e:
            st.error(f"Database connection error: {str(e)}")
            raise
    
    def _init_database(self):
        # with db_lock:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    role TEXT DEFAULT 'User',
                    department TEXT DEFAULT '',
                    phone TEXT DEFAULT '',
                    company_id TEXT DEFAULT '',
                    is_active INTEGER DEFAULT 1,
                    created_date TEXT NOT NULL,
                    last_login_date TEXT,
                    created_by TEXT DEFAULT '',
                    can_create_users INTEGER DEFAULT 0,
                    can_deactivate_users INTEGER DEFAULT 0,
                    can_reset_passwords INTEGER DEFAULT 0,
                    can_manage_tickets INTEGER DEFAULT 0,
                    can_view_all_tickets INTEGER DEFAULT 0,
                    can_delete_tickets INTEGER DEFAULT 0,
                    can_export_data INTEGER DEFAULT 0,
                    location TEXT DEFAULT ''
                );
                
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    priority TEXT DEFAULT 'Medium',
                    status TEXT DEFAULT 'Open',
                    assigned_to TEXT DEFAULT '',
                    category TEXT DEFAULT 'General',
                    subcategory TEXT DEFAULT '',
                    created_date TEXT NOT NULL,
                    updated_date TEXT,
                    due_date TEXT,
                    reporter TEXT DEFAULT '',
                    resolution TEXT DEFAULT '',
                    tags TEXT DEFAULT '',
                    estimated_hours REAL DEFAULT 0,
                    actual_hours REAL DEFAULT 0,
                    company_id TEXT DEFAULT '',
                    source TEXT DEFAULT 'Manual',
                    modified_by TEXT DEFAULT '',
                    last_viewed_by TEXT DEFAULT '',
                    last_viewed_date TEXT,
                    is_locked INTEGER DEFAULT 0,
                    locked_by TEXT DEFAULT '',
                    locked_date TEXT,
                    email_thread_id TEXT DEFAULT '',
                    auto_generated INTEGER DEFAULT 0
                );
                
                CREATE TABLE IF NOT EXISTS ticket_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    field_changed TEXT DEFAULT '',
                    old_value TEXT DEFAULT '',
                    new_value TEXT DEFAULT '',
                    comment TEXT DEFAULT '',
                    created_by TEXT NOT NULL,
                    created_date TEXT NOT NULL,
                    session_id TEXT DEFAULT '',
                    FOREIGN KEY (ticket_id) REFERENCES tickets (id)
                );
                
                CREATE TABLE IF NOT EXISTS ticket_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER NOT NULL,
                    update_text TEXT NOT NULL,
                    is_internal BOOLEAN DEFAULT 0,
                    created_by TEXT NOT NULL,
                    created_date TEXT NOT NULL,
                    email_sent BOOLEAN DEFAULT 0,
                    FOREIGN KEY (ticket_id) REFERENCES tickets (id)
                );
                
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT UNIQUE NOT NULL,
                    company_name TEXT NOT NULL,
                    contact_email TEXT DEFAULT '',
                    phone TEXT DEFAULT '',
                    address TEXT DEFAULT '',
                    is_active INTEGER DEFAULT 1,
                    created_date TEXT NOT NULL,
                    support_email TEXT DEFAULT ''
                );
                
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_id TEXT UNIQUE NOT NULL,
                    login_time TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    ip_address TEXT DEFAULT '',
                    user_agent TEXT DEFAULT '',
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                
                CREATE TABLE IF NOT EXISTS email_integration (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_address TEXT NOT NULL,
                    ticket_id INTEGER,
                    subject TEXT,
                    body TEXT,
                    received_date TEXT NOT NULL,
                    processed BOOLEAN DEFAULT 0,
                    FOREIGN KEY (ticket_id) REFERENCES tickets (id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
                CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority);
                CREATE INDEX IF NOT EXISTS idx_tickets_assigned_to ON tickets(assigned_to);
                CREATE INDEX IF NOT EXISTS idx_tickets_company_id ON tickets(company_id);
                CREATE INDEX IF NOT EXISTS idx_tickets_created_date ON tickets(created_date);
                CREATE INDEX IF NOT EXISTS idx_ticket_history_ticket_id ON ticket_history(ticket_id);
                CREATE INDEX IF NOT EXISTS idx_ticket_updates_ticket_id ON ticket_updates(ticket_id);
                CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
            """)                
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                self._create_default_users(cursor)
            
            cursor.execute("SELECT COUNT(*) FROM tickets")
            if cursor.fetchone()[0] == 0:
                self._create_sample_tickets(cursor)
            
            cursor.execute("SELECT COUNT(*) FROM companies")
            if cursor.fetchone()[0] == 0:
                self._create_sample_companies(cursor)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Database initialization error: {str(e)}")
            raise
    
    def _create_default_users(self, cursor):
        users = [
            ('admin', 'admin@flowtls.com', 'admin123', 'System', 'Administrator', 'Admin', 'IT', '+1-555-0001', 'FLOWTLS001', 1, 1, 1, 1, 1, 1, 1, 'San Francisco, CA'),
            ('jsmith', 'john.smith@flowtls.com', 'password123', 'John', 'Smith', 'Manager', 'Support', '+1-555-0002', 'FLOWTLS001', 0, 0, 0, 1, 1, 0, 1, 'New York, NY'),
            ('achen', 'alice.chen@flowtls.com', 'password123', 'Alice', 'Chen', 'Agent', 'Technical', '+1-555-0003', 'FLOWTLS001', 0, 0, 0, 1, 1, 0, 0, 'Austin, TX'),
            ('sjohnson', 'sarah.johnson@flowtls.com', 'password123', 'Sarah', 'Johnson', 'User', 'Operations', '+1-555-0005', 'CLIENT001', 0, 0, 0, 0, 0, 0, 0, 'Denver, CO')
        ]
        
        for user_data in users:
            try:
                salt = secrets.token_hex(32)
                password_hash = hashlib.sha256((user_data[2] + salt).encode()).hexdigest()
                
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, salt, first_name, last_name, 
                                     role, department, phone, company_id, created_date, created_by,
                                     can_create_users, can_deactivate_users, can_reset_passwords,
                                     can_manage_tickets, can_view_all_tickets, can_delete_tickets,
                                     can_export_data, location)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_data[0], user_data[1], password_hash, salt,
                    user_data[3], user_data[4], user_data[5],
                    user_data[6], user_data[7], user_data[8],
                    datetime.now().isoformat(), 'System',
                    user_data[9], user_data[10], user_data[11], user_data[12],
                    user_data[13], user_data[14], user_data[15], user_data[16]
                ))
            except Exception as e:
                st.error(f"Error creating user {user_data[0]}: {str(e)}")
    
    def _create_sample_tickets(self, cursor):
        sample_tickets = [
            ("FlowTLS Integration Critical Error", "System integration completely failing - production down", "Critical", "Open", "John Smith", "Integration", "System Integration", "Sarah Johnson", "urgent,integration,flowtls,production", "CLIENT001"),
            ("User Authentication SSO Issues", "Multiple users unable to login with SSO affecting entire department", "High", "In Progress", "Alice Chen", "Security", "Authentication", "System Administrator", "sso,login,authentication,department", "CLIENT002"),
            ("Database Performance Degradation", "Customer reports taking 30+ seconds to load, needs immediate optimization", "High", "Open", "Alice Chen", "Performance", "Database", "John Smith", "performance,database,reports,slow", "CLIENT001"),
            ("UI Modernization Project", "Update interface design to match new corporate brand guidelines", "Medium", "Open", "Alice Chen", "Enhancement", "User Interface", "Sarah Johnson", "ui,enhancement,design,branding", "CLIENT001"),
            ("Email Notification System", "Configure automated email alerts for high priority tickets", "Medium", "Resolved", "John Smith", "Configuration", "Email System", "System Administrator", "email,notifications,alerts", "CLIENT002")
        ]
        
        for i in range(len(sample_tickets)):
            ticket = sample_tickets[i]
            title = ticket[0]
            desc = ticket[1] 
            priority = ticket[2]
            status = ticket[3]
            assigned_to = ticket[4]
            category = ticket[5]
            subcategory = ticket[6]
            reporter = ticket[7]
            tags = ticket[8]
            company_id = ticket[9]
            
            try:
                hours_to_add = {"Critical": 4, "High": 8, "Medium": 24, "Low": 72}[priority]
                due_date = datetime.now() + timedelta(hours=hours_to_add)
                
                if i % 4 == 0 and status in ["Open", "In Progress"]:
                    due_date = datetime.now() - timedelta(hours=2)
                
                cursor.execute("""
                    INSERT INTO tickets (title, description, priority, status, assigned_to, category, 
                                   subcategory, created_date, updated_date, due_date, reporter, tags, company_id, modified_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (title, desc, priority, status, assigned_to, category, subcategory, 
                      (datetime.now() - timedelta(days=i)).isoformat(), 
                      (datetime.now() - timedelta(days=i, hours=2)).isoformat(),
                      due_date.isoformat(), reporter, tags, company_id, 'System'))
                
                ticket_id = cursor.lastrowid
                cursor.execute("""
                    INSERT INTO ticket_history (ticket_id, action_type, comment, created_by, created_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (ticket_id, 'Created', f'Ticket created: {title}', 'System', 
                          (datetime.now() - timedelta(days=i)).isoformat()))
                
            except Exception as e:
                st.error(f"Error creating sample ticket {i}: {str(e)}")
                
    def _create_sample_companies(self, cursor):
        companies = [
            ("FLOWTLS001", "FlowTLS Internal", "admin@flowtls.com", "+1-555-0000", "123 Tech Street, Silicon Valley, CA", "support@flowtls.com"),
            ("CLIENT001", "Acme Corporation", "support@acme.com", "+1-555-1000", "456 Business Ave, New York, NY", "tickets@acme.com"),
            ("CLIENT002", "TechStart Inc", "help@techstart.com", "+1-555-2000", "789 Innovation Dr, Austin, TX", "support@techstart.com")
        ]
    
        for company_id, name, email, phone, address, support_email in companies:
            try:
                cursor.execute("""
                    INSERT INTO companies (company_id, company_name, contact_email, phone, address, created_date, support_email)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (company_id, name, email, phone, address, datetime.now().isoformat(), support_email))
            except Exception as e:
                st.error(f"Error creating company {company_id}: {str(e)}")

class ConcurrencyManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.lock_timeout_minutes = 15
    
    def acquire_ticket_lock(self, ticket_id: int, user_name: str) -> Tuple[bool, str]:
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Check if ticket is already locked
            cursor.execute("""
                SELECT locked_by, locked_date FROM tickets 
                WHERE id = ? AND is_locked = 1
            """, (ticket_id,))
            
            existing_lock = cursor.fetchone()
            if existing_lock:
                locked_by, locked_date = existing_lock
                if locked_date:
                    lock_time = datetime.fromisoformat(locked_date)
                    if datetime.now() - lock_time < timedelta(minutes=self.lock_timeout_minutes):
                        if locked_by != user_name:
                            conn.close()
                            return False, f"Ticket is being edited by {locked_by}"
            
            # Acquire lock
            cursor.execute("""
                UPDATE tickets SET is_locked = 1, locked_by = ?, locked_date = ?
                WHERE id = ?
            """, (user_name, datetime.now().isoformat(), ticket_id))
            
            conn.commit()
            conn.close()
            return True, "Lock acquired"
        except Exception as e:
            return False, f"Error acquiring lock: {str(e)}"
    
    def release_ticket_lock(self, ticket_id: int, user_name: str):
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE tickets SET is_locked = 0, locked_by = '', locked_date = ''
                WHERE id = ? AND locked_by = ?
            """, (ticket_id, user_name))
            
            conn.commit()
            conn.close()
        except Exception as e:
            pass
    
    def check_ticket_lock_status(self, ticket_id: int) -> Dict:
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT is_locked, locked_by, locked_date FROM tickets WHERE id = ?
            """, (ticket_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'is_locked': bool(result[0]),
                    'locked_by': result[1] or '',
                    'locked_date': result[2] or ''
                }
            return {'is_locked': False, 'locked_by': '', 'locked_date': ''}
        except Exception as e:
            return {'is_locked': False, 'locked_by': '', 'locked_date': ''}

class AuthService:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def hash_password(self, password: str, salt: str) -> str:
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def verify_password(self, password: str, hash_value: str, salt: str) -> bool:
        return self.hash_password(password, salt) == hash_value
    
    def create_session(self, user_id: int, ip_address: str = "", user_agent: str = "") -> str:
        session_id = str(uuid.uuid4())
    
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_sessions (user_id, session_id, login_time, last_activity, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, session_id, datetime.now().isoformat(), datetime.now().isoformat(), ip_address, user_agent))
            
            conn.commit()
            conn.close()
            return session_id
        except Exception as e:
            return ""

    def update_session_activity(self, session_id: str):
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE user_sessions SET last_activity = ? WHERE session_id = ? AND is_active = 1
            """, (datetime.now().isoformat(), session_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            pass
    
    def login(self, username: str, password: str) -> Tuple[bool, Optional[Dict], str]:
        if not username or not password:
            return False, None, "Username and password are required"
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Simple query without complex locking
            cursor.execute("""
                SELECT id, username, email, password_hash, salt, first_name, last_name, role,
                       department, company_id, is_active, can_create_users, can_deactivate_users,
                       can_reset_passwords, can_manage_tickets, can_view_all_tickets, 
                       can_delete_tickets, can_export_data, location
                FROM users WHERE username = ? AND is_active = 1
            """, (username,))
            
            user = cursor.fetchone()
            st.write(f"Debug: Found user: {user is not None}")
            
            if not user:
                conn.close()
                return False, None, "Invalid username or password"
            
            st.write(f"Debug: Password verification passed")
            if not self.verify_password(password, user[3], user[4]):
                conn.close()
                return False, None, "Invalid username or password"
            
            # Update last login
            #cursor.execute("UPDATE users SET last_login_date = ? WHERE id = ?", 
                         # (datetime.now().isoformat(), user[0]))
            
            # Create simple session ID
            session_id = str(uuid.uuid4())
            
            user_data = {
                'id': user[0], 'username': user[1], 'email': user[2],
                'first_name': user[5], 'last_name': user[6], 
                'full_name': f"{user[5]} {user[6]}".strip(),
                'role': user[7], 'department': user[8], 'company_id': user[9],
                'location': user[18] if len(user) > 18 and user[18] else 'Unknown',
                'session_id': session_id,
                'permissions': {
                    'can_create_users': bool(user[11]), 'can_deactivate_users': bool(user[12]),
                    'can_reset_passwords': bool(user[13]), 'can_manage_tickets': bool(user[14]),
                    'can_view_all_tickets': bool(user[15]), 'can_delete_tickets': bool(user[16]),
                    'can_export_data': bool(user[17])
                }
            }
            
            #conn.commit()
            conn.close()
            return True, user_data, ""
            
        except Exception as e:
            st.error(f"Login error details: {str(e)}")
            return False, None, f"Authentication error: {str(e)}"

class UserService:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_all_users(self, include_inactive=False):
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT id, username, email, first_name, last_name, role, department, 
                       company_id, is_active, created_date, last_login_date, created_by,
                       can_create_users, can_deactivate_users, can_reset_passwords,
                       can_manage_tickets, can_view_all_tickets, can_delete_tickets,
                       can_export_data, phone, location
                FROM users {} ORDER BY created_date DESC
            """.format("" if include_inactive else "WHERE is_active = 1")                
            cursor.execute(query)
            
            users = []
            for row in cursor.fetchall():
                user = {
                    'id': row[0], 'username': row[1], 'email': row[2],
                    'first_name': row[3], 'last_name': row[4], 'full_name': f"{row[3]} {row[4]}".strip(),
                    'role': row[5], 'department': row[6], 'company_id': row[7],
                    'is_active': bool(row[8]), 'created_date': row[9], 'last_login_date': row[10],
                    'created_by': row[11], 'phone': row[19], 
                    'location': row[20] or 'Unknown',
                    'permissions': {
                        'can_create_users': bool(row[12]), 'can_deactivate_users': bool(row[13]),
                        'can_reset_passwords': bool(row[14]), 'can_manage_tickets': bool(row[15]),
                        'can_view_all_tickets': bool(row[16]), 'can_delete_tickets': bool(row[17]),
                        'can_export_data': bool(row[18])
                    }
                }
                users.append(user)
            
            conn.close()
            return users
                
        except Exception as e:
            st.error(f"Error retrieving users: {str(e)}")
            return []
    
    def get_companies(self):
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT company_id, company_name, contact_email, phone, address, is_active FROM companies ORDER BY company_name")
            
            companies = []
            for row in cursor.fetchall():
                company = {
                    'company_id': row[0], 'company_name': row[1], 'contact_email': row[2],
                    'phone': row[3], 'address': row[4], 'is_active': bool(row[5])
                }
                companies.append(company)
            
            conn.close()
            return companies
        except Exception as e:
            st.error(f"Error retrieving companies: {str(e)}")
            return []
    
    def get_company_by_id(self, company_id):
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT company_id, company_name, contact_email, phone, address FROM companies WHERE company_id = ?", (company_id,))
            row = cursor.fetchone()
            
            if row:
                company = {
                    'company_id': row[0], 'company_name': row[1], 'contact_email': row[2],
                    'phone': row[3], 'address': row[4]
                }
                conn.close()
                return company
            
            conn.close()
            return None
        except Exception as e:
            st.error(f"Error retrieving company: {str(e)}")
            return None


class TicketService:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_all_tickets(self, user_id: int, permissions: Dict, user_name: str) -> List[Dict]:
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            if permissions.get('can_view_all_tickets', False):
                cursor.execute("""
                    SELECT id, title, description, priority, status, assigned_to, category, subcategory,
                           created_date, updated_date, due_date, reporter, resolution, tags,
                           estimated_hours, actual_hours, company_id, source, modified_by,
                           last_viewed_by, last_viewed_date, is_locked, locked_by, locked_date,
                           email_thread_id, auto_generated
                    FROM tickets ORDER BY created_date DESC
                """)                
            else:
                cursor.execute("""
                    SELECT id, title, description, priority, status, assigned_to, category, subcategory,
                           created_date, updated_date, due_date, reporter, resolution, tags,
                           estimated_hours, actual_hours, company_id, source, modified_by,
                           last_viewed_by, last_viewed_date, is_locked, locked_by, locked_date,
                           email_thread_id, auto_generated
                    FROM tickets WHERE reporter = ? OR assigned_to = ? ORDER BY created_date DESC
                """, (user_name, user_name))
            
            tickets = []
            for row in cursor.fetchall():
                ticket = {
                    'id': row[0], 'title': row[1], 'description': row[2], 'priority': row[3],
                    'status': row[4], 'assigned_to': row[5] or 'Unassigned', 'category': row[6],
                    'subcategory': row[7], 'created_date': row[8], 'updated_date': row[9],
                    'due_date': row[10], 'reporter': row[11] or 'Unknown', 'resolution': row[12],
                    'tags': row[13], 'estimated_hours': row[14], 'actual_hours': row[15],
                    'company_id': row[16], 'source': row[17], 'modified_by': row[18],
                    'last_viewed_by': row[19], 'last_viewed_date': row[20], 'is_locked': bool(row[21]), 'locked_by': row[22] or '', 'locked_date': row[23],
                    'email_thread_id': row[24] or '', 'auto_generated': bool(row[25]),
                    'is_overdue': self.is_ticket_overdue(row[10], row[4])
                }
                tickets.append(ticket)
            
            conn.close()
            return tickets
        except Exception as e:
            st.error(f"Error retrieving tickets: {str(e)}")
            return []
    
    def get_ticket_by_id(self, ticket_id: int) -> Optional[Dict]:
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, title, description, priority, status, assigned_to, category, subcategory,
                       created_date, updated_date, due_date, reporter, resolution, tags,
                       estimated_hours, actual_hours, company_id, source, modified_by,
                       last_viewed_by, last_viewed_date
                FROM tickets WHERE id = ?
            """, (ticket_id,))
            
            row = cursor.fetchone()
            if row:
                ticket = {
                    'id': row[0], 'title': row[1], 'description': row[2], 'priority': row[3],
                    'status': row[4], 'assigned_to': row[5] or 'Unassigned', 'category': row[6],
                    'subcategory': row[7], 'created_date': row[8], 'updated_date': row[9],
                    'due_date': row[10], 'reporter': row[11] or 'Unknown', 'resolution': row[12],
                    'tags': row[13], 'estimated_hours': row[14], 'actual_hours': row[15],
                    'company_id': row[16], 'source': row[17], 'modified_by': row[18],
                    'last_viewed_by': row[19], 'last_viewed_date': row[20],
                    'is_overdue': self.is_ticket_overdue(row[10], row[4])
                }
                conn.close()
                return ticket
            
            conn.close()
            return None
        except Exception as e:
            st.error(f"Error retrieving ticket: {str(e)}")
            return None
    
    def get_ticket_history(self, ticket_id: int) -> List[Dict]:
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, action_type, field_changed, old_value, new_value, comment,
                       created_by, created_date
                FROM ticket_history WHERE ticket_id = ? ORDER BY created_date DESC
            """, (ticket_id,))
            
            history = []
            for row in cursor.fetchall():
                entry = {
                    'id': row[0], 'action_type': row[1], 'field_changed': row[2],
                    'old_value': row[3], 'new_value': row[4], 'comment': row[5],
                    'created_by': row[6], 'created_date': row[7]
                }
                history.append(entry)
            
            conn.close()
            return history
        except Exception as e:
            st.error(f"Error retrieving ticket history: {str(e)}")
            return []
    
    def get_ticket_updates(self, ticket_id: int) -> List[Dict]:
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, update_text, is_internal, created_by, created_date
                FROM ticket_updates WHERE ticket_id = ? ORDER BY created_date DESC
            """, (ticket_id,))
            
            updates = []
            for row in cursor.fetchall():
                update = {
                    'id': row[0], 'update_text': row[1], 'is_internal': bool(row[2]),
                    'created_by': row[3], 'created_date': row[4]
                }
                updates.append(update)
            
            conn.close()
            return updates
        except Exception as e:
            st.error(f"Error retrieving ticket updates: {str(e)}")
            return []
    
    def update_ticket_last_viewed(self, ticket_id: int, user_name: str):
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE tickets SET last_viewed_by = ?, last_viewed_date = ?
                WHERE id = ?
            """, (user_name, datetime.now().isoformat(), ticket_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            st.error(f"Error updating last viewed: {str(e)}")
    
    def update_ticket(self, ticket_id: int, ticket_data: Dict, user_name: str) -> bool:
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get current ticket data for comparison
            cursor.execute("""
                SELECT title, description, priority, status, assigned_to, category, 
                       subcategory, tags, estimated_hours, actual_hours, resolution
                FROM tickets WHERE id = ?
            """, (ticket_id,))
            
            current_data = cursor.fetchone()
            if not current_data:
                conn.close()
                return False
            
            current_fields = {
                'title': current_data[0], 'description': current_data[1],
                'priority': current_data[2], 'status': current_data[3],
                'assigned_to': current_data[4], 'category': current_data[5],
                'subcategory': current_data[6], 'tags': current_data[7],
                'estimated_hours': current_data[8], 'actual_hours': current_data[9],
                'resolution': current_data[10]
            }
            
            # Update the ticket
            cursor.execute("""
                UPDATE tickets SET title = ?, description = ?, priority = ?, status = ?,
                                 assigned_to = ?, category = ?, subcategory = ?, tags = ?,
                                 estimated_hours = ?, actual_hours = ?, resolution = ?,
                                 updated_date = ?, modified_by = ?
                WHERE id = ?
            """, (
                ticket_data['title'], ticket_data['description'], ticket_data['priority'],
                ticket_data['status'], ticket_data['assigned_to'], ticket_data['category'],
                ticket_data['subcategory'], ticket_data['tags'], ticket_data['estimated_hours'],
                ticket_data['actual_hours'], ticket_data['resolution'],
                datetime.now().isoformat(), user_name, ticket_id
            ))
            
            # Log changes in history
            for field, new_value in ticket_data.items():
                if field in current_fields and str(current_fields[field]) != str(new_value):
                    cursor.execute("""
                        INSERT INTO ticket_history (ticket_id, action_type, field_changed,
                                                   old_value, new_value, created_by, created_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (ticket_id, 'Updated', field, str(current_fields[field]),
                          str(new_value), user_name, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error updating ticket: {str(e)}")
            return False
    
    def add_ticket_update(self, ticket_id: int, update_text: str, is_internal: bool, user_name: str) -> bool:
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ticket_updates (ticket_id, update_text, is_internal, created_by, created_date)
                VALUES (?, ?, ?, ?, ?)
            """, (ticket_id, update_text, is_internal, user_name, datetime.now().isoformat()))
            
            # Add to history
            update_type = "Internal Update" if is_internal else "Public Update"
            cursor.execute("""
                INSERT INTO ticket_history (ticket_id, action_type, comment, created_by, created_date)
                VALUES (?, ?, ?, ?, ?)
            """, (ticket_id, update_type, update_text, user_name, datetime.now().isoformat()))
            
            # Update ticket's updated_date
            cursor.execute("""
                UPDATE tickets SET updated_date = ?, modified_by = ? WHERE id = ?
            """, (datetime.now().isoformat(), user_name, ticket_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error adding ticket update: {str(e)}")
            return False
    
    def is_ticket_overdue(self, due_date: str, status: str) -> bool:
        if not due_date or status in ['Resolved', 'Closed']:
            return False
        try:
            due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            return due < datetime.now()
        except:
            return False
    
    def create_ticket(self, ticket_data: Dict, user_name: str) -> bool:
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            hours_to_add = {"Critical": 4, "High": 8, "Medium": 24, "Low": 72}[ticket_data['priority']]
            due_date = datetime.now() + timedelta(hours=hours_to_add)
            
            cursor.execute("""
                INSERT INTO tickets (title, description, priority, status, assigned_to, category, 
                                   subcategory, created_date, updated_date, due_date, reporter, tags, 
                                   company_id, modified_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket_data['title'], ticket_data['description'], ticket_data['priority'],
                ticket_data['status'], ticket_data['assigned_to'], ticket_data['category'],
                ticket_data['subcategory'], datetime.now().isoformat(), datetime.now().isoformat(),
                due_date.isoformat(), user_name, ticket_data['tags'], 
                ticket_data['company_id'], user_name
            ))
            
            ticket_id = cursor.lastrowid
            
            # Add initial history entry
            cursor.execute("""
                INSERT INTO ticket_history (ticket_id, action_type, comment, created_by, created_date)
                VALUES (?, ?, ?, ?, ?)
            """, (ticket_id, 'Created', f'Ticket created: {ticket_data["title"]}', 
                  user_name, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error creating ticket: {str(e)}")
            return False


class UserManagementService:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create_user(self, user_data: Dict, created_by: str) -> Tuple[bool, str]:
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ? OR email = ?", 
                         (user_data['username'], user_data['email']))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return False, "Username or email already exists"
            
            salt = secrets.token_hex(32)
            password_hash = hashlib.sha256((user_data['password'] + salt).encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, salt, first_name, last_name, 
                                 role, department, phone, company_id, created_date, created_by,
                                 can_create_users, can_deactivate_users, can_reset_passwords,
                                 can_manage_tickets, can_view_all_tickets, can_delete_tickets,
                                 can_export_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_data['username'], user_data['email'], password_hash, salt,
                user_data['first_name'], user_data['last_name'], user_data['role'],
                user_data['department'], user_data['phone'], user_data['company_id'],
                datetime.now().isoformat(), created_by,
                user_data.get('can_create_users', 0), user_data.get('can_deactivate_users', 0),
                user_data.get('can_reset_passwords', 0), user_data.get('can_manage_tickets', 0),
                user_data.get('can_view_all_tickets', 0), user_data.get('can_delete_tickets', 0),
                user_data.get('can_export_data', 0)
            ))
            
            conn.commit()
            conn.close()
            return True, "User created successfully"
        except Exception as e:
            return False, f"Error creating user: {str(e)}"
    
    def update_user(self, user_id: int, user_data: Dict) -> Tuple[bool, str]:
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET first_name = ?, last_name = ?, role = ?, department = ?,
                               phone = ?, company_id = ?, can_create_users = ?, 
                               can_deactivate_users = ?, can_reset_passwords = ?,
                               can_manage_tickets = ?, can_view_all_tickets = ?,
                               can_delete_tickets = ?, can_export_data = ?
                WHERE id = ?
            """, (
                user_data['first_name'], user_data['last_name'], user_data['role'],
                user_data['department'], user_data['phone'], user_data['company_id'],
                user_data.get('can_create_users', 0), user_data.get('can_deactivate_users', 0),
                user_data.get('can_reset_passwords', 0), user_data.get('can_manage_tickets', 0),
                user_data.get('can_view_all_tickets', 0), user_data.get('can_delete_tickets', 0),
                user_data.get('can_export_data', 0), user_id
            ))
            
            conn.commit()
            conn.close()
            return True, "User updated successfully"
        except Exception as e:
            return False, f"Error updating user: {str(e)}"
    
    def reset_password(self, user_id: int, new_password: str) -> Tuple[bool, str]:
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            salt = secrets.token_hex(32)
            password_hash = hashlib.sha256((new_password + salt).encode()).hexdigest()
            
            cursor.execute("UPDATE users SET password_hash = ?, salt = ? WHERE id = ?", 
                         (password_hash, salt, user_id))
            
            conn.commit()
            conn.close()
            return True, "Password reset successfully"
        except Exception as e:
            return False, f"Error resetting password: {str(e)}"
    
    def deactivate_user(self, user_id: int) -> Tuple[bool, str]:
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            return True, "User deactivated successfully"
        except Exception as e:
            return False, f"Error deactivating user: {str(e)}"
    
    def activate_user(self, user_id: int) -> Tuple[bool, str]:
        # with db_lock:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET is_active = 1 WHERE id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            return True, "User activated successfully"
        except Exception as e:
            return False, f"Error activating user: {str(e)}"


def init_services():
    try:
        db_manager = DatabaseManager()
        auth_service = AuthService(db_manager)
        ticket_service = TicketService(db_manager)
        user_service = UserService(db_manager)
        user_management_service = UserManagementService(db_manager)
        concurrency_manager = ConcurrencyManager(db_manager)
        return db_manager, auth_service, ticket_service, user_service, user_management_service, concurrency_manager
    except Exception as e:
        st.error(f"Failed to initialize services: {str(e)}")
        st.stop()

try:
    db_manager, auth_service, ticket_service, user_service, user_management_service, concurrency_manager = init_services()
except Exception as e:
    st.error("Application initialization failed. Please refresh the page.")
    st.stop()

if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'selected_ticket_id' not in st.session_state:
    st.session_state.selected_ticket_id = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'ticket_filter' not in st.session_state:
    st.session_state.ticket_filter = 'All'


def require_auth(permission: str = None) -> bool:
    if not st.session_state.user:
        st.session_state.page = 'login'
        return False
    if permission and not st.session_state.user.get('permissions', {}).get(permission, False):
        st.error("⚠️ Access Denied: You don't have permission for this action")
        return False
    return True


def format_date(date_str: str) -> str:
    if not date_str:
        return "N/A"
    try:
        if isinstance(date_str, str):
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            date_obj = date_str
        return date_obj.strftime("%b %d, %Y %I:%M %p")
    except:
        return str(date_str)


def show_login_page():
    st.markdown('<div class="main-header"><h1>🎫 FlowTLS SYNC+ Professional</h1><p>Enterprise Ticketing & Service Management Platform</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Sign In")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            
            if submitted:
                st.write(f"Debug: Form submitted with username: {username}, password length: {len(password) if password else 0}")
                if username and password:
                    try:
                        st.write("Debug: About to call auth_service.login()")
                        success, user, error_msg = auth_service.login(username, password)
                        st.write(f"Debug: Login result - Success: {success}, Error: {error_msg}")
                        if success:
                            st.session_state.user = user
                            st.session_state.page = 'dashboard'
                            st.rerun()
                        else:
                            st.error(error_msg)
                    except Exception as e:
                        st.error(f"Login error: {str(e)}")
                else:
                    st.error("Please enter both username and password")
        
        with st.expander("🎭 Demo User Accounts", expanded=True):
            st.markdown("**Administrator:** `admin` / `admin123` - Full system access  \n**Manager:** `jsmith` / `password123` - Can manage tickets and view reports  \n**Agent:** `achen` / `password123` - Can work on assigned tickets  \n**User:** `sjohnson` / `password123` - Can create and view own tickets")


def show_dashboard():
    if not require_auth():
        return
    
    user = st.session_state.user
    st.markdown(f'<div class="main-header"><h1>🎫 FlowTLS SYNC+ Dashboard</h1><p>Welcome back, {user["full_name"]}! | Role: <strong>{user["role"]}</strong> | Department: {user["department"]}</p></div>', unsafe_allow_html=True)
    
    tickets = ticket_service.get_all_tickets(user['id'], user['permissions'], user['full_name'])
    
    st.subheader("🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Create New Ticket", use_container_width=True):
            st.session_state.page = 'create_ticket'
            st.rerun()
    
    with col2:
        if st.button("🎫 View All Tickets", use_container_width=True):
            st.session_state.page = 'tickets'
            st.rerun()
    
    with col3:
        if user['permissions'].get('can_view_all_tickets', False):
            if st.button("📊 Analytics", use_container_width=True):
                st.session_state.page = 'analytics'
                st.rerun()
        else:
            st.empty()
    
    with col4:
        if user['permissions'].get('can_create_users', False):
            if st.button("👥 Manage Users", use_container_width=True):
                st.session_state.page = 'users'
                st.rerun()
        else:
            st.empty()
    
    st.subheader("📈 Dashboard Overview")
    
    total_tickets = len(tickets)
    open_tickets = len([t for t in tickets if t['status'] == 'Open'])
    in_progress_tickets = len([t for t in tickets if t['status'] == 'In Progress'])
    resolved_tickets = len([t for t in tickets if t['status'] == 'Resolved'])
    overdue_tickets = len([t for t in tickets if t['is_overdue']])
    
# Add custom CSS just for metric buttons
    st.markdown("""
    <style>
    /* Target buttons by their specific key attributes */
    button[key="metric_total"],
    button[key="metric_open"], 
    button[key="metric_progress"],
    button[key="metric_resolved"],
    button[key="metric_overdue"] {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%) !important;
        border: 2px solid #e5e7eb !important;
        border-radius: 1.5rem !important;
        padding: 3rem 2rem !important;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08) !important;
        color: #1f2937 !important;
        font-weight: 800 !important;
        font-size: 2.5rem !important;
        line-height: 1.2 !important;
        min-height: 200px !important;
        white-space: pre-line !important;
        text-align: center !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Dashboard metrics with custom styling
st.markdown("""
<div style="display: flex; gap: 1rem; margin: 2rem 0;">
    <div class="metric-card" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'All'}, '*')">
        <div class="metric-number">{}</div>
        <div class="metric-label">Total Tickets</div>
    </div>
    <div class="metric-card" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'Open'}, '*')">
        <div class="metric-number" style="color: #dc2626;">{}</div>
        <div class="metric-label">Open Tickets</div>
    </div>
    <div class="metric-card" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'In Progress'}, '*')">
        <div class="metric-number" style="color: #ca8a04;">{}</div>
        <div class="metric-label">In Progress</div>
    </div>
    <div class="metric-card" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'Resolved'}, '*')">
        <div class="metric-number" style="color: #059669;">{}</div>
        <div class="metric-label">Resolved</div>
    </div>
    <div class="metric-card" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'Overdue'}, '*')">
        <div class="metric-number" style="color: #dc2626;">{}</div>
        <div class="metric-label">Overdue</div>
    </div>
</div>

<style>
.metric-card {{
    background: linear-gradient(145deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%);
    border: 2px solid #e5e7eb;
    border-radius: 1.5rem;
    padding: 3rem 2rem;
    text-align: center;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
    cursor: pointer;
    transition: all 0.3s ease;
    flex: 1;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}}

.metric-card:hover {{
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 12px 30px rgba(59, 130, 246, 0.15);
    border-color: #3b82f6;
}}

.metric-number {{
    font-size: 3.5rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 0.5rem;
    color: #1f2937;
}}

.metric-label {{
    font-size: 1.1rem;
    font-weight: 600;
    color: #6b7280;
}}
</style>
""".format(total_tickets, open_tickets, in_progress_tickets, resolved_tickets, overdue_tickets), unsafe_allow_html=True)

# Add invisible buttons for navigation
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("", key="metric_total_hidden", help="Total"):
        st.session_state.ticket_filter = "All"
        st.session_state.page = 'filtered_tickets'
        st.rerun()
        
# Add the rest of the hidden buttons for other columns...
    
    if tickets:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Tickets by Status")
            status_data = pd.DataFrame(tickets)['status'].value_counts()
            fig = px.pie(
                values=status_data.values,
                names=status_data.index,
                color_discrete_map={
                    'Open': '#dc2626',
                    'In Progress': '#ca8a04',
                    'Resolved': '#059669',
                    'Closed': '#6b7280'
                }
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 Tickets by Priority")
            priority_data = pd.DataFrame(tickets)['priority'].value_counts()
            fig = px.bar(
                x=priority_data.index,
                y=priority_data.values,
                color=priority_data.index,
                color_discrete_map={
                    'Critical': '#dc2626',
                    'High': '#ea580c',
                    'Medium': '#ca8a04',
                    'Low': '#059669'
                }
            )
            fig.update_layout(height=350, showlegend=False)
            fig.update_xaxes(title="Priority")
            fig.update_yaxes(title="Number of Tickets")
            st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🕐 Recent Tickets")
    if tickets:
        recent_tickets = sorted(tickets, key=lambda x: x['created_date'], reverse=True)[:5]
        
        for ticket in recent_tickets:
            company = user_service.get_company_by_id(ticket['company_id'])
            company_name = company['company_name'] if company else ticket['company_id']
            
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(f"#{ticket['id']} - {ticket['title']}", key=f"dash_ticket_{ticket['id']}", use_container_width=True):
                        st.session_state.selected_ticket_id = ticket['id']
                        st.session_state.page = 'ticket_detail'
                        st.rerun()
                with col2:
                    if ticket['is_overdue']:
                        st.markdown('<span class="overdue-indicator">⚠️ OVERDUE</span>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 1, 3])
                with col1:
                    st.markdown(f'<span class="priority-{ticket["priority"].lower()}">{ticket["priority"]}</span>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<span class="status-{ticket["status"].lower().replace(" ", "-")}">{ticket["status"]}</span>', unsafe_allow_html=True)
                
                description = ticket['description'][:100] + '...' if len(ticket['description']) > 100 else ticket['description']
                st.write(description)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Company:** {company_name}")
                with col2:
                    st.write(f"**Assigned:** {ticket['assigned_to']}")
                with col3:
                    st.write(f"**Due:** {format_date(ticket['due_date'])}")
                
                st.markdown("---")
    else:
        st.info("No tickets found. Create your first ticket using the button above!")


def show_tickets_page():
    if not require_auth():
        return
    
    st.title("🎫 Ticket Management")
    
    tickets = ticket_service.get_all_tickets(st.session_state.user['id'], 
                                           st.session_state.user['permissions'], 
                                           st.session_state.user['full_name'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Open", "In Progress", "Resolved", "Closed"])
    with col2:
        priority_filter = st.selectbox("Filter by Priority", ["All", "Critical", "High", "Medium", "Low"])
    with col3:
        company_filter = st.selectbox("Filter by Company", ["All"] + list(set([t['company_id'] for t in tickets])))
    
    filtered_tickets = tickets
    if status_filter != "All":
        filtered_tickets = [t for t in filtered_tickets if t['status'] == status_filter]
    if priority_filter != "All":
        filtered_tickets = [t for t in filtered_tickets if t['priority'] == priority_filter]
    if company_filter != "All":
        filtered_tickets = [t for t in filtered_tickets if t['company_id'] == company_filter]
    
    st.subheader(f"Showing {len(filtered_tickets)} of {len(tickets)} tickets")
    
    for ticket in filtered_tickets:
        company = user_service.get_company_by_id(ticket['company_id'])
        company_name = company['company_name'] if company else ticket['company_id']
        
        with st.container():
            st.markdown('<div class="ticket-card">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"#{ticket['id']} - {ticket['title']}", key=f"ticket_{ticket['id']}", use_container_width=True):
                    st.session_state.selected_ticket_id = ticket['id']
                    st.session_state.page = 'ticket_detail'
                    st.rerun()
            with col2:
                if ticket['is_overdue']:
                    st.markdown('<span class="overdue-indicator">⚠️ OVERDUE</span>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 3])
            with col1:
                st.markdown(f'<span class="priority-{ticket["priority"].lower()}">{ticket["priority"]}</span>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<span class="status-{ticket["status"].lower().replace(" ", "-")}">{ticket["status"]}</span>', unsafe_allow_html=True)
            
            if ticket['last_viewed_by'] and ticket['last_viewed_date']:
                last_activity = f"Last viewed by {ticket['last_viewed_by']} on {format_date(ticket['last_viewed_date'])}"
                st.caption(last_activity)
            
            description = ticket['description'][:150] + '...' if len(ticket['description']) > 150 else ticket['description']
            st.write(description)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Company:** {company_name}")
                st.write(f"**Assigned to:** {ticket['assigned_to']}")
                st.write(f"**Created:** {format_date(ticket['created_date'])}")
            with col2:
                st.write(f"**Category:** {ticket['category']}")
                st.write(f"**Reporter:** {ticket['reporter']}")
                st.write(f"**Due:** {format_date(ticket['due_date'])}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")

def show_filtered_tickets_page():
    if not require_auth():
        return
    
    # Get filter from session state
    filter_type = st.session_state.get('ticket_filter', 'All')
    
    # Header with back button
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("← Dashboard"):
            st.session_state.page = 'dashboard'
            st.rerun()
    with col2:
        st.title(f"🎫 {filter_type} Tickets")
    
    tickets = ticket_service.get_all_tickets(st.session_state.user['id'], 
                                           st.session_state.user['permissions'], 
                                           st.session_state.user['full_name'])
    
    # Apply filter
    if filter_type == "Open":
        filtered_tickets = [t for t in tickets if t['status'] == 'Open']
    elif filter_type == "In Progress":
        filtered_tickets = [t for t in tickets if t['status'] == 'In Progress']
    elif filter_type == "Resolved":
        filtered_tickets = [t for t in tickets if t['status'] == 'Resolved']
    elif filter_type == "Overdue":
        filtered_tickets = [t for t in tickets if t['is_overdue']]
    else:  # All
        filtered_tickets = tickets
    
    if not filtered_tickets:
        st.info(f"No {filter_type.lower()} tickets found.")
        return
    
    # Initialize pagination state
    # if 'current_page' not in st.session_state:
        # st.session_state.current_page = 1

    # Default items per page (will be controlled by dropdown at bottom)
    items_per_page = 25
    total_pages = (len(filtered_tickets) - 1) // items_per_page + 1 if len(filtered_tickets) > 0 else 1
    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(filtered_tickets))
    current_tickets = filtered_tickets[start_idx:end_idx]
    

    # Compact table header
    col1, col2, col3, col4, col5, col6, col7 = st.columns([0.8, 2.5, 0.8, 0.8, 1, 1, 2])
    with col1:
        st.write("**ID**")
    with col2:
        st.write("**Title**")
    with col3:
        st.write("**Priority**")
    with col4:
        st.write("**Status**")
    with col5:
        st.write("**Assigned**")
    with col6:
        st.write("**Company**")
    with col7:
        st.write("**Actions**")
    st.markdown("---")
  
    # Compact ticket rows
    for ticket in current_tickets:
        company = user_service.get_company_by_id(ticket['company_id'])
        company_name = company['company_name'] if company else ticket['company_id']
        
        # Truncate title if too long
        title_display = ticket['title'][:40] + '...' if len(ticket['title']) > 40 else ticket['title']
        
        # Status color mapping
        status_colors = {
            'Open': '#dc2626', 'In Progress': '#ca8a04', 
            'Resolved': '#059669', 'Closed': '#6b7280'
        }
        priority_colors = {
            'Critical': '#dc2626', 'High': '#ea580c', 
            'Medium': '#ca8a04', 'Low': '#059669'
        }
        
        overdue_badge = "⚠️" if ticket['is_overdue'] else ""
        
        # Create row with grid layout
        st.markdown(f"""
            <div style="background: white; padding: 0.75rem; border-radius: 0.5rem; margin: 0.25rem 0; border: 1px solid #e5e7eb; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);">
                <div style="display: grid; grid-template-columns: 0.8fr 2.5fr 0.8fr 0.8fr 1fr 1fr 2fr; gap: 1rem; align-items: center; font-size: 0.9rem;">
                    <div style="font-weight: bold; color: #3b82f6;">#{ticket['id']}</div>
                    <div style="color: #374151;">
                        <div style="font-weight: 500;">{title_display}</div>
                        <div style="font-size: 0.8rem; color: #6b7280; margin-top: 0.2rem;">{ticket['description'][:60]}{'...' if len(ticket['description']) > 60 else ''}</div>
                    </div>
                    <div style="text-align: center;">
                        <span style="background: {priority_colors.get(ticket['priority'], '#6b7280')}; color: white; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; font-weight: bold;">
                            {ticket['priority']}
                        </span>
                    </div>
                    <div style="text-align: center;">
                        <span style="background: {status_colors.get(ticket['status'], '#6b7280')}; color: white; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; font-weight: bold;">
                            {ticket['status']} {overdue_badge}
                        </span>
                    </div>
                    <div style="font-size: 0.85rem; color: #374151;">{ticket['assigned_to'][:15]}{'...' if len(ticket['assigned_to']) > 15 else ''}</div>
                    <div style="font-size: 0.85rem; color: #374151;">{company_name[:15]}{'...' if len(company_name) > 15 else ''}</div>
                    <div id="actions_{ticket['id']}" style="text-align: center;">
                        <!-- Actions will be added here by Streamlit -->
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Action buttons in a compact row
        col1, col2, col3, col4, col5, col6, col7 = st.columns([0.8, 2.5, 0.8, 0.8, 1, 1, 2])
        with col7:  # Actions column
            action_col1, action_col2, action_col3, action_col4 = st.columns(4)
            
            with action_col1:
                if st.button("👁️", key=f"view_{ticket['id']}", help="View Details"):
                    st.session_state.selected_ticket_id = ticket['id']
                    st.session_state.page = 'ticket_detail'
                    st.rerun()
            
            with action_col2:
                if st.session_state.user['permissions'].get('can_manage_tickets', False):
                    if st.button("✏️", key=f"edit_{ticket['id']}", help="Edit Ticket"):
                        st.session_state.selected_ticket_id = ticket['id']
                        st.session_state.page = 'ticket_detail'
                        st.rerun()
            
            with action_col3:
                if st.session_state.user['permissions'].get('can_manage_tickets', False):
                    if ticket['status'] == 'Open':
                        if st.button("▶️", key=f"start_{ticket['id']}", help="Start"):
                            ticket_data = {
                                'title': ticket['title'], 'description': ticket['description'],
                                'priority': ticket['priority'], 'status': 'In Progress',
                                'assigned_to': ticket['assigned_to'], 'category': ticket['category'],
                                'subcategory': ticket['subcategory'], 'tags': ticket['tags'],
                                'estimated_hours': ticket['estimated_hours'], 'actual_hours': ticket['actual_hours'],
                                'resolution': ticket['resolution']
                            }
                            if ticket_service.update_ticket(ticket['id'], ticket_data, st.session_state.user['full_name']):
                                st.success("Ticket started!")
                                st.rerun()
                    
                    elif ticket['status'] == 'In Progress':
                        if st.button("✅", key=f"resolve_{ticket['id']}", help="Resolve"):
                            ticket_data = {
                                'title': ticket['title'], 'description': ticket['description'],
                                'priority': ticket['priority'], 'status': 'Resolved',
                                'assigned_to': ticket['assigned_to'], 'category': ticket['category'],
                                'subcategory': ticket['subcategory'], 'tags': ticket['tags'],
                                'estimated_hours': ticket['estimated_hours'], 'actual_hours': ticket['actual_hours'],
                                'resolution': ticket['resolution']
                            }
                            if ticket_service.update_ticket(ticket['id'], ticket_data, st.session_state.user['full_name']):
                                st.success("Ticket resolved!")
                                st.rerun()
                    
                    elif ticket['status'] == 'Resolved':
                        if st.button("🔄", key=f"reopen_{ticket['id']}", help="Reopen"):
                            ticket_data = {
                                'title': ticket['title'], 'description': ticket['description'],
                                'priority': ticket['priority'], 'status': 'Open',
                                'assigned_to': ticket['assigned_to'], 'category': ticket['category'],
                                'subcategory': ticket['subcategory'], 'tags': ticket['tags'],
                                'estimated_hours': ticket['estimated_hours'], 'actual_hours': ticket['actual_hours'],
                                'resolution': ticket['resolution']
                            }
                            if ticket_service.update_ticket(ticket['id'], ticket_data, st.session_state.user['full_name']):
                                st.success("Ticket reopened!")
                                st.rerun()
            
            with action_col4:
                if st.session_state.user['permissions'].get('can_delete_tickets', False):
                    if st.button("🗑️", key=f"delete_{ticket['id']}", help="Delete"):
                        st.warning("Delete functionality not implemented yet")
    
    # Bottom pagination controls - compact
    st.markdown("---")
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1.5, 0.5, 0.5, 1, 0.5, 0.5, 1])

    with col2:
        items_per_page = st.selectbox("Items per page", [10, 25, 50, 100], index=1, key="items_per_page")

    # Recalculate pagination when dropdown changes
    if items_per_page != 25:  # If user changed from default
        total_pages = (len(filtered_tickets) - 1) // items_per_page + 1 if len(filtered_tickets) > 0 else 1
        start_idx = (st.session_state.current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(filtered_tickets))
        current_tickets = filtered_tickets[start_idx:end_idx]

    with col3:
        st.button("⏮️", disabled=(st.session_state.current_page == 1), key="first", on_click=lambda: setattr(st.session_state, 'current_page', 1))

    with col4:
        if st.session_state.current_page > 1:
            st.button("◀️", key="prev", on_click=lambda: setattr(st.session_state, 'current_page', st.session_state.current_page - 1))
        else:
            st.button("◀️", disabled=True, key="prev_disabled")

    with col5:
        st.write(f"Page {st.session_state.current_page} of {total_pages}")

    with col6:
        if st.session_state.current_page < total_pages:
            st.button("▶️", key="next", on_click=lambda: setattr(st.session_state, 'current_page', st.session_state.current_page + 1))
        else:
            st.button("▶️", disabled=True, key="next_disabled")

    with col7:
        st.button("⏭️", disabled=(st.session_state.current_page == total_pages), key="last", on_click=lambda: setattr(st.session_state, 'current_page', total_pages))

def show_ticket_detail_page():
    if not require_auth():
        return
    
    ticket_id = st.session_state.selected_ticket_id
    if not ticket_id:
        st.error("No ticket selected")
        return
    
    ticket = ticket_service.get_ticket_by_id(ticket_id)
    if not ticket:
        st.error("Ticket not found")
        return
    
    # Update last viewed
    ticket_service.update_ticket_last_viewed(ticket_id, st.session_state.user['full_name'])
    
    # Header with back button
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("← Back"):
            st.session_state.page = 'tickets'
            st.rerun()
    with col2:
        st.title(f"🎫 Ticket #{ticket['id']}")
    
    # Ticket header info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"## {ticket['title']}")
    with col2:
        st.markdown(f'<span class="priority-{ticket["priority"].lower()}">{ticket["priority"]}</span>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<span class="status-{ticket["status"].lower().replace(" ", "-")}">{ticket["status"]}</span>', unsafe_allow_html=True)
    
    if ticket['is_overdue']:
        st.markdown('<span class="overdue-indicator">⚠️ OVERDUE TICKET</span>', unsafe_allow_html=True)
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Details", "📝 Updates", "📊 History", "✏️ Edit"])
    
    with tab1:
        # Ticket details
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 Basic Information")
            company = user_service.get_company_by_id(ticket['company_id'])
            company_name = company['company_name'] if company else ticket['company_id']
            
            st.write(f"**Company:** {company_name}")
            st.write(f"**Category:** {ticket['category']}")
            st.write(f"**Subcategory:** {ticket['subcategory']}")
            st.write(f"**Source:** {ticket['source']}")
            st.write(f"**Tags:** {ticket['tags']}")
            
        with col2:
            st.subheader("👥 Assignment & Timing")
            st.write(f"**Reporter:** {ticket['reporter']}")
            st.write(f"**Assigned to:** {ticket['assigned_to']}")
            st.write(f"**Created:** {format_date(ticket['created_date'])}")
            st.write(f"**Updated:** {format_date(ticket['updated_date'])}")
            st.write(f"**Due Date:** {format_date(ticket['due_date'])}")
            
        st.subheader("📝 Description")
        st.write(ticket['description'])
        
        if ticket['resolution']:
            st.subheader("✅ Resolution")
            st.write(ticket['resolution'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Estimated Hours", ticket['estimated_hours'])
        with col2:
            st.metric("Actual Hours", ticket['actual_hours'])
    
    with tab2:
        # Updates section
        st.subheader("💬 Add New Update")
        
        with st.form("add_update_form"):
            update_text = st.text_area("Update", placeholder="Enter update details...", height=100)
            is_internal = st.checkbox("Internal Update (visible only to staff)")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Add Update", use_container_width=True)
            
            if submitted and update_text:
                if ticket_service.add_ticket_update(ticket_id, update_text, is_internal, 
                                                  st.session_state.user['full_name']):
                    st.success("Update added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add update")
        
        # Display existing updates
        st.subheader("📋 Previous Updates")
        updates = ticket_service.get_ticket_updates(ticket_id)
        
        if updates:
            for update in updates:
                update_type = "🔒 Internal" if update['is_internal'] else "📢 Public"
                st.markdown(f"""
                <div class="update-box">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span class="history-user">{update['created_by']}</span>
                        <span style="font-size: 0.8rem;">{update_type} | {format_date(update['created_date'])}</span>
                    </div>
                    <div>{update['update_text']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No updates yet.")
    
    with tab3:
        # History section
        st.subheader("📊 Ticket History")
        history = ticket_service.get_ticket_history(ticket_id)
        
        if history:
            for entry in history:
                icon = {
                    'Created': '🆕',
                    'Updated': '✏️',
                    'Public Update': '📢',
                    'Internal Update': '🔒',
                    'Status Change': '🔄',
                    'Assignment': '👤'
                }.get(entry['action_type'], '📝')
                
                change_text = ""
                if entry['field_changed'] and entry['old_value'] and entry['new_value']:
                    change_text = f"<br><small><strong>{entry['field_changed']}:</strong> '{entry['old_value']}' → '{entry['new_value']}'</small>"
                
                st.markdown(f"""
                <div class="history-entry">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span>{icon} <strong>{entry['action_type']}</strong> by <span class="history-user">{entry['created_by']}</span></span>
                        <span class="history-timestamp">{format_date(entry['created_date'])}</span>
                    </div>
                    {f"<div style='margin-top: 0.5rem;'>{entry['comment']}</div>" if entry['comment'] else ""}
                    {change_text}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No history available.")
    
    with tab4:
        # Edit section
        if not st.session_state.user['permissions'].get('can_manage_tickets', False):
            st.warning("You don't have permission to edit tickets.")
        else:
            st.subheader("✏️ Edit Ticket")
            
            companies = user_service.get_companies()
            company_options = {comp['company_name']: comp['company_id'] for comp in companies}
            current_company_name = next((name for name, id in company_options.items() 
                                       if id == ticket['company_id']), list(company_options.keys())[0])
            
            with st.form("edit_ticket_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    title = st.text_input("Title", value=ticket['title'])
                    priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], 
                                          index=["Low", "Medium", "High", "Critical"].index(ticket['priority']))
                    status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"], 
                                        index=["Open", "In Progress", "Resolved", "Closed"].index(ticket['status']))
                    category = st.selectbox("Category", 
                                          ["General", "Bug", "Enhancement", "Security", "Performance", "Integration", "Maintenance"],
                                          index=["General", "Bug", "Enhancement", "Security", "Performance", "Integration", "Maintenance"].index(ticket['category']) if ticket['category'] in ["General", "Bug", "Enhancement", "Security", "Performance", "Integration", "Maintenance"] else 0)
                
                with col2:
                    assigned_to = st.text_input("Assigned To", value=ticket['assigned_to'])
                    subcategory = st.text_input("Subcategory", value=ticket['subcategory'])
                    tags = st.text_input("Tags", value=ticket['tags'])
                    
                description = st.text_area("Description", value=ticket['description'], height=100)
                resolution = st.text_area("Resolution", value=ticket['resolution'], height=80)
                
                col1, col2 = st.columns(2)
                with col1:
                    estimated_hours = st.number_input("Estimated Hours", value=float(ticket['estimated_hours']), min_value=0.0, step=0.5)
                with col2:
                    actual_hours = st.number_input("Actual Hours", value=float(ticket['actual_hours']), min_value=0.0, step=0.5)
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("Update Ticket", use_container_width=True)
                with col2:
                    cancelled = st.form_submit_button("Cancel", use_container_width=True)
                
                if submitted:
                    ticket_data = {
                        'title': title,
                        'description': description,
                        'priority': priority,
                        'status': status,
                        'assigned_to': assigned_to,
                        'category': category,
                        'subcategory': subcategory,
                        'tags': tags,
                        'estimated_hours': estimated_hours,
                        'actual_hours': actual_hours,
                        'resolution': resolution
                    }
                    
                    if ticket_service.update_ticket(ticket_id, ticket_data, st.session_state.user['full_name']):
                        st.success("✅ Ticket updated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update ticket")
                
                if cancelled:
                    st.session_state.page = 'tickets'
                    st.rerun()


def show_create_ticket_page():
    if not require_auth():
        return
    
    st.title("➕ Create New Ticket")
    
    companies = user_service.get_companies()
    company_options = {comp['company_name']: comp['company_id'] for comp in companies}
    
    with st.form("create_ticket_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Ticket Title*", placeholder="Enter a descriptive title")
            priority = st.selectbox("Priority*", ["Low", "Medium", "High", "Critical"])
            category = st.selectbox("Category*", ["General", "Bug", "Enhancement", "Security", "Performance", "Integration", "Maintenance"])
            company_name = st.selectbox("Company*", list(company_options.keys()))
        
        with col2:
            status = st.selectbox("Status*", ["Open", "In Progress"])
            subcategory = st.text_input("Subcategory", placeholder="Optional subcategory")
            assigned_to = st.text_input("Assign To", placeholder="Leave blank for unassigned")
            tags = st.text_input("Tags", placeholder="Comma-separated tags")
        
        description = st.text_area("Description*", placeholder="Detailed description of the issue", height=150)
        
        submitted = st.form_submit_button("Create Ticket", use_container_width=True)
        
        if submitted:
            if title and description and company_name:
                ticket_data = {
                    'title': title,
                    'description': description,
                    'priority': priority,
                    'status': status,
                    'category': category,
                    'subcategory': subcategory,
                    'assigned_to': assigned_to,
                    'tags': tags,
                    'company_id': company_options[company_name]
                }
                
                if ticket_service.create_ticket(ticket_data, st.session_state.user['full_name']):
                    st.success("✅ Ticket created successfully!")
                    st.balloons()
                    st.session_state.ticket_created = True
                else:
                    st.error("❌ Failed to create ticket. Please try again.")
            else:
                st.error("❌ Please fill in all required fields (marked with *)")
            
    if st.session_state.get('ticket_created', False):
        if st.button("🏠 Go to Dashboard", use_container_width=True):
            st.session_state.page = 'dashboard'
            st.session_state.ticket_created = False
            st.rerun()


def show_users_page():
    if not require_auth('can_create_users'):
        return
    
    st.title("👥 User Management")
    
    tab1, tab2 = st.tabs(["📋 All Users", "➕ Add New User"])
    
    with tab1:
        users = user_service.get_all_users(include_inactive=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            role_filter = st.selectbox("Filter by Role", ["All", "Admin", "Manager", "Agent", "User"])
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
        with col3:
            company_filter = st.selectbox("Filter by Company", ["All"] + list(set([u['company_id'] for u in users])))
        
        filtered_users = users
        if role_filter != "All":
            filtered_users = [u for u in filtered_users if u['role'] == role_filter]
        if status_filter == "Active":
            filtered_users = [u for u in filtered_users if u['is_active']]
        elif status_filter == "Inactive":
            filtered_users = [u for u in filtered_users if not u['is_active']]
        if company_filter != "All":
            filtered_users = [u for u in filtered_users if u['company_id'] == company_filter]
        
        st.subheader(f"Showing {len(filtered_users)} of {len(users)} users")
        
        for user in filtered_users:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"#### {user['full_name']} (@{user['username']})")
                with col2:
                    role_badge = f'<span class="user-role-{user["role"].lower()}">{user["role"]}</span>'
                    if user['is_active']:
                        status_badge = '<span style="background: #059669; color: white; padding: 0.25rem 0.5rem; border-radius: 0.5rem; font-size: 0.7rem;">ACTIVE</span>'
                    else:
                        status_badge = '<span style="background: #dc2626; color: white; padding: 0.25rem 0.5rem; border-radius: 0.5rem; font-size: 0.7rem;">INACTIVE</span>'
                    st.markdown(f"{role_badge} {status_badge}", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Email:** {user['email']}")
                    st.write(f"**Phone:** {user.get('phone', 'N/A')}")
                with col2:
                    st.write(f"**Department:** {user['department']}")
                    st.write(f"**Company:** {user['company_id']}")
                with col3:
                    st.write(f"**Created:** {format_date(user['created_date'])}")
                    last_login = format_date(user['last_login_date']) if user['last_login_date'] else 'Never'
                    st.write(f"**Last Login:** {last_login}")
                
                st.write("**Permissions:**")
                permissions = []
                if user['permissions']['can_create_users']:
                    permissions.append("Create Users")
                if user['permissions']['can_deactivate_users']:
                    permissions.append("Deactivate Users")
                if user['permissions']['can_reset_passwords']:
                    permissions.append("Reset Passwords")
                if user['permissions']['can_manage_tickets']:
                    permissions.append("Manage Tickets")
                if user['permissions']['can_view_all_tickets']:
                    permissions.append("View All Tickets")
                if user['permissions']['can_delete_tickets']:
                    permissions.append("Delete Tickets")
                if user['permissions']['can_export_data']:
                    permissions.append("Export Data")
                
                if permissions:
                    permission_badges = []
                    for perm in permissions:
                        permission_badges.append(f'<span style="background: #3b82f6; color: white; padding: 0.15rem 0.4rem; border-radius: 0.3rem; font-size: 0.7rem; margin-right: 0.25rem;">{perm}</span>')
                    st.markdown(" ".join(permission_badges), unsafe_allow_html=True)
                else:
                    st.write("*No special permissions*")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"✏️ Edit", key=f"edit_{user['id']}"):
                        st.session_state.edit_user_id = user['id']
                        st.session_state.page = 'edit_user'
                        st.rerun()
                
                with col2:
                    if user['is_active']:
                        if st.button(f"🚫 Deactivate", key=f"deactivate_{user['id']}"):
                            success, message = user_management_service.deactivate_user(user['id'])
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    else:
                        if st.button(f"✅ Activate", key=f"activate_{user['id']}"):
                            success, message = user_management_service.activate_user(user['id'])
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                
                with col3:
                    if st.button(f"🔑 Reset Password", key=f"reset_{user['id']}"):
                        st.session_state.reset_user_id = user['id']
                
                if st.session_state.get('reset_user_id') == user['id']:
                    new_password = st.text_input("New Password", type="password", key=f"new_pwd_{user['id']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Confirm Reset", key=f"confirm_reset_{user['id']}"):
                            if new_password:
                                success, message = user_management_service.reset_password(user['id'], new_password)
                                if success:
                                    st.success(message)
                                    st.session_state.reset_user_id = None
                                    st.rerun()
                                else:
                                    st.error(message)
                            else:
                                st.error("Please enter a new password")
                    with col2:
                        if st.button("Cancel", key=f"cancel_reset_{user['id']}"):
                            st.session_state.reset_user_id = None
                            st.rerun()
                
                st.markdown("---")
    
    with tab2:
        st.subheader("Create New User")
        
        companies = user_service.get_companies()
        company_options = {comp['company_name']: comp['company_id'] for comp in companies}
        
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username*", placeholder="Enter username")
                email = st.text_input("Email*", placeholder="Enter email address")
                first_name = st.text_input("First Name*", placeholder="Enter first name")
                last_name = st.text_input("Last Name*", placeholder="Enter last name")
                password = st.text_input("Password*", type="password", placeholder="Enter password")
            
            with col2:
                role = st.selectbox("Role*", ["User", "Agent", "Manager", "Admin"])
                department = st.text_input("Department", placeholder="Enter department")
                phone = st.text_input("Phone", placeholder="Enter phone number")
                company_name = st.selectbox("Company*", list(company_options.keys()))
            
                        # Auto-populate permissions based on role
            if role == "Admin":
                default_permissions = {
                    'can_create_users': True, 'can_deactivate_users': True,
                    'can_reset_passwords': True, 'can_manage_tickets': True,
                    'can_view_all_tickets': True, 'can_delete_tickets': True,
                    'can_export_data': True
                }
            elif role == "Manager":
                default_permissions = {
                    'can_create_users': False, 'can_deactivate_users': False,
                    'can_reset_passwords': True, 'can_manage_tickets': True,
                    'can_view_all_tickets': True, 'can_delete_tickets': False,
                    'can_export_data': True
                }
            elif role == "Agent":
                default_permissions = {
                    'can_create_users': False, 'can_deactivate_users': False,
                    'can_reset_passwords': False, 'can_manage_tickets': True,
                    'can_view_all_tickets': False, 'can_delete_tickets': False,
                    'can_export_data': False
                }
            else:  # User
                default_permissions = {
                    'can_create_users': False, 'can_deactivate_users': False,
                    'can_reset_passwords': False, 'can_manage_tickets': False,
                    'can_view_all_tickets': False, 'can_delete_tickets': False,
                    'can_export_data': False
                }
            st.subheader("Permissions")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                can_create_users = st.checkbox("Create Users", value=default_permissions['can_create_users'])
                can_deactivate_users = st.checkbox("Deactivate Users", value=default_permissions['can_deactivate_users'])

            with col2:
                can_reset_passwords = st.checkbox("Reset Passwords", value=default_permissions['can_reset_passwords'])
                can_manage_tickets = st.checkbox("Manage Tickets", value=default_permissions['can_manage_tickets'])

            with col3:
                can_view_all_tickets = st.checkbox("View All Tickets", value=default_permissions['can_view_all_tickets'])
                can_delete_tickets = st.checkbox("Delete Tickets", value=default_permissions['can_delete_tickets'])

            with col4:
                can_export_data = st.checkbox("Export Data", value=default_permissions['can_export_data'])
            
            submitted = st.form_submit_button("Create User", use_container_width=True)
            
            if submitted:
                if username and email and first_name and last_name and password and company_name:
                    user_data = {
                        'username': username,
                        'email': email,
                        'password': password,
                        'first_name': first_name,
                        'last_name': last_name,
                        'role': role,
                        'department': department,
                        'phone': phone,
                        'company_id': company_options[company_name],
                        'can_create_users': can_create_users,
                        'can_deactivate_users': can_deactivate_users,
                        'can_reset_passwords': can_reset_passwords,
                        'can_manage_tickets': can_manage_tickets,
                        'can_view_all_tickets': can_view_all_tickets,
                        'can_delete_tickets': can_delete_tickets,
                        'can_export_data': can_export_data
                    }
                    
                    success, message = user_management_service.create_user(user_data, st.session_state.user['full_name'])
                    if success:
                        st.success("✅ User created successfully!")
                        st.balloons()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("❌ Please fill in all required fields (marked with *)")


def show_edit_user_page():
    if not require_auth('can_create_users'):
        return
    
    st.title("✏️ Edit User")
    
    users = user_service.get_all_users(include_inactive=True)
    user_to_edit = next((u for u in users if u['id'] == st.session_state.get('edit_user_id')), None)
    
    if not user_to_edit:
        st.error("User not found")
        if st.button("Back to Users"):
            st.session_state.page = 'users'
            st.rerun()
        return
    
    st.subheader(f"Editing: {user_to_edit['full_name']}")
    
    companies = user_service.get_companies()
    company_options = {comp['company_name']: comp['company_id'] for comp in companies}
    current_company_name = next((name for name, id in company_options.items() if id == user_to_edit['company_id']), list(company_options.keys())[0])
    
    with st.form("edit_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name*", value=user_to_edit['first_name'])
            last_name = st.text_input("Last Name*", value=user_to_edit['last_name'])
            role = st.selectbox("Role*", ["User", "Agent", "Manager", "Admin"], index=["User", "Agent", "Manager", "Admin"].index(user_to_edit['role']))
            department = st.text_input("Department", value=user_to_edit['department'])
        
        with col2:
            phone = st.text_input("Phone", value=user_to_edit.get('phone', ''))
            company_name = st.selectbox("Company*", list(company_options.keys()), index=list(company_options.keys()).index(current_company_name))
        
        st.subheader("Permissions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            can_create_users = st.checkbox("Create Users", value=user_to_edit['permissions']['can_create_users'])
            can_deactivate_users = st.checkbox("Deactivate Users", value=user_to_edit['permissions']['can_deactivate_users'])
        
        with col2:
            can_reset_passwords = st.checkbox("Reset Passwords", value=user_to_edit['permissions']['can_reset_passwords'])
            can_manage_tickets = st.checkbox("Manage Tickets", value=user_to_edit['permissions']['can_manage_tickets'])
        
        with col3:
            can_view_all_tickets = st.checkbox("View All Tickets", value=user_to_edit['permissions']['can_view_all_tickets'])
            can_delete_tickets = st.checkbox("Delete Tickets", value=user_to_edit['permissions']['can_delete_tickets'])
        
        with col4:
            can_export_data = st.checkbox("Export Data", value=user_to_edit['permissions']['can_export_data'])
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Update User", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)
        
        if submitted:
            if first_name and last_name and company_name:
                user_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': role,
                    'department': department,
                    'phone': phone,
                    'company_id': company_options[company_name],
                    'can_create_users': can_create_users,
                    'can_deactivate_users': can_deactivate_users,
                    'can_reset_passwords': can_reset_passwords,
                    'can_manage_tickets': can_manage_tickets,
                    'can_view_all_tickets': can_view_all_tickets,
                    'can_delete_tickets': can_delete_tickets,
                    'can_export_data': can_export_data
                }
                
                success, message = user_management_service.update_user(user_to_edit['id'], user_data)
                if success:
                    st.success("✅ User updated successfully!")
                    st.session_state.page = 'users'
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.error("❌ Please fill in all required fields")
        
        if cancelled:
            st.session_state.page = 'users'
            st.rerun()


def show_analytics_page():
    if not require_auth('can_view_all_tickets'):
        return
    
    st.title("📊 Analytics & Reports")
    
    tickets = ticket_service.get_all_tickets(st.session_state.user['id'], 
                                           st.session_state.user['permissions'], 
                                           st.session_state.user['full_name'])
    
    if not tickets:
        st.info("No tickets available for analysis.")
        return
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(tickets)
    
    # Time-based filters
    col1, col2 = st.columns(2)
    with col1:
        days_back = st.selectbox("Time Period", [7, 14, 30, 60, 90, 365], index=2)
    with col2:
        cutoff_date = datetime.now() - timedelta(days=days_back)
        df_filtered = df[pd.to_datetime(df['created_date']) >= cutoff_date]
        st.metric("Tickets in Period", len(df_filtered))
    
    # Key Metrics
    st.subheader("📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_resolution_time = "N/A"  # Would need resolution timestamps
        st.metric("Avg Resolution Time", avg_resolution_time)
    
    with col2:
        overdue_count = len([t for t in tickets if t['is_overdue']])
        st.metric("Overdue Tickets", overdue_count)
    
    with col3:
        high_priority = len(df[df['priority'].isin(['Critical', 'High'])])
        st.metric("High Priority Tickets", high_priority)
    
    with col4:
        resolution_rate = len(df[df['status'] == 'Resolved']) / len(df) * 100 if len(df) > 0 else 0
        st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Tickets by Category")
        category_data = df['category'].value_counts()
        fig = px.bar(
            x=category_data.values,
            y=category_data.index,
            orientation='h',
            title="Ticket Distribution by Category"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("👥 Tickets by Assignee")
        assignee_data = df['assigned_to'].value_counts().head(10)
        fig = px.pie(
            values=assignee_data.values,
            names=assignee_data.index,
            title="Top 10 Assignees"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Time series analysis
    st.subheader("📈 Ticket Creation Trends")
    df['created_date'] = pd.to_datetime(df['created_date'])
    df['date'] = df['created_date'].dt.date
    daily_tickets = df.groupby('date').size().reset_index(name='count')
    
    fig = px.line(
        daily_tickets, 
        x='date', 
        y='count',
        title="Daily Ticket Creation"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Company analysis
    st.subheader("🏢 Tickets by Company")
    company_data = df['company_id'].value_counts()
    
    # Get company names
    companies = user_service.get_companies()
    company_map = {comp['company_id']: comp['company_name'] for comp in companies}
    
    company_names = [company_map.get(comp_id, comp_id) for comp_id in company_data.index]
    
    fig = px.bar(
        x=company_data.values,
        y=company_names,
        orientation='h',
        title="Tickets by Company"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def show_sidebar():
    with st.sidebar:
        st.markdown('<div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); border-radius: 0.5rem; color: white; margin-bottom: 1rem;"><h2>🎫 FlowTLS SYNC+</h2><p>Professional Edition</p></div>', unsafe_allow_html=True)
        
        if st.session_state.user:
            user = st.session_state.user
            st.markdown(f'''
            <div style="text-align: center; margin-bottom: 1rem;">
                <strong>{user["full_name"]}</strong><br>
                <span class="user-role-{user["role"].lower()}">{user["role"]}</span><br>
                <small>{user["department"]}</small>
            </div>
            ''', unsafe_allow_html=True)
            
            st.markdown("---")
            
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.page = 'dashboard'
                st.rerun()
            
            if st.button("🎫 Tickets", use_container_width=True):
                st.session_state.page = 'tickets'
                st.rerun()
            
            if st.button("➕ Create Ticket", use_container_width=True):
                st.session_state.page = 'create_ticket'
                st.rerun()
            
            if user['permissions'].get('can_view_all_tickets', False):
                if st.button("📈 Analytics", use_container_width=True):
                    st.session_state.page = 'analytics'
                    st.rerun()
            
            if user['permissions'].get('can_create_users', False):
                if st.button("👥 Users", use_container_width=True):
                    st.session_state.page = 'users'
                    st.rerun()
            
            st.markdown("---")
            
            # Show currently viewing ticket if applicable
            if st.session_state.selected_ticket_id and st.session_state.page == 'ticket_detail':
                st.markdown("**Currently Viewing:**")
                ticket = ticket_service.get_ticket_by_id(st.session_state.selected_ticket_id)
                if ticket:
                    st.markdown(f"🎫 #{ticket['id']}")
                    st.markdown(f"**{ticket['title'][:30]}{'...' if len(ticket['title']) > 30 else ''}**")
                    st.markdown(f'<span class="priority-{ticket["priority"].lower()}">{ticket["priority"]}</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="status-{ticket["status"].lower().replace(" ", "-")}">{ticket["status"]}</span>', unsafe_allow_html=True)
                    
                    if st.button("📋 Back to Tickets", use_container_width=True):
                        st.session_state.page = 'tickets'
                        st.session_state.selected_ticket_id = None
                        st.rerun()
                st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.page = 'login'
                st.session_state.selected_ticket_id = None
                st.rerun()


def main():
    try:
        if st.session_state.user:
            show_sidebar()
        
        if st.session_state.page == 'login':
            show_login_page()
        elif st.session_state.page == 'dashboard':
            show_dashboard()
        elif st.session_state.page == 'tickets':
            show_tickets_page()
        elif st.session_state.page == 'filtered_tickets':
            show_filtered_tickets_page()      
        elif st.session_state.page == 'ticket_detail':
            show_ticket_detail_page()
        elif st.session_state.page == 'create_ticket':
            show_create_ticket_page()
        elif st.session_state.page == 'users':
            show_users_page()
        elif st.session_state.page == 'edit_user':
            show_edit_user_page()
        elif st.session_state.page == 'analytics':
            show_analytics_page()
        else:
            st.session_state.page = 'login'
            st.rerun()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please refresh the page to continue.")


if __name__ == "__main__":
    main()        
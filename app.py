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
from typing import Dict, List, Optional, Tuple

# Configure page
st.set_page_config(
    page_title="FlowTLS SYNC+ Professional",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for professional styling
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
    
    .ticket-card {
        border: 1px solid #e5e7eb;
        border-radius: 0.75rem;
        padding: 1.25rem;
        margin: 0.75rem 0;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        color: #1f2937;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    
    .ticket-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border-color: #3b82f6;
    }
    
    .ticket-card h4 {
        color: #1f2937 !important;
        margin: 0 0 0.75rem 0;
        font-weight: 600;
    }
    
    .ticket-card p {
        color: #4b5563 !important;
        margin: 0.5rem 0 1rem 0;
        line-height: 1.5;
    }
    
    .priority-critical {
        background: linear-gradient(135deg, #dc2626, #ef4444);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .priority-high {
        background: linear-gradient(135deg, #ea580c, #f59e0b);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .priority-medium {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .priority-low {
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-open {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .status-in-progress {
        background: linear-gradient(135deg, #7c3aed, #8b5cf6);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .status-resolved {
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .status-closed {
        background: linear-gradient(135deg, #4b5563, #6b7280);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .overdue {
        border-left: 4px solid #dc2626;
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        color: #1f2937 !important;
    }
    
    .overdue h4 {
        color: #dc2626 !important;
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
        background: linear-gradient(135deg, #1e40af, #3b82f6);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .user-role-agent {
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .user-role-user {
        background: linear-gradient(135deg, #4b5563, #6b7280);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .comment-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.75rem 0;
        border-left: 4px solid #3b82f6;
    }
    
    .comment-internal {
        border-left-color: #f59e0b;
        background: #fffbeb;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Simple but Professional Database Manager
class DatabaseManager:
    def __init__(self, db_path="flowtls_professional.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Simple, reliable schema
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
                is_active INTEGER DEFAULT 1,
                created_date TEXT NOT NULL,
                last_login_date TEXT
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
                actual_hours REAL DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS ticket_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                comment TEXT NOT NULL,
                is_internal INTEGER DEFAULT 0,
                created_date TEXT NOT NULL,
                FOREIGN KEY (ticket_id) REFERENCES tickets (id)
            );
        """)
        
        # Create default users if none exist
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            self.create_default_users()
        
        # Add sample tickets if none exist
        cursor.execute("SELECT COUNT(*) FROM tickets")
        if cursor.fetchone()[0] == 0:
            self.create_sample_tickets()
        
        conn.commit()
        conn.close()
    
    def create_default_users(self):
        users = [
            ("admin", "admin@flowtls.com", "admin123", "System", "Administrator", "Admin", "IT", "+1-555-0001"),
            ("jsmith", "john.smith@flowtls.com", "password123", "John", "Smith", "Manager", "Support", "+1-555-0002"),
            ("achen", "alice.chen@flowtls.com", "password123", "Alice", "Chen", "Agent", "Technical", "+1-555-0003"),
            ("sjohnson", "sarah.johnson@flowtls.com", "password123", "Sarah", "Johnson", "User", "Operations", "+1-555-0005"),
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for username, email, password, first_name, last_name, role, department, phone in users:
            salt = secrets.token_hex(32)
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, salt, first_name, last_name, 
                                 role, department, phone, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (username, email, password_hash, salt, first_name, last_name, role, 
                  department, phone, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def create_sample_tickets(self):
        sample_tickets = [
            ("FlowTLS Integration Critical Error", "System integration completely failing - production down", "Critical", "Open", "John Smith", "Integration", "System Integration", "Sarah Johnson", "urgent,integration,flowtls,production"),
            ("User Authentication SSO Issues", "Multiple users unable to login with SSO affecting entire department", "High", "In Progress", "Alice Chen", "Security", "Authentication", "System Administrator", "sso,login,authentication,department"),
            ("Database Performance Degradation", "Customer reports taking 30+ seconds to load, needs immediate optimization", "High", "Open", "Alice Chen", "Performance", "Database", "John Smith", "performance,database,reports,slow"),
            ("UI Modernization Project", "Update interface design to match new corporate brand guidelines", "Medium", "Open", "Alice Chen", "Enhancement", "User Interface", "Sarah Johnson", "ui,enhancement,design,branding"),
            ("Email Notification System", "Configure automated email alerts for high priority tickets", "Medium", "Resolved", "John Smith", "Configuration", "Email System", "System Administrator", "email,notifications,alerts"),
            ("Mobile App Critical Crash", "iOS application crashes when accessing ticket details - affects mobile users", "Critical", "In Progress", "Alice Chen", "Bug", "Mobile Application", "Alice Chen", "mobile,ios,crash,critical"),
            ("API Rate Limiting Implementation", "Implement comprehensive rate limiting for all public API endpoints", "Medium", "Open", "Alice Chen", "Security", "API Development", "System Administrator", "api,security,rate-limit,public"),
            ("Customer Data Export Feature", "Add secure ability to export customer data in multiple formats", "Low", "Resolved", "Alice Chen", "Feature Request", "Data Export", "Sarah Johnson", "export,csv,pdf,excel,feature"),
            ("Production Server Monitoring", "Set up comprehensive monitoring and alerting for all production infrastructure", "High", "Open", "John Smith", "Infrastructure", "Server Management", "System Administrator", "monitoring,servers,production,alerts"),
            ("Security Policy Update", "Update password requirements and implement 2FA to meet compliance standards", "Medium", "Closed", "Alice Chen", "Security", "Policy Management", "System Administrator", "password,policy,security,2fa,compliance"),
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for i, (title, desc, priority, status, assigned_to, category, subcategory, reporter, tags) in enumerate(sample_tickets):
            # Calculate due dates based on priority
            hours_to_add = {"Critical": 4, "High": 8, "Medium": 24, "Low": 72}[priority]
            due_date = datetime.now() + timedelta(hours=hours_to_add)
            
            # Some tickets should be overdue for demonstration
            if i % 4 == 0 and status in ["Open", "In Progress"]:
                due_date = datetime.now() - timedelta(hours=2)
            
            cursor.execute("""
                INSERT INTO tickets (title, description, priority, status, assigned_to, category, 
                                   subcategory, created_date, due_date, reporter, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, desc, priority, status, assigned_to, category, subcategory, 
                  (datetime.now() - timedelta(days=i)).isoformat(), due_date.isoformat(), reporter, tags))
        
        conn.commit()
        conn.close()

# Simple Authentication Service
class AuthService:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def hash_password(self, password: str, salt: str) -> str:
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def verify_password(self, password: str, hash_value: str, salt: str) -> bool:
        return self.hash_password(password, salt) == hash_value
    
    def login(self, username: str, password: str) -> Tuple[bool, Optional[Dict], str]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, password_hash, salt, first_name, last_name, role,
                   department, is_active
            FROM users WHERE username = ? AND is_active = 1
        """, (username,))
        
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return False, None, "Invalid username or password"
        
        if not self.verify_password(password, user[3], user[4]):
            conn.close()
            return False, None, "Invalid username or password"
        
        # Update last login
        cursor.execute("""
            UPDATE users SET last_login_date = ? WHERE id = ?
        """, (datetime.now().isoformat(), user[0]))
        
        user_data = {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'first_name': user[5],
            'last_name': user[6],
            'full_name': f"{user[5]} {user[6]}".strip(),
            'role': user[7],
            'department': user[8],
            'permissions': self.get_user_permissions(user[7])
        }
        
        conn.commit()
        conn.close()
        
        return True, user_data, ""
    
    def get_user_permissions(self, role: str) -> Dict[str, bool]:
        """Define role-based permissions"""
        permissions = {
            'Admin': {
                'create_tickets': True,
                'edit_all_tickets': True,
                'delete_tickets': True,
                'view_all_tickets': True,
                'manage_users': True,
                'view_internal_comments': True,
                'bulk_operations': True,
                'export_data': True,
            },
            'Manager': {
                'create_tickets': True,
                'edit_all_tickets': True,
                'delete_tickets': False,
                'view_all_tickets': True,
                'manage_users': False,
                'view_internal_comments': True,
                'bulk_operations': True,
                'export_data': True,
            },
            'Agent': {
                'create_tickets': True,
                'edit_all_tickets': False,
                'delete_tickets': False,
                'view_all_tickets': True,
                'manage_users': False,
                'view_internal_comments': True,
                'bulk_operations': False,
                'export_data': False,
            },
            'User': {
                'create_tickets': True,
                'edit_all_tickets': False,
                'delete_tickets': False,
                'view_all_tickets': False,
                'manage_users': False,
                'view_internal_comments': False,
                'bulk_operations': False,
                'export_data': False,
            }
        }
        
        return permissions.get(role, permissions['User'])

# Professional Ticket Service
class TicketService:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_all_tickets(self, user_id: int, role: str, user_name: str) -> List[Dict]:
        """Get tickets based on user permissions"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if role in ['Admin', 'Manager', 'Agent']:
            # Can see all tickets
            cursor.execute("""
                SELECT id, title, description, priority, status, assigned_to, category, subcategory,
                       created_date, updated_date, due_date, reporter, resolution, tags,
                       estimated_hours, actual_hours
                FROM tickets ORDER BY created_date DESC
            """)
        else:
            # Users can only see tickets they created or are assigned to
            cursor.execute("""
                SELECT id, title, description, priority, status, assigned_to, category, subcategory,
                       created_date, updated_date, due_date, reporter, resolution, tags,
                       estimated_hours, actual_hours
                FROM tickets 
                WHERE reporter = ? OR assigned_to = ?
                ORDER BY created_date DESC
            """, (user_name, user_name))
        
        tickets = []
        for row in cursor.fetchall():
            ticket = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'priority': row[3],
                'status': row[4],
                'assigned_to': row[5] or 'Unassigned',
                'category': row[6],
                'subcategory': row[7],
                'created_date': row[8],
                'updated_date': row[9],
                'due_date': row[10],
                'reporter': row[11] or 'Unknown',
                'resolution': row[12],
                'tags': row[13],
                'estimated_hours': row[14],
                'actual_hours': row[15],
                'is_overdue': self.is_ticket_overdue(row[10], row[4])
            }
            tickets.append(ticket)
        
        conn.close()
        return tickets
    
    def is_ticket_overdue(self, due_date: str, status: str) -> bool:
        """Check if ticket is overdue"""
        if not due_date or status in ['Resolved', 'Closed']:
            return False
        try:
            due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            return due < datetime.now()
        except:
            return False
    
    def create_ticket(self, ticket_data: Dict, user_name: str) -> int:
        """Create a new ticket"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Calculate due date based on priority
        hours_map = {'Critical': 4, 'High': 8, 'Medium': 24, 'Low': 72}
        hours = hours_map.get(ticket_data['priority'], 24)
        due_date = datetime.now() + timedelta(hours=hours)
        
        cursor.execute("""
            INSERT INTO tickets (title, description, priority, status, assigned_to, category, 
                               subcategory, created_date, due_date, reporter, tags, estimated_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket_data['title'],
            ticket_data['description'],
            ticket_data['priority'],
            ticket_data['status'],
            ticket_data.get('assigned_to', ''),
            ticket_data['category'],
            ticket_data.get('subcategory', ''),
            datetime.now().isoformat(),
            due_date.isoformat(),
            user_name,
            ticket_data.get('tags', ''),
            ticket_data.get('estimated_hours', 0)
        ))
        
        ticket_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return ticket_id
    
    def update_ticket(self, ticket_id: int, ticket_data: Dict) -> bool:
        """Update a ticket"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE tickets SET title=?, description=?, priority=?, status=?, assigned_to=?, 
                                 category=?, subcategory=?, updated_date=?, resolution=?, tags=?,
                                 estimated_hours=?, actual_hours=?
                WHERE id=?
            """, (
                ticket_data['title'],
                ticket_data['description'],
                ticket_data['priority'],
                ticket_data['status'],
                ticket_data.get('assigned_to', ''),
                ticket_data['category'],
                ticket_data.get('subcategory', ''),
                datetime.now().isoformat(),
                ticket_data.get('resolution', ''),
                ticket_data.get('tags', ''),
                ticket_data.get('estimated_hours', 0),
                ticket_data.get('actual_hours', 0),
                ticket_id
            ))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def add_comment(self, ticket_id: int, user_name: str, comment: str, is_internal: bool = False) -> bool:
        """Add comment to ticket"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ticket_comments (ticket_id, user_name, comment, is_internal, created_date)
                VALUES (?, ?, ?, ?, ?)
            """, (ticket_id, user_name, comment, int(is_internal), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_ticket_comments(self, ticket_id: int, can_view_internal: bool = False) -> List[Dict]:
        """Get comments for a ticket"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if can_view_internal:
            cursor.execute("""
                SELECT user_name, comment, is_internal, created_date
                FROM ticket_comments WHERE ticket_id = ?
                ORDER BY created_date ASC
            """, (ticket_id,))
        else:
            cursor.execute("""
                SELECT user_name, comment, is_internal, created_date
                FROM ticket_comments WHERE ticket_id = ? AND is_internal = 0
                ORDER BY created_date ASC
            """, (ticket_id,))
        
        comments = []
        for row in cursor.fetchall():
            comment = {
                'user_name': row[0],
                'comment': row[1],
                'is_internal': bool(row[2]),
                'created_date': row[3]
            }
            comments.append(comment)
        
        conn.close()
        return comments
    
    def get_ticket_statistics(self, user_id: int, role: str, user_name: str) -> Dict:
        """Get ticket statistics based on user role"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if role in ['Admin', 'Manager', 'Agent']:
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM tickets 
                WHERE status != 'Deleted' 
                GROUP BY status
            """)
        else:
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM tickets 
                WHERE (reporter = ? OR assigned_to = ?) AND status != 'Deleted'
                GROUP BY status
            """, (user_name, user_name))
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = row[1]
        
        # Add overdue count for managers/admins
        if role in ['Admin', 'Manager']:
            cursor.execute("""
                SELECT COUNT(*) FROM tickets 
                WHERE due_date < ? AND status NOT IN ('Resolved', 'Closed', 'Deleted')
            """, (datetime.now().isoformat(),))
            stats['Overdue'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def search_tickets(self, search_term: str, user_id: int, role: str, user_name: str) -> List[Dict]:
        """Search tickets"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if role in ['Admin', 'Manager', 'Agent']:
            cursor.execute("""
                SELECT id, title, description, priority, status, assigned_to, category, subcategory,
                       created_date, updated_date, due_date, reporter, resolution, tags,
                       estimated_hours, actual_hours
                FROM tickets 
                WHERE (title LIKE ? OR description LIKE ? OR tags LIKE ?)
                ORDER BY created_date DESC
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        else:
            cursor.execute("""
                SELECT id, title, description, priority, status, assigned_to, category, subcategory,
                       created_date, updated_date, due_date, reporter, resolution, tags,
                       estimated_hours, actual_hours
                FROM tickets 
                WHERE (reporter = ? OR assigned_to = ?) 
                AND (title LIKE ? OR description LIKE ? OR tags LIKE ?)
                ORDER BY created_date DESC
            """, (user_name, user_name, f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        
        tickets = []
        for row in cursor.fetchall():
            ticket = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'priority': row[3],
                'status': row[4],
                'assigned_to': row[5] or 'Unassigned',
                'category': row[6],
                'subcategory': row[7],
                'created_date': row[8],
                'updated_date': row[9],
                'due_date': row[10],
                'reporter': row[11] or 'Unknown',
                'resolution': row[12],
                'tags': row[13],
                'estimated_hours': row[14],
                'actual_hours': row[15],
                'is_overdue': self.is_ticket_overdue(row[10], row[4])
            }
            tickets.append(ticket)
        
        conn.close()
        return tickets

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
def require_auth(permission: str = None) -> bool:
    if not st.session_state.user:
        st.session_state.page = 'login'
        return False
    
    if permission and not st.session_state.user.get('permissions', {}).get(permission, False):
        st.error(f"⚠️ Access Denied: You don't have permission to {permission.replace('_', ' ')}")
        return False
    
    return True

# Utility functions
def get_priority_color(priority: str) -> str:
    colors = {
        'Critical': '#dc2626',
        'High': '#ea580c',
        'Medium': '#2563eb',
        'Low': '#059669'
    }
    return colors.get(priority, '#6b7280')

def get_status_color(status: str) -> str:
    colors = {
        'Open': '#2563eb',
        'In Progress': '#7c3aed',
        'Resolved': '#059669',
        'Closed': '#4b5563',
        'Deleted': '#dc2626',
        'On Hold': '#ea580c'
    }
    return colors.get(status, '#6b7280')

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

# Enhanced Login Page
def show_login_page():
    st.markdown("""
        <div class="main-header">
            <h1>🎫 FlowTLS SYNC+ Professional</h1>
            <p>Enterprise Ticketing & Service Management Platform</p>
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
                    success, user, error_msg = auth_service.login(username, password)
                    if success:
                        st.session_state.user = user
                        st.session_state.page = 'dashboard'
                        st.rerun()
                    else:
                        st.error(error_msg)
                else:
                    st.error("Please enter both username and password")
        
        with st.expander("🎭 Demo User Accounts", expanded=True):
            st.markdown("""
            **Administrator:** `admin` / `admin123`  
            **Manager:** `jsmith` / `password123`  
            **Agent:** `achen` / `password123`  
            **User:** `sjohnson` / `password123`  
            
            *Each role has different permissions and access levels*
            """)

# Enhanced Dashboard
def show_dashboard():
    if not require_auth():
        return
    
    user = st.session_state.user
    user_name = user['full_name']
    
    # Header with user info
    st.markdown(f"""
        <div class="main-header">
            <h1>🎫 FlowTLS SYNC+ Dashboard</h1>
            <p>Welcome back, {user_name}! | Role: <strong>{user['role']}</strong> | Department: {user['department']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get ticket statistics
    stats = ticket_service.get_ticket_statistics(user['id'], user['role'], user_name)
    total_tickets = sum(stats.values()) if stats else 0
    
    # Enhanced metrics row
    if user['role'] in ['Admin', 'Manager']:
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
            overdue = stats.get('Overdue', 0)
            st.metric("⚠️ Overdue", overdue, delta=f"-{overdue}" if overdue > 0 else None)
    else:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("My Tickets", total_tickets)
        with col2:
            st.metric("Open", stats.get('Open', 0))
        with col3:
            st.metric("In Progress", stats.get('In Progress', 0))
        with col4:
            st.metric("Resolved", stats.get('Resolved', 0))
    
    # Charts and Recent Activity
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if stats:
            # Filter out special metrics for pie chart
            chart_stats = {k: v for k, v in stats.items() if k not in ['Overdue']}
            if chart_stats:
                fig = px.pie(
                    values=list(chart_stats.values()),
                    names=list(chart_stats.keys()),
                    title="Tickets by Status",
                    color_discrete_sequence=['#3b82f6', '#8b5cf6', '#10b981', '#6b7280', '#f59e0b']
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Recent Activity")
        tickets = ticket_service.get_all_tickets(user['id'], user['role'], user_name)[:5]
        
        for ticket in tickets:
            priority_class = f"priority-{ticket['priority'].lower()}"
            status_class = f"status-{ticket['status'].lower().replace(' ', '-')}"
            overdue_indicator = "🔥" if ticket['is_overdue'] else ""
            
            st.markdown(f"""
                <div class="ticket-card">
                    <h4 style="color: #1f2937 !important;">
                        {overdue_indicator} #{ticket['id']} - {ticket['title']}
                    </h4>
                    <p style="color: #4b5563 !important;">
                        {ticket['description'][:80]}...
                    </p>
                    <div>
                        <span class="{priority_class}">{ticket['priority']}</span>
                        <span class="{status_class}">{ticket['status']}</span>
                        <span style="margin-left: 10px; color: #4b5563;">
                            👤 {ticket['assigned_to']}
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    # Quick Actions
    st.subheader("Quick Actions")
    
    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
    
    with quick_col1:
        if st.button("➕ Create Ticket", use_container_width=True):
            st.session_state.page = 'new_ticket'
            st.rerun()
    
    with quick_col2:
        if st.button("🎫 View All Tickets", use_container_width=True):
            st.session_state.page = 'tickets'
            st.rerun()
    
    with quick_col3:
        if st.button("🔍 Search Tickets", use_container_width=True):
            st.session_state.page = 'search'
            st.rerun()
    
    with quick_col4:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.page = 'settings'
            st.rerun()

# Enhanced Tickets Page
def show_tickets_page():
    if not require_auth():
        return
    
    user = st.session_state.user
    user_name = user['full_name']
    
    st.title("🎫 Professional Ticket Management")
    
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
                                   ["All", "Open", "In Progress", "Resolved", "Closed", "On Hold"])
    
    with col5:
        if user['permissions'].get('export_data', False):
            if st.button("📊 Export CSV", use_container_width=True):
                tickets = ticket_service.get_all_tickets(user['id'], user['role'], user_name)
                csv_data = generate_csv_export(tickets)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"flowtls_tickets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    # Get tickets based on search and filter
    if search_term:
        tickets = ticket_service.search_tickets(search_term, user['id'], user['role'], user_name)
    else:
        tickets = ticket_service.get_all_tickets(user['id'], user['role'], user_name)
    
    if filter_status != "All":
        tickets = [t for t in tickets if t['status'] == filter_status]
    
    # Enhanced ticket display
    display_professional_ticket_list(tickets, user)

def display_professional_ticket_list(tickets, user):
    if not tickets:
        st.info("No tickets found.")
        return
    
    for ticket in tickets:
        overdue_class = "overdue" if ticket['is_overdue'] else ""
        priority_class = f"priority-{ticket['priority'].lower()}"
        status_class = f"status-{ticket['status'].lower().replace(' ', '-')}"
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                overdue_indicator = "🔥 " if ticket['is_overdue'] else ""
                
                st.markdown(f"""
                    <div class="ticket-card {overdue_class}">
                        <h4 style="color: #1f2937 !important; margin-bottom: 0.75rem;">
                            {overdue_indicator}#{ticket['id']} - {ticket['title']}
                        </h4>
                        <p style="color: #4b5563 !important; margin-bottom: 0.75rem;">
                            {ticket['description'][:150]}{'...' if len(ticket['description']) > 150 else ''}
                        </p>
                        <div style="margin-bottom: 0.5rem;">
                            <span class="{priority_class}">{ticket['priority']}</span>
                            <span class="{status_class}">{ticket['status']}</span>
                            <span style="margin-left: 10px; color: #4b5563;">📁 {ticket['category']}</span>
                            <span style="margin-left: 10px; color: #4b5563;">👤 {ticket['assigned_to']}</span>
                        </div>
                        <div style="font-size: 0.875rem; color: #6b7280;">
                            <span>📅 Created: {format_date(ticket['created_date'])}</span>
                            <span style="margin-left: 15px;">⏰ Due: {format_date(ticket['due_date'])}</span>
                            <span style="margin-left: 15px;">👨‍💼 Reporter: {ticket['reporter']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("View Details", key=f"view_{ticket['id']}"):
                    st.session_state.selected_ticket = ticket
                    st.session_state.page = 'ticket_details'
                    st.rerun()
                
                if user['permissions'].get('edit_all_tickets', False):
                    if st.button("Edit", key=f"edit_{ticket['id']}"):
                        st.session_state.selected_ticket = ticket
                        st.session_state.page = 'edit_ticket'
                        st.rerun()

# Helper function for CSV export
def generate_csv_export(tickets):
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'ID', 'Title', 'Description', 'Priority', 'Status', 'Assigned To',
        'Category', 'Subcategory', 'Created Date', 'Updated Date', 'Due Date', 
        'Reporter', 'Tags', 'Estimated Hours', 'Actual Hours'
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
            ticket['subcategory'],
            format_date(ticket['created_date']),
            format_date(ticket['updated_date']),
            format_date(ticket['due_date']),
            ticket['reporter'],
            ticket['tags'],
            ticket['estimated_hours'],
            ticket['actual_hours']
        ])
    
    return output.getvalue()

# Sidebar Navigation
def show_sidebar():
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); 
                       border-radius: 0.5rem; color: white; margin-bottom: 1rem;">
                <h2>🎫 FlowTLS SYNC+</h2>
                <p>Professional Edition</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.user:
            user = st.session_state.user
            role_class = f"user-role-{user['role'].lower()}"
            
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 1rem;">
                    <strong>{user['full_name']}</strong><br>
                    <span class="{role_class}">{user['role']}</span><br>
                    <small>{user['department']}</small>
                </div>
            """, unsafe_allow_html=True)
            
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
    else:
        st.session_state.page = 'login'
        st.rerun()

if __name__ == "__main__":
    main()
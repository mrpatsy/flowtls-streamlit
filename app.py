import streamlit as st
import sqlite3
import hashlib
import secrets
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import csv
from io import StringIO, BytesIO
import plotly.express as px
import plotly.graph_objects as go
import re
from typing import Dict, List, Optional, Tuple
import base64

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
        position: relative;
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
    
    .audit-log {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        font-family: 'Courier New', monospace;
        font-size: 0.875rem;
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
    
    .notification-banner {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: #92400e;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        font-weight: 600;
    }
    
    .password-strength {
        height: 4px;
        border-radius: 2px;
        margin-top: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .strength-weak { background: #ef4444; }
    .strength-fair { background: #f59e0b; }
    .strength-good { background: #3b82f6; }
    .strength-strong { background: #10b981; }
</style>
""", unsafe_allow_html=True)

# Enhanced Database Manager with Multi-User Support
class DatabaseManager:
    def __init__(self, db_path="flowtls_professional.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Enhanced tables for professional use
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
                created_date DATETIME NOT NULL,
                last_login_date DATETIME,
                created_by INTEGER,
                password_changed_date DATETIME,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until DATETIME,
                FOREIGN KEY (created_by) REFERENCES users (id)
            );
            
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'Open',
                assigned_to_id INTEGER,
                category TEXT DEFAULT 'General',
                subcategory TEXT DEFAULT '',
                created_date DATETIME NOT NULL,
                updated_date DATETIME,
                due_date DATETIME,
                reporter_id INTEGER,
                resolution TEXT DEFAULT '',
                tags TEXT DEFAULT '',
                sla_breach_date DATETIME,
                estimated_hours REAL,
                actual_hours REAL,
                customer_satisfaction INTEGER,
                attachments TEXT DEFAULT '',
                is_public INTEGER DEFAULT 1,
                FOREIGN KEY (assigned_to_id) REFERENCES users (id),
                FOREIGN KEY (reporter_id) REFERENCES users (id)
            );
            
            CREATE TABLE IF NOT EXISTS ticket_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                comment TEXT NOT NULL,
                is_internal INTEGER DEFAULT 0,
                created_date DATETIME NOT NULL,
                updated_date DATETIME,
                updated_by INTEGER,
                FOREIGN KEY (ticket_id) REFERENCES tickets (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (updated_by) REFERENCES users (id)
            );
            
            CREATE TABLE IF NOT EXISTS ticket_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                field_name TEXT,
                old_value TEXT,
                new_value TEXT,
                description TEXT,
                created_date DATETIME NOT NULL,
                FOREIGN KEY (ticket_id) REFERENCES tickets (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id INTEGER,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_date DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                preference_key TEXT,
                preference_value TEXT,
                category TEXT DEFAULT 'General',
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            
            CREATE TABLE IF NOT EXISTS email_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                template_type TEXT DEFAULT 'notification',
                is_active INTEGER DEFAULT 1,
                created_by INTEGER,
                created_date DATETIME NOT NULL,
                FOREIGN KEY (created_by) REFERENCES users (id)
            );
            
            CREATE TABLE IF NOT EXISTS sla_policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                priority TEXT NOT NULL,
                response_time_hours INTEGER NOT NULL,
                resolution_time_hours INTEGER NOT NULL,
                escalation_time_hours INTEGER,
                is_active INTEGER DEFAULT 1,
                created_date DATETIME NOT NULL
            );
        """)
        
        # Create default admin if none exists
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            self.create_default_users()
        
        # Create default SLA policies
        cursor.execute("SELECT COUNT(*) FROM sla_policies")
        if cursor.fetchone()[0] == 0:
            self.create_default_sla_policies()
        
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
            ("mwilson", "mike.wilson@flowtls.com", "password123", "Mike", "Wilson", "Agent", "Security", "+1-555-0004"),
            ("sjohnson", "sarah.johnson@flowtls.com", "password123", "Sarah", "Johnson", "User", "Operations", "+1-555-0005"),
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for username, email, password, first_name, last_name, role, department, phone in users:
            salt = secrets.token_hex(32)
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, salt, first_name, last_name, 
                                 role, department, phone, created_date, password_changed_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (username, email, password_hash, salt, first_name, last_name, role, 
                  department, phone, datetime.now(), datetime.now()))
        
        conn.commit()
        conn.close()
    
    def create_default_sla_policies(self):
        sla_policies = [
            ("Critical Priority SLA", "Critical", 1, 4, 2),  # 1hr response, 4hr resolution, 2hr escalation
            ("High Priority SLA", "High", 2, 8, 4),          # 2hr response, 8hr resolution, 4hr escalation
            ("Medium Priority SLA", "Medium", 4, 24, 12),    # 4hr response, 24hr resolution, 12hr escalation
            ("Low Priority SLA", "Low", 8, 72, 24),          # 8hr response, 72hr resolution, 24hr escalation
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for name, priority, response_time, resolution_time, escalation_time in sla_policies:
            cursor.execute("""
                INSERT INTO sla_policies (name, priority, response_time_hours, resolution_time_hours, 
                                        escalation_time_hours, created_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, priority, response_time, resolution_time, escalation_time, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def create_sample_tickets(self):
        sample_tickets = [
            ("FlowTLS Integration Critical Error", "System integration completely failing - production down", "Critical", "Open", 1, "Integration", "System Integration", 2, "urgent,integration,flowtls,production"),
            ("User Authentication SSO Issues", "Multiple users unable to login with SSO affecting entire department", "High", "In Progress", 4, "Security", "Authentication", 1, "sso,login,authentication,department"),
            ("Database Performance Degradation", "Customer reports taking 30+ seconds to load, needs immediate optimization", "High", "Open", 3, "Performance", "Database", 2, "performance,database,reports,slow"),
            ("UI Modernization Project", "Update interface design to match new corporate brand guidelines", "Medium", "Open", 3, "Enhancement", "User Interface", 5, "ui,enhancement,design,branding"),
            ("Email Notification System", "Configure automated email alerts for high priority tickets and SLA breaches", "Medium", "Resolved", 2, "Configuration", "Email System", 1, "email,notifications,alerts,sla"),
            ("Mobile App Critical Crash", "iOS application crashes when accessing ticket details - affects 60% of mobile users", "Critical", "In Progress", 3, "Bug", "Mobile Application", 4, "mobile,ios,crash,critical"),
            ("API Rate Limiting Implementation", "Implement comprehensive rate limiting for all public API endpoints", "Medium", "Open", 4, "Security", "API Development", 1, "api,security,rate-limit,public"),
            ("Customer Data Export Feature", "Add secure ability to export customer data in multiple formats (CSV, PDF, Excel)", "Low", "Resolved", 3, "Feature Request", "Data Export", 5, "export,csv,pdf,excel,feature"),
            ("Production Server Monitoring", "Set up comprehensive monitoring and alerting for all production infrastructure", "High", "Open", 2, "Infrastructure", "Server Management", 1, "monitoring,servers,production,alerts"),
            ("Security Policy Update", "Update password requirements and implement 2FA to meet new compliance standards", "Medium", "Closed", 4, "Security", "Policy Management", 1, "password,policy,security,2fa,compliance"),
            ("Customer Portal Performance", "Customer self-service portal loading slowly during peak hours", "Medium", "Open", 3, "Performance", "Customer Portal", 5, "portal,performance,peak-hours"),
            ("Backup System Validation", "Quarterly validation of backup systems and disaster recovery procedures", "Low", "Open", 2, "Maintenance", "Backup Systems", 1, "backup,disaster-recovery,validation"),
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get user IDs for assignment
        cursor.execute("SELECT id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        for i, (title, desc, priority, status, assigned_to_id, category, subcategory, reporter_id, tags) in enumerate(sample_tickets):
            # Calculate due dates based on priority and SLA
            hours_to_add = {"Critical": 4, "High": 8, "Medium": 24, "Low": 72}[priority]
            due_date = datetime.now() + timedelta(hours=hours_to_add)
            
            # Some tickets should be overdue for demonstration
            if i % 4 == 0 and status in ["Open", "In Progress"]:
                due_date = datetime.now() - timedelta(hours=2)
            
            cursor.execute("""
                INSERT INTO tickets (title, description, priority, status, assigned_to_id, category, 
                                   subcategory, created_date, due_date, reporter_id, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, desc, priority, status, assigned_to_id, category, subcategory, 
                  datetime.now() - timedelta(days=i), due_date, reporter_id, tags))
            
            ticket_id = cursor.lastrowid
            
            # Add some sample comments
            if i % 3 == 0:
                cursor.execute("""
                    INSERT INTO ticket_comments (ticket_id, user_id, comment, is_internal, created_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (ticket_id, assigned_to_id, f"Working on this issue. Initial analysis shows {['network', 'database', 'authentication', 'UI'][i % 4]} related problems.", 
                          0, datetime.now() - timedelta(hours=2)))
                
                if i % 6 == 0:  # Internal comments
                    cursor.execute("""
                        INSERT INTO ticket_comments (ticket_id, user_id, comment, is_internal, created_date)
                        VALUES (?, ?, ?, ?, ?)
                    """, (ticket_id, 1, "Internal note: This may require escalation to vendor support.", 
                          1, datetime.now() - timedelta(hours=1)))
        
        conn.commit()
        conn.close()

# Enhanced Authentication Service with RBAC
class AuthService:
    def __init__(self, db_manager):
        self.db = db_manager
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
    
    def hash_password(self, password: str, salt: str) -> str:
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def verify_password(self, password: str, hash_value: str, salt: str) -> bool:
        return self.hash_password(password, salt) == hash_value
    
    def check_password_strength(self, password: str) -> Tuple[str, int]:
        """Return password strength level and score (0-4)"""
        score = 0
        feedback = []
        
        if len(password) >= 8:
            score += 1
        else:
            feedback.append("At least 8 characters")
            
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            feedback.append("Uppercase letter")
            
        if re.search(r'[a-z]', password):
            score += 1
        else:
            feedback.append("Lowercase letter")
            
        if re.search(r'\d', password):
            score += 1
        else:
            feedback.append("Number")
            
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1
        else:
            feedback.append("Special character")
        
        strength_levels = ["Very Weak", "Weak", "Fair", "Good", "Strong"]
        return strength_levels[min(score, 4)], score
    
    def is_account_locked(self, user_id: int) -> bool:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT locked_until FROM users 
            WHERE id = ? AND locked_until > ?
        """, (user_id, datetime.now()))
        
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def login(self, username: str, password: str, ip_address: str = "") -> Tuple[bool, Optional[Dict], str]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute("""
            SELECT id, username, email, password_hash, salt, first_name, last_name, role,
                   department, is_active, failed_login_attempts, locked_until
            FROM users WHERE username = ?
        """, (username,))
        
        user = cursor.fetchone()
        
        if not user:
            self.log_audit(None, "LOGIN_FAILED", "authentication", None, 
                          f"Login attempt with invalid username: {username}", ip_address)
            conn.close()
            return False, None, "Invalid username or password"
        
        user_id = user[0]
        
        # Check if account is active
        if not user[9]:  # is_active
            self.log_audit(user_id, "LOGIN_FAILED", "authentication", None, 
                          "Login attempt on deactivated account", ip_address)
            conn.close()
            return False, None, "Account is deactivated"
        
        # Check if account is locked
        if user[11] and user[11] > datetime.now().isoformat():  # locked_until
            self.log_audit(user_id, "LOGIN_FAILED", "authentication", None, 
                          "Login attempt on locked account", ip_address)
            conn.close()
            return False, None, f"Account is locked due to too many failed attempts. Try again later."
        
        # Verify password
        if not self.verify_password(password, user[3], user[4]):
            # Increment failed attempts
            failed_attempts = (user[10] or 0) + 1
            locked_until = None
            
            if failed_attempts >= self.max_failed_attempts:
                locked_until = datetime.now() + self.lockout_duration
            
            cursor.execute("""
                UPDATE users SET failed_login_attempts = ?, locked_until = ?
                WHERE id = ?
            """, (failed_attempts, locked_until, user_id))
            
            self.log_audit(user_id, "LOGIN_FAILED", "authentication", None, 
                          f"Invalid password attempt {failed_attempts}/{self.max_failed_attempts}", ip_address)
            conn.commit()
            conn.close()
            
            if locked_until:
                return False, None, f"Too many failed attempts. Account locked for {self.lockout_duration.seconds//60} minutes."
            
            return False, None, "Invalid username or password"
        
        # Successful login - reset failed attempts and update last login
        cursor.execute("""
            UPDATE users SET last_login_date = ?, failed_login_attempts = 0, locked_until = NULL
            WHERE id = ?
        """, (datetime.now(), user_id))
        
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
        
        self.log_audit(user_id, "LOGIN_SUCCESS", "authentication", None, 
                      "Successful login", ip_address)
        
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
                'view_audit_logs': True,
                'manage_settings': True,
                'view_internal_comments': True,
                'manage_sla': True,
                'bulk_operations': True,
                'export_data': True,
            },
            'Manager': {
                'create_tickets': True,
                'edit_all_tickets': True,
                'delete_tickets': False,
                'view_all_tickets': True,
                'manage_users': False,
                'view_audit_logs': True,
                'manage_settings': False,
                'view_internal_comments': True,
                'manage_sla': False,
                'bulk_operations': True,
                'export_data': True,
            },
            'Agent': {
                'create_tickets': True,
                'edit_all_tickets': False,
                'delete_tickets': False,
                'view_all_tickets': True,
                'manage_users': False,
                'view_audit_logs': False,
                'manage_settings': False,
                'view_internal_comments': True,
                'manage_sla': False,
                'bulk_operations': False,
                'export_data': False,
            },
            'User': {
                'create_tickets': True,
                'edit_all_tickets': False,
                'delete_tickets': False,
                'view_all_tickets': False,
                'manage_users': False,
                'view_audit_logs': False,
                'manage_settings': False,
                'view_internal_comments': False,
                'manage_sla': False,
                'bulk_operations': False,
                'export_data': False,
            }
        }
        
        return permissions.get(role, permissions['User'])
    
    def register_user(self, username: str, email: str, password: str, first_name: str, 
                     last_name: str, role: str, department: str, phone: str, created_by: int) -> Tuple[bool, str]:
        """Register a new user"""
        # Validate input
        if not all([username, email, password, first_name, last_name]):
            return False, "All required fields must be filled"
        
        # Check password strength
        strength, score = self.check_password_strength(password)
        if score < 2:
            return False, f"Password too weak ({strength}). Please use a stronger password."
        
        # Check if username/email already exists
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            conn.close()
            return False, "Username or email already exists"
        
        # Create user
        salt = secrets.token_hex(32)
        password_hash = self.hash_password(password, salt)
        
        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, salt, first_name, last_name,
                                 role, department, phone, created_date, created_by, password_changed_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (username, email, password_hash, salt, first_name, last_name, role,
                  department, phone, datetime.now(), created_by, datetime.now()))
            
            user_id = cursor.lastrowid
            self.log_audit(created_by, "USER_CREATED", "user", user_id, 
                          f"Created user: {username} ({role})")
            
            conn.commit()
            conn.close()
            return True, "User created successfully"
            
        except Exception as e:
            conn.close()
            return False, f"Error creating user: {str(e)}"
    
    def log_audit(self, user_id: Optional[int], action: str, resource_type: str, 
                  resource_id: Optional[int], details: str, ip_address: str = "", user_agent: str = ""):
        """Log audit trail"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_log (user_id, action, resource_type, resource_id, details, 
                                 ip_address, user_agent, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, action, resource_type, resource_id, details, ip_address, user_agent, datetime.now()))
        
        conn.commit()
        conn.close()

# Enhanced Ticket Service with Comments and History
class TicketService:
    def __init__(self, db_manager, auth_service):
        self.db = db_manager
        self.auth = auth_service
    
    def get_all_tickets(self, user_id: int, role: str) -> List[Dict]:
        """Get tickets based on user permissions"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Build query based on permissions
        if role in ['Admin', 'Manager']:
            # Can see all tickets
            query = """
                SELECT t.id, t.title, t.description, t.priority, t.status, t.category, t.subcategory,
                       t.created_date, t.updated_date, t.due_date, t.resolution, t.tags,
                       t.estimated_hours, t.actual_hours, t.sla_breach_date,
                       u1.first_name || ' ' || u1.last_name as assigned_to_name,
                       u2.first_name || ' ' || u2.last_name as reporter_name,
                       t.assigned_to_id, t.reporter_id
                FROM tickets t
                LEFT JOIN users u1 ON t.assigned_to_id = u1.id
                LEFT JOIN users u2 ON t.reporter_id = u2.id
                ORDER BY t.created_date DESC
            """
            cursor.execute(query)
        elif role == 'Agent':
            # Can see all tickets but limited actions
            query = """
                SELECT t.id, t.title, t.description, t.priority, t.status, t.category, t.subcategory,
                       t.created_date, t.updated_date, t.due_date, t.resolution, t.tags,
                       t.estimated_hours, t.actual_hours, t.sla_breach_date,
                       u1.first_name || ' ' || u1.last_name as assigned_to_name,
                       u2.first_name || ' ' || u2.last_name as reporter_name,
                       t.assigned_to_id, t.reporter_id
                FROM tickets t
                LEFT JOIN users u1 ON t.assigned_to_id = u1.id
                LEFT JOIN users u2 ON t.reporter_id = u2.id
                ORDER BY t.created_date DESC
            """
            cursor.execute(query)
        else:
            # Users can only see public tickets they created or are assigned to
            query = """
                SELECT t.id, t.title, t.description, t.priority, t.status, t.category, t.subcategory,
                       t.created_date, t.updated_date, t.due_date, t.resolution, t.tags,
                       t.estimated_hours, t.actual_hours, t.sla_breach_date,
                       u1.first_name || ' ' || u1.last_name as assigned_to_name,
                       u2.first_name || ' ' || u2.last_name as reporter_name,
                       t.assigned_to_id, t.reporter_id
                FROM tickets t
                LEFT JOIN users u1 ON t.assigned_to_id = u1.id
                LEFT JOIN users u2 ON t.reporter_id = u2.id
                WHERE (t.reporter_id = ? OR t.assigned_to_id = ?) AND t.is_public = 1
                ORDER BY t.created_date DESC
            """
            cursor.execute(query, (user_id, user_id))
        
        tickets = []
        for row in cursor.fetchall():
            ticket = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'priority': row[3],
                'status': row[4],
                'category': row[5],
                'subcategory': row[6],
                'created_date': row[7],
                'updated_date': row[8],
                'due_date': row[9],
                'resolution': row[10],
                'tags': row[11],
                'estimated_hours': row[12],
                'actual_hours': row[13],
                'sla_breach_date': row[14],
                'assigned_to_name': row[15] or 'Unassigned',
                'reporter_name': row[16] or 'Unknown',
                'assigned_to_id': row[17],
                'reporter_id': row[18],
                'is_overdue': self.is_ticket_overdue(row[9], row[4])
            }
            tickets.append(ticket)
        
        conn.close()
        return tickets
    
    def is_ticket_overdue(self, due_date: str, status: str) -> bool:
        """Check if ticket is overdue"""
        if not due_date or status in ['Resolved', 'Closed']:
            return False
        try:
            due = datetime.fromisoformat(due_date)
            return due < datetime.now()
        except:
            return False
    
    def create_ticket(self, ticket_data: Dict, user_id: int) -> int:
        """Create a new ticket with audit logging"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Calculate SLA due date
        due_date = self.calculate_sla_due_date(ticket_data['priority'])
        
        cursor.execute("""
            INSERT INTO tickets (title, description, priority, status, assigned_to_id, category, 
                               subcategory, created_date, due_date, reporter_id, tags, 
                               estimated_hours, is_public)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket_data['title'],
            ticket_data['description'],
            ticket_data['priority'],
            ticket_data['status'],
            ticket_data.get('assigned_to_id'),
            ticket_data['category'],
            ticket_data.get('subcategory', ''),
            datetime.now(),
            due_date,
            user_id,
            ticket_data['tags'],
            ticket_data.get('estimated_hours'),
            ticket_data.get('is_public', 1)
        ))
        
        ticket_id = cursor.lastrowid
        
        # Log ticket creation
        self.log_ticket_history(ticket_id, user_id, "CREATED", None, None, 
                               ticket_data['status'], "Ticket created")
        
        self.auth.log_audit(user_id, "TICKET_CREATED", "ticket", ticket_id,
                           f"Created ticket: {ticket_data['title']}")
        
        conn.commit()
        conn.close()
        
        return ticket_id
    
    def calculate_sla_due_date(self, priority: str) -> datetime:
        """Calculate SLA due date based on priority"""
        hours_map = {
            'Critical': 4,
            'High': 8,
            'Medium': 24,
            'Low': 72
        }
        hours = hours_map.get(priority, 24)
        return datetime.now() + timedelta(hours=hours)
    
    def log_ticket_history(self, ticket_id: int, user_id: int, action_type: str,
                          field_name: str, old_value: str, new_value: str, description: str):
        """Log ticket history"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ticket_history (ticket_id, user_id, action_type, field_name, 
                                      old_value, new_value, description, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (ticket_id, user_id, action_type, field_name, old_value, new_value, 
              description, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def add_comment(self, ticket_id: int, user_id: int, comment: str, is_internal: bool = False) -> bool:
        """Add comment to ticket"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ticket_comments (ticket_id, user_id, comment, is_internal, created_date)
                VALUES (?, ?, ?, ?, ?)
            """, (ticket_id, user_id, comment, int(is_internal), datetime.now()))
            
            # Log the activity
            comment_type = "internal comment" if is_internal else "comment"
            self.log_ticket_history(ticket_id, user_id, "COMMENT_ADDED", None, None, None,
                                  f"Added {comment_type}")
            
            self.auth.log_audit(user_id, "COMMENT_ADDED", "ticket", ticket_id,
                               f"Added {comment_type} to ticket")
            
            conn.commit()
            conn.close()
            return True
            
        except Exception:
            return False
    
    def get_ticket_comments(self, ticket_id: int, can_view_internal: bool = False) -> List[Dict]:
        """Get comments for a ticket"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if can_view_internal:
            query = """
                SELECT c.id, c.comment, c.is_internal, c.created_date, c.updated_date,
                       u.first_name || ' ' || u.last_name as user_name, u.role
                FROM ticket_comments c
                JOIN users u ON c.user_id = u.id
                WHERE c.ticket_id = ?
                ORDER BY c.created_date ASC
            """
        else:
            query = """
                SELECT c.id, c.comment, c.is_internal, c.created_date, c.updated_date,
                       u.first_name || ' ' || u.last_name as user_name, u.role
                FROM ticket_comments c
                JOIN users u ON c.user_id = u.id
                WHERE c.ticket_id = ? AND c.is_internal = 0
                ORDER BY c.created_date ASC
            """
        
        cursor.execute(query, (ticket_id,))
        
        comments = []
        for row in cursor.fetchall():
            comment = {
                'id': row[0],
                'comment': row[1],
                'is_internal': bool(row[2]),
                'created_date': row[3],
                'updated_date': row[4],
                'user_name': row[5],
                'user_role': row[6]
            }
            comments.append(comment)
        
        conn.close()
        return comments
    
    def get_ticket_statistics(self, user_id: int, role: str) -> Dict:
        """Get ticket statistics based on user role"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if role in ['Admin', 'Manager', 'Agent']:
            # Get all ticket stats
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM tickets 
                WHERE status != 'Deleted' 
                GROUP BY status
            """)
        else:
            # Get user's ticket stats only
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM tickets 
                WHERE (reporter_id = ? OR assigned_to_id = ?) AND status != 'Deleted'
                GROUP BY status
            """, (user_id, user_id))
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = row[1]
        
        # Add additional metrics for managers/admins
        if role in ['Admin', 'Manager']:
            # Overdue tickets
            cursor.execute("""
                SELECT COUNT(*) FROM tickets 
                WHERE due_date < ? AND status NOT IN ('Resolved', 'Closed', 'Deleted')
            """, (datetime.now(),))
            stats['Overdue'] = cursor.fetchone()[0]
            
            # SLA breaches
            cursor.execute("""
                SELECT COUNT(*) FROM tickets 
                WHERE sla_breach_date IS NOT NULL
            """, )
            stats['SLA Breaches'] = cursor.fetchone()[0]
        
        conn.close()
        return stats

# Initialize services
@st.cache_resource
def init_services():
    db_manager = DatabaseManager()
    auth_service = AuthService(db_manager)
    ticket_service = TicketService(db_manager, auth_service)
    return db_manager, auth_service, ticket_service

db_manager, auth_service, ticket_service = init_services()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'selected_ticket' not in st.session_state:
    st.session_state.selected_ticket = None

# Authentication check with permission validation
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

def get_user_list() -> List[Tuple[int, str]]:
    """Get list of users for assignment"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, first_name || ' ' || last_name || ' (' || role || ')' as display_name
        FROM users WHERE is_active = 1 ORDER BY first_name, last_name
    """)
    users = cursor.fetchall()
    conn.close()
    return users

# Enhanced Login Page with Security Features
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
                    success, user, error_msg = auth_service.login(username, password, "127.0.0.1")
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

# Enhanced Dashboard with Role-Based Metrics
def show_dashboard():
    if not require_auth():
        return
    
    user = st.session_state.user
    
    # Header with user info
    st.markdown(f"""
        <div class="main-header">
            <h1>🎫 FlowTLS SYNC+ Dashboard</h1>
            <p>Welcome back, {user['full_name']}! | Role: <strong>{user['role']}</strong> | Department: {user['department']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get ticket statistics
    stats = ticket_service.get_ticket_statistics(user['id'], user['role'])
    total_tickets = sum(stats.values()) if stats else 0
    
    # Enhanced metrics row
    if user['role'] in ['Admin', 'Manager']:
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
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
        with col6:
            sla_breaches = stats.get('SLA Breaches', 0)
            st.metric("🚨 SLA Breaches", sla_breaches, delta=f"-{sla_breaches}" if sla_breaches > 0 else None)
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
            chart_stats = {k: v for k, v in stats.items() if k not in ['Overdue', 'SLA Breaches']}
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
        tickets = ticket_service.get_all_tickets(user['id'], user['role'])[:5]
        
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
                            👤 {ticket['assigned_to_name']}
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    # Quick Actions for different roles
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
        if user['permissions'].get('manage_users', False):
            if st.button("👥 Manage Users", use_container_width=True):
                st.session_state.page = 'users'
                st.rerun()
    
    with quick_col4:
        if user['permissions'].get('view_audit_logs', False):
            if st.button("📋 Audit Logs", use_container_width=True):
                st.session_state.page = 'audit'
                st.rerun()

# Continue with the rest of the application...
# [This is Part 1 of the enhanced professional version]

if __name__ == "__main__":
    # For now, show login page
    if st.session_state.page == 'login':
        show_login_page()
    elif st.session_state.page == 'dashboard':
        show_dashboard()
    else:
        st.session_state.page = 'login'
        st.rerun()
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
import threading

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
    .overdue-indicator {
        background: linear-gradient(135deg, #dc2626, #b91c1c);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.5rem;
        font-size: 0.7rem;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
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
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=20.0, isolation_level=None)
            conn.execute("PRAGMA journal_mode=WAL")
            return conn
        except Exception as e:
            st.error(f"Database connection error: {str(e)}")
            raise
    
    def _init_database(self):
        with db_lock:
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
                        can_export_data INTEGER DEFAULT 0
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
                        source TEXT DEFAULT 'Manual'
                    );
                    
                    CREATE TABLE IF NOT EXISTS companies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id TEXT UNIQUE NOT NULL,
                        company_name TEXT NOT NULL,
                        contact_email TEXT DEFAULT '',
                        phone TEXT DEFAULT '',
                        address TEXT DEFAULT '',
                        is_active INTEGER DEFAULT 1,
                        created_date TEXT NOT NULL
                    );
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
            ('admin', 'admin@flowtls.com', 'admin123', 'System', 'Administrator', 'Admin', 'IT', '+1-555-0001', 'FLOWTLS001', 1, 1, 1, 1, 1, 1, 1),
            ('jsmith', 'john.smith@flowtls.com', 'password123', 'John', 'Smith', 'Manager', 'Support', '+1-555-0002', 'FLOWTLS001', 0, 0, 0, 1, 1, 0, 1),
            ('achen', 'alice.chen@flowtls.com', 'password123', 'Alice', 'Chen', 'Agent', 'Technical', '+1-555-0003', 'FLOWTLS001', 0, 0, 0, 1, 1, 0, 0),
            ('sjohnson', 'sarah.johnson@flowtls.com', 'password123', 'Sarah', 'Johnson', 'User', 'Operations', '+1-555-0005', 'CLIENT001', 0, 0, 0, 0, 0, 0, 0)
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
                                     can_export_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_data[0], user_data[1], password_hash, salt,
                    user_data[3], user_data[4], user_data[5],
                    user_data[6], user_data[7], user_data[8],
                    datetime.now().isoformat(), 'System',
                    user_data[9], user_data[10], user_data[11], user_data[12],
                    user_data[13], user_data[14], user_data[15]
                ))
            except Exception as e:
                st.error(f"Error creating user {user_data[0]}: {str(e)}")
    
    def _create_sample_tickets(self, cursor):
        sample_tickets = [
            ("FlowTLS Integration Critical Error", "System integration completely failing - production down", "Critical", "Open", "John Smith", "Integration", "System Integration", "Sarah Johnson", "urgent,integration,flowtls,production", "CLIENT001"),
            ("User Authentication SSO Issues", "Multiple users unable to login with SSO affecting entire department", "High", "In Progress", "Alice Chen", "Security", "Authentication", "System Administrator", "sso,login,authentication,department", "CLIENT002"),
            ("Database Performance Degradation", "Customer reports taking 30+ seconds to load, needs immediate optimization", "High", "Open", "Alice Chen", "Performance", "Database", "John Smith", "performance,database,reports,slow", "CLIENT001"),
            ("UI Modernization Project", "Update interface design to match new corporate brand guidelines", "Medium", "Open", "Alice Chen", "Enhancement", "User Interface", "Sarah Johnson", "ui,enhancement,design,branding", "CLIENT001"),
            ("Email Notification System", "Configure automated email alerts for high priority tickets", "Medium", "Resolved", "John Smith", "Configuration", "Email System", "System Administrator", "email,notifications,alerts", "CLIENT002"),
            ("Server Maintenance Window", "Scheduled maintenance for database servers", "Low", "Open", "John Smith", "Maintenance", "Infrastructure", "Alice Chen", "maintenance,scheduled,database", "CLIENT001"),
            ("Mobile App Bug Report", "Users reporting crashes on iOS app during login", "High", "In Progress", "Alice Chen", "Bug", "Mobile Application", "Sarah Johnson", "bug,mobile,ios,crash", "CLIENT002"),
            ("Network Connectivity Issues", "Intermittent connection drops affecting remote users", "Medium", "Open", "John Smith", "Network", "Infrastructure", "System Administrator", "network,connectivity,remote", "CLIENT001")
        ]
        
        for i, (title, desc, priority, status, assigned_to, category, subcategory, reporter, tags, company_id) in enumerate(sample_tickets):
            try:
                hours_to_add = {"Critical": 4, "High": 8, "Medium": 24, "Low": 72}[priority]
                due_date = datetime.now() + timedelta(hours=hours_to_add)
                
                # Make some tickets overdue for demonstration
                if i % 4 == 0 and status in ["Open", "In Progress"]:
                    due_date = datetime.now() - timedelta(hours=2)
                
                cursor.execute("""
                    INSERT INTO tickets (title, description, priority, status, assigned_to, category, 
                                       subcategory, created_date, due_date, reporter, tags, company_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (title, desc, priority, status, assigned_to, category, subcategory, 
                      (datetime.now() - timedelta(days=i)).isoformat(), due_date.isoformat(), 
                      reporter, tags, company_id))
            except Exception as e:
                st.error(f"Error creating sample ticket {i}: {str(e)}")
    
    def _create_sample_companies(self, cursor):
        companies = [
            ("FLOWTLS001", "FlowTLS Internal", "admin@flowtls.com", "+1-555-0000", "123 Tech Street, Silicon Valley, CA"),
            ("CLIENT001", "Acme Corporation", "support@acme.com", "+1-555-1000", "456 Business Ave, New York, NY"),
            ("CLIENT002", "TechStart Inc", "help@techstart.com", "+1-555-2000", "789 Innovation Dr, Austin, TX")
        ]
        
        for company_id, name, email, phone, address in companies:
            try:
                cursor.execute("""
                    INSERT INTO companies (company_id, company_name, contact_email, phone, address, created_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (company_id, name, email, phone, address, datetime.now().isoformat()))
            except Exception as e:
                st.error(f"Error creating company {company_id}: {str(e)}")

class AuthService:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def hash_password(self, password: str, salt: str) -> str:
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def verify_password(self, password: str, hash_value: str, salt: str) -> bool:
        return self.hash_password(password, salt) == hash_value
    
    def login(self, username: str, password: str) -> Tuple[bool, Optional[Dict], str]:
        if not username or not password:
            return False, None, "Username and password are required"
        
        with db_lock:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, username, email, password_hash, salt, first_name, last_name, role,
                           department, company_id, is_active, can_create_users, can_deactivate_users,
                           can_reset_passwords, can_manage_tickets, can_view_all_tickets, 
                           can_delete_tickets, can_export_data
                    FROM users WHERE username = ? AND is_active = 1
                """, (username,))
                
                user = cursor.fetchone()
                
                if not user:
                    conn.close()
                    return False, None, "Invalid username or password"
                
                if not self.verify_password(password, user[3], user[4]):
                    conn.close()
                    return False, None, "Invalid username or password"
                
                cursor.execute("UPDATE users SET last_login_date = ? WHERE id = ?", (datetime.now().isoformat(), user[0]))
                
                user_data = {
                    'id': user[0], 'username': user[1], 'email': user[2],
                    'first_name': user[5], 'last_name': user[6], 'full_name': f"{user[5]} {user[6]}".strip(),
                    'role': user[7], 'department': user[8], 'company_id': user[9],
                    'permissions': {
                        'can_create_users': bool(user[11]), 'can_deactivate_users': bool(user[12]),
                        'can_reset_passwords': bool(user[13]), 'can_manage_tickets': bool(user[14]),
                        'can_view_all_tickets': bool(user[15]), 'can_delete_tickets': bool(user[16]),
                        'can_export_data': bool(user[17])
                    }
                }
                
                conn.commit()
                conn.close()
                return True, user_data, ""
                
            except Exception as e:
                return False, None, f"Authentication error: {str(e)}"

class UserService:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_all_users(self, include_inactive=False):
        with db_lock:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                query = """
                    SELECT id, username, email, first_name, last_name, role, department, 
                           company_id, is_active, created_date, last_login_date, created_by,
                           can_create_users, can_deactivate_users, can_reset_passwords,
                           can_manage_tickets, can_view_all_tickets, can_delete_tickets,
                           can_export_data, phone
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
        with db_lock:
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
        with db_lock:
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
        with db_lock:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                if permissions.get('can_view_all_tickets', False):
                    cursor.execute("""
                        SELECT id, title, description, priority, status, assigned_to, category, subcategory,
                               created_date, updated_date, due_date, reporter, resolution, tags,
                               estimated_hours, actual_hours, company_id, source
                        FROM tickets ORDER BY created_date DESC
                    """)
                else:
                    st.error("Please enter both username and password")
        
        with st.expander("🎭 Demo User Accounts", expanded=True):
            st.markdown("**Administrator:** `admin` / `admin123` - Full system access  \n**Manager:** `jsmith` / `password123` - Can manage tickets and view reports  \n**Agent:** `achen` / `password123` - Can work on assigned tickets  \n**User:** `sjohnson` / `password123` - Can create and view own tickets")

def show_dashboard():
    if not require_auth():
        return
    
    user = st.session_state.user
    st.markdown(f'<div class="main-header"><h1>🎫 FlowTLS SYNC+ Dashboard</h1><p>Welcome back, {user["full_name"]}! | Role: <strong>{user["role"]}</strong> | Department: {user["department"]}</p></div>', unsafe_allow_html=True)
    
    # Get tickets for dashboard
    tickets = ticket_service.get_all_tickets(user['id'], user['permissions'], user['full_name'])
    
    # Quick Action Buttons
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
    
    with col4:
        if user['permissions'].get('can_create_users', False):
            if st.button("👥 Manage Users", use_container_width=True):
                st.session_state.page = 'users'
                st.rerun()
    
    # Dashboard Metrics
    st.subheader("📈 Dashboard Overview")
    
    # Calculate metrics
    total_tickets = len(tickets)
    open_tickets = len([t for t in tickets if t['status'] == 'Open'])
    in_progress_tickets = len([t for t in tickets if t['status'] == 'In Progress'])
    resolved_tickets = len([t for t in tickets if t['status'] == 'Resolved'])
    overdue_tickets = len([t for t in tickets if t['is_overdue']])
    
    # Metrics cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{total_tickets}</div>
            <div class="metric-label">Total Tickets</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value" style="color: #dc2626;">{open_tickets}</div>
            <div class="metric-label">Open</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value" style="color: #ca8a04;">{in_progress_tickets}</div>
            <div class="metric-label">In Progress</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value" style="color: #059669;">{resolved_tickets}</div>
            <div class="metric-label">Resolved</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col5:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value" style="color: #dc2626;">{overdue_tickets}</div>
            <div class="metric-label">Overdue</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Charts Row
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
    
    # Recent Tickets
    st.subheader("🕐 Recent Tickets")
    if tickets:
        recent_tickets = sorted(tickets, key=lambda x: x['created_date'], reverse=True)[:5]
        
        for ticket in recent_tickets:
            # Get company details
            company = user_service.get_company_by_id(ticket['company_id'])
            company_name = company['company_name'] if company else ticket['company_id']
            
            with st.container():
                st.markdown(f'''
                <div class="ticket-card">
                    <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 0.5rem;">
                        <h4 style="margin: 0;">#{ticket['id']} - {ticket['title']}</h4>
                        {'<span class="overdue-indicator">⚠️ OVERDUE</span>' if ticket['is_overdue'] else ''}
                    </div>
                    <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem;">
                        <span class="priority-{ticket['priority'].lower()}">{ticket['priority']}</span>
                        <span class="status-{ticket['status'].lower().replace(' ', '-')}">{ticket['status']}</span>
                    </div>
                    <p style="margin: 0.5rem 0; color: #6b7280;">{ticket['description'][:100]}{'...' if len(ticket['description']) > 100 else ''}</p>
                    <div style="display: flex; justify-content: between; align-items: center; font-size: 0.85rem; color: #6b7280;">
                        <span><strong>Company:</strong> {company_name}</span>
                        <span><strong>Assigned:</strong> {ticket['assigned_to']}</span>
                        <span><strong>Due:</strong> {format_date(ticket['due_date'])}</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
    else:
        st.info("No tickets found. Create your first ticket using the button above!")

def show_tickets_page():
    if not require_auth():
        return
    
    st.title("🎫 Ticket Management")
    
    # Get tickets
    tickets = ticket_service.get_all_tickets(st.session_state.user['id'], 
                                           st.session_state.user['permissions'], 
                                           st.session_state.user['full_name'])
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Open", "In Progress", "Resolved", "Closed"])
    with col2:
        priority_filter = st.selectbox("Filter by Priority", ["All", "Critical", "High", "Medium", "Low"])
    with col3:
        company_filter = st.selectbox("Filter by Company", ["All"] + list(set([t['company_id'] for t in tickets])))
    
    # Apply filters
    filtered_tickets = tickets
    if status_filter != "All":
        filtered_tickets = [t for t in filtered_tickets if t['status'] == status_filter]
    if priority_filter != "All":
        filtered_tickets = [t for t in filtered_tickets if t['priority'] == priority_filter]
    if company_filter != "All":
        filtered_tickets = [t for t in filtered_tickets if t['company_id'] == company_filter]
    
    st.subheader(f"Showing {len(filtered_tickets)} of {len(tickets)} tickets")
    
    # Display tickets
    for ticket in filtered_tickets:
        # Get company details
        company = user_service.get_company_by_id(ticket['company_id'])
        company_name = company['company_name'] if company else ticket['company_id']
        
        with st.container():
            st.markdown(f'''
            <div class="ticket-card">
                <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 0.5rem;">
                    <h4 style="margin: 0;">#{ticket['id']} - {ticket['title']}</h4>
                    {'<span class="overdue-indicator">⚠️ OVERDUE</span>' if ticket['is_overdue'] else ''}
                </div>
                <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem;">
                    <span class="priority-{ticket['priority'].lower()}">{ticket['priority']}</span>
                    <span class="status-{ticket['status'].lower().replace(' ', '-')}">{ticket['status']}</span>
                </div>
                <p style="margin: 0.5rem 0; color: #374151;">{ticket['description']}</p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.85rem; color: #6b7280; margin-top: 1rem;">
                    <div><strong>Company:</strong> {company_name}</div>
                    <div><strong>Category:</strong> {ticket['category']}</div>
                    <div><strong>Assigned to:</strong> {ticket['assigned_to']}</div>
                    <div><strong>Reporter:</strong> {ticket['reporter']}</div>
                    <div><strong>Created:</strong> {format_date(ticket['created_date'])}</div>
                    <div><strong>Due:</strong> {format_date(ticket['due_date'])}</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

def show_create_ticket_page():
    if not require_auth():
        return
    
    st.title("➕ Create New Ticket")
    
    # Get companies for dropdown
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
                    if st.button("Go to Dashboard"):
                        st.session_state.page = 'dashboard'
                        st.rerun()
                else:
                    st.error("❌ Failed to create ticket. Please try again.")
            else:
                st.error("❌ Please fill in all required fields (marked with *)")

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
            
            # Navigation buttons
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.page = 'dashboard'
                st.rerun()
            
            if st.button("🎫 Tickets", use_container_width=True):
                st.session_state.page = 'tickets'
                st.rerun()
            
            if st.button("➕ Create Ticket", use_container_width=True):
                st.session_state.page = 'create_ticket'
                st.rerun()
            
            # Admin functions
            if user['permissions'].get('can_view_all_tickets', False):
                if st.button("📈 Analytics", use_container_width=True):
                    st.session_state.page = 'analytics'
                    st.rerun()
            
            if user['permissions'].get('can_create_users', False):
                if st.button("👥 Users", use_container_width=True):
                    st.session_state.page = 'users'
                    st.rerun()
            
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.page = 'login'
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
        elif st.session_state.page == 'create_ticket':
            show_create_ticket_page()
        else:
            st.session_state.page = 'login'
            st.rerun()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please refresh the page to continue.")

if __name__ == "__main__":
    main()cursor.execute("""
                        SELECT id, title, description, priority, status, assigned_to, category, subcategory,
                               created_date, updated_date, due_date, reporter, resolution, tags,
                               estimated_hours, actual_hours, company_id, source
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
                        'company_id': row[16], 'source': row[17],
                        'is_overdue': self.is_ticket_overdue(row[10], row[4])
                    }
                    tickets.append(ticket)
                
                conn.close()
                return tickets
            except Exception as e:
                st.error(f"Error retrieving tickets: {str(e)}")
                return []
    
    def is_ticket_overdue(self, due_date: str, status: str) -> bool:
        if not due_date or status in ['Resolved', 'Closed']:
            return False
        try:
            due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            return due < datetime.now()
        except:
            return False
    
    def create_ticket(self, ticket_data: Dict, user_name: str) -> bool:
        with db_lock:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                hours_to_add = {"Critical": 4, "High": 8, "Medium": 24, "Low": 72}[ticket_data['priority']]
                due_date = datetime.now() + timedelta(hours=hours_to_add)
                
                cursor.execute("""
                    INSERT INTO tickets (title, description, priority, status, assigned_to, category, 
                                       subcategory, created_date, due_date, reporter, tags, company_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ticket_data['title'], ticket_data['description'], ticket_data['priority'],
                    ticket_data['status'], ticket_data['assigned_to'], ticket_data['category'],
                    ticket_data['subcategory'], datetime.now().isoformat(), due_date.isoformat(),
                    user_name, ticket_data['tags'], ticket_data['company_id']
                ))
                
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                st.error(f"Error creating ticket: {str(e)}")
                return False

def init_services():
    try:
        db_manager = DatabaseManager()
        auth_service = AuthService(db_manager)
        ticket_service = TicketService(db_manager)
        user_service = UserService(db_manager)
        return db_manager, auth_service, ticket_service, user_service
    except Exception as e:
        st.error(f"Failed to initialize services: {str(e)}")
        st.stop()

try:
    db_manager, auth_service, ticket_service, user_service = init_services()
except Exception as e:
    st.error("Application initialization failed. Please refresh the page.")
    st.stop()

if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

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
                if username and password:
                    try:
                        success, user, error_msg = auth_service.login(username, password)
                        if success:
                            st.session_state.user = user
                            st.session_state.page = 'dashboard'
                            st.rerun()
                        else:
                            st.error(error_msg)
                    except Exception as e:
                        st.error(f"Login error: {str(e)}")
                else:
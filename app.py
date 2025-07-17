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
    
    .user-card {
        border: 1px solid #e5e7eb;
        border-radius: 0.75rem;
        padding: 1.25rem;
        margin: 0.75rem 0;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    
    .user-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border-color: #3b82f6;
    }
    
    .user-inactive {
        opacity: 0.6;
        border-left: 4px solid #dc2626;
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
</style>
""", unsafe_allow_html=True)

# Thread-safe database connection lock
db_lock = threading.Lock()

# Enhanced Database Manager
class DatabaseManager:
    def deactivate_user(self, user_id: int) -> bool:
        with db_lock:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                st.error(f"Error deactivating user: {str(e)}")
                return False
    
    def activate_user(self, user_id: int) -> bool:
        with db_lock:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("UPDATE users SET is_active = 1 WHERE id = ?", (user_id,))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                st.error(f"Error activating user: {str(e)}")
                return False
    
    def reset_password(self, user_id: int, new_password: str) -> bool:
        with db_lock:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                # Generate new salt and hash
                salt = secrets.token_hex(32)
                password_hash = hashlib.sha256((new_password + salt).encode()).hexdigest()
                
                cursor.execute("""
                    UPDATE users SET password_hash = ?, salt = ? WHERE id = ?
                """, (password_hash, salt, user_id))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                st.error(f"Error resetting password: {str(e)}")
                return False
    
    def get_companies(self):
        with db_lock:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT company_id, company_name, contact_email, phone, address, is_active
                    FROM companies ORDER BY company_name
                """)
                
                companies = []
                for row in cursor.fetchall():
                    company = {
                        'company_id': row[0],
                        'company_name': row[1],
                        'contact_email': row[2],
                        'phone': row[3],
                        'address': row[4],
                        'is_active': bool(row[5])
                    }
                    companies.append(company)
                
                conn.close()
                return companies
                
            except Exception as e:
                st.error(f"Error retrieving companies: {str(e)}")
                return []

# Enhanced Ticket Service
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
                    cursor.execute("""
                        SELECT id, title, description, priority, status, assigned_to, category, subcategory,
                               created_date, updated_date, due_date, reporter, resolution, tags,
                               estimated_hours, actual_hours, company_id, source
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
                        'company_id': row[16],
                        'source': row[17],
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
    
    def create_ticket(self, ticket_data: Dict, user_name: str, user_id: int) -> int:
        with db_lock:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                # Calculate due date based on priority
                hours_map = {'Critical': 4, 'High': 8, 'Medium': 24, 'Low': 72}
                hours = hours_map.get(ticket_data['priority'], 24)
                due_date = datetime.now() + timedelta(hours=hours)
                
                cursor.execute("""
                    INSERT INTO tickets (title, description, priority, status, assigned_to, category, 
                                       subcategory, created_date, due_date, reporter, reporter_id, tags, 
                                       estimated_hours, company_id, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ticket_data['title'],
                    ticket_data['description'],
                    ticket_data['priority'],
                    ticket_data.get('status', 'Open'),
                    ticket_data.get('assigned_to', ''),
                    ticket_data['category'],
                    ticket_data.get('subcategory', ''),
                    datetime.now().isoformat(),
                    due_date.isoformat(),
                    user_name,
                    user_id,
                    ticket_data.get('tags', ''),
                    ticket_data.get('estimated_hours', 0),
                    ticket_data.get('company_id', ''),
                    ticket_data.get('source', 'Manual')
                ))
                
                ticket_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                return ticket_id
                
            except Exception as e:
                st.error(f"Error creating ticket: {str(e)}")
                return 0
    
    def update_ticket(self, ticket_id: int, ticket_data: Dict) -> bool:
        with db_lock:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE tickets SET title=?, description=?, priority=?, status=?, assigned_to=?, 
                                     category=?, subcategory=?, updated_date=?, resolution=?, tags=?,
                                     estimated_hours=?, actual_hours=?, company_id=?
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
                    ticket_data.get('company_id', ''),
                    ticket_id
                ))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                st.error(f"Error updating ticket: {str(e)}")
                return False
    
    def get_ticket_statistics(self, user_id: int, permissions: Dict, user_name: str) -> Dict:
        with db_lock:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                if permissions.get('can_view_all_tickets', False):
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
                
                # Add overdue count for those who can view all tickets
                if permissions.get('can_view_all_tickets', False):
                    cursor.execute("""
                        SELECT COUNT(*) FROM tickets 
                        WHERE due_date < ? AND status NOT IN ('Resolved', 'Closed', 'Deleted')
                    """, (datetime.now().isoformat(),))
                    stats['Overdue'] = cursor.fetchone()[0]
                
                conn.close()
                return stats
                
            except Exception as e:
                st.error(f"Error retrieving statistics: {str(e)}")
                return {}

# Initialize services
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

# Initialize services
try:
    db_manager, auth_service, ticket_service, user_service = init_services()
except Exception as e:
    st.error("Application initialization failed. Please refresh the page.")
    st.stop()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'selected_ticket' not in st.session_state:
    st.session_state.selected_ticket = None
if 'selected_user' not in st.session_state:
    st.session_state.selected_user = None

# Authentication check
def require_auth(permission: str = None) -> bool:
    if not st.session_state.user:
        st.session_state.page = 'login'
        return False
    
    if permission and not st.session_state.user.get('permissions', {}).get(permission, False):
        st.error(f"⚠️ Access Denied: You don't have permission for this action")
        return False
    
    return True

# Utility functions
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

def generate_csv_export(tickets):
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'ID', 'Title', 'Description', 'Priority', 'Status', 'Assigned To',
        'Category', 'Subcategory', 'Created Date', 'Updated Date', 'Due Date', 
        'Reporter', 'Tags', 'Estimated Hours', 'Actual Hours', 'Company ID', 'Source'
    ])
    
    for ticket in tickets:
        writer.writerow([
            ticket['id'], ticket['title'], ticket['description'], ticket['priority'],
            ticket['status'], ticket['assigned_to'], ticket['category'], ticket['subcategory'],
            format_date(ticket['created_date']), format_date(ticket['updated_date']),
            format_date(ticket['due_date']), ticket['reporter'], ticket['tags'],
            ticket['estimated_hours'], ticket['actual_hours'], ticket['company_id'], ticket['source']
        ])
    
    return output.getvalue()

# Login Page
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
                    st.error("Please enter both username and password")
        
        with st.expander("🎭 Demo User Accounts", expanded=True):
            st.markdown("""
            **Administrator:** `admin` / `admin123` - Full system access  
            **Manager:** `jsmith` / `password123` - Can manage tickets and view reports  
            **Agent:** `achen` / `password123` - Can work on assigned tickets  
            **User:** `sjohnson` / `password123` - Can create and view own tickets  
            
            *Each role has different permissions and access levels*
            """)

# Dashboard
def show_dashboard():
    if not require_auth():
        return
    
    user = st.session_state.user
    user_name = user['full_name']
    
    st.markdown(f"""
        <div class="main-header">
            <h1>🎫 FlowTLS SYNC+ Dashboard</h1>
            <p>Welcome back, {user_name}! | Role: <strong>{user['role']}</strong> | Department: {user['department']} | Company: {user['company_id']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get ticket statistics
    stats = ticket_service.get_ticket_statistics(user['id'], user['permissions'], user_name)
    total_tickets = sum(stats.values()) if stats else 0
    
    # Enhanced metrics row
    if user['permissions'].get('can_view_all_tickets', False):
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
        tickets = ticket_service.get_all_tickets(user['id'], user['permissions'], user_name)[:5]
        
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
                            👤 {ticket['assigned_to']} | 🏢 {ticket['company_id']}
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
        if user['permissions'].get('can_create_users', False):
            if st.button("👥 User Management", use_container_width=True):
                st.session_state.page = 'users'
                st.rerun()
    
    with quick_col4:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.page = 'settings'
            st.rerun()

# Tickets Page
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
        if user['permissions'].get('can_export_data', False):
            if st.button("📊 Export CSV", use_container_width=True):
                tickets = ticket_service.get_all_tickets(user['id'], user['permissions'], user_name)
                csv_data = generate_csv_export(tickets)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"flowtls_tickets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    # Get tickets
    tickets = ticket_service.get_all_tickets(user['id'], user['permissions'], user_name)
    
    if search_term:
        tickets = [t for t in tickets if search_term.lower() in t['title'].lower() or 
                  search_term.lower() in t['description'].lower() or 
                  search_term.lower() in t['tags'].lower()]
    
    if filter_status != "All":
        tickets = [t for t in tickets if t['status'] == filter_status]
    
    # Display tickets
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
                            <span style="margin-left: 10px; color: #4b5563;">🏢 {ticket['company_id']}</span>
                        </div>
                        <div style="font-size: 0.875rem; color: #6b7280;">
                            <span>📅 Created: {format_date(ticket['created_date'])}</span>
                            <span style="margin-left: 15px;">⏰ Due: {format_date(ticket['due_date'])}</span>
                            <span style="margin-left: 15px;">👨‍💼 Reporter: {ticket['reporter']}</span>
                            <span style="margin-left: 15px;">📧 Source: {ticket['source']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("View Details", key=f"view_{ticket['id']}"):
                    st.session_state.selected_ticket = ticket
                    st.session_state.page = 'ticket_details'
                    st.rerun()
                
                if user['permissions'].get('can_manage_tickets', False):
                    if st.button("Edit", key=f"edit_{ticket['id']}"):
                        st.session_state.selected_ticket = ticket
                        st.session_state.page = 'edit_ticket'
                        st.rerun()

# User Management Page
def show_users_page():
    if not require_auth('can_create_users'):
        return
    
    st.title("👥 User Management")
    
    # Action buttons
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search users", placeholder="Search by name, username, or email")
    
    with col2:
        if st.button("➕ New User", use_container_width=True):
            st.session_state.page = 'new_user'
            st.rerun()
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    with col4:
        show_inactive = st.checkbox("Show Inactive Users")
    
    # Get users
    users = user_service.get_all_users(include_inactive=show_inactive)
    
    if search_term:
        users = [u for u in users if search_term.lower() in u['username'].lower() or 
                search_term.lower() in u['full_name'].lower() or 
                search_term.lower() in u['email'].lower()]
    
    # Display users
    display_user_list(users)

def display_user_list(users):
    if not users:
        st.info("No users found.")
        return
    
    for user in users:
        user_class = "user-inactive" if not user['is_active'] else ""
        role_class = f"user-role-{user['role'].lower()}"
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                status_indicator = "🔴 INACTIVE" if not user['is_active'] else "🟢 ACTIVE"
                
                st.markdown(f"""
                    <div class="user-card {user_class}">
                        <h4 style="color: #1f2937 !important; margin-bottom: 0.75rem;">
                            👤 {user['full_name']} (@{user['username']}) {status_indicator}
                        </h4>
                        <p style="color: #4b5563 !important; margin-bottom: 0.75rem;">
                            📧 {user['email']} | 📞 {user['phone']} | 🏢 {user['company_id']}
                        </p>
                        <div style="margin-bottom: 0.5rem;">
                            <span class="{role_class}">{user['role']}</span>
                            <span style="margin-left: 10px; color: #4b5563;">🏢 {user['department']}</span>
                        </div>
                        <div style="font-size: 0.875rem; color: #6b7280;">
                            <span>📅 Created: {format_date(user['created_date'])}</span>
                            <span style="margin-left: 15px;">⏰ Last Login: {format_date(user['last_login_date'])}</span>
                            <span style="margin-left: 15px;">👨‍💼 Created by: {user['created_by']}</span>
                        </div>
                        <div style="font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem;">
                            Permissions: 
                            {'✅ Create Users' if user['permissions']['can_create_users'] else '❌ Create Users'} | 
                            {'✅ Manage Tickets' if user['permissions']['can_manage_tickets'] else '❌ Manage Tickets'} | 
                            {'✅ View All' if user['permissions']['can_view_all_tickets'] else '❌ View All'} |
                            {'✅ Export Data' if user['permissions']['can_export_data'] else '❌ Export Data'}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("Edit", key=f"edit_user_{user['id']}"):
                    st.session_state.selected_user = user
                    st.session_state.page = 'edit_user'
                    st.rerun()
                
                if user['is_active']:
                    if st.button("Deactivate", key=f"deactivate_{user['id']}"):
                        if user_service.deactivate_user(user['id']):
                            st.success(f"User {user['username']} deactivated")
                            st.rerun()
                else:
                    if st.button("Activate", key=f"activate_{user['id']}"):
                        if user_service.activate_user(user['id']):
                            st.success(f"User {user['username']} activated")
                            st.rerun()

# New User Page
def show_new_user_page():
    if not require_auth('can_create_users'):
        return
    
    st.title("➕ Create New User")
    
    companies = user_service.get_companies()
    company_options = [f"{comp['company_id']} - {comp['company_name']}" for comp in companies]
    
    with st.form("new_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username*", placeholder="Enter username")
            first_name = st.text_input("First Name*", placeholder="Enter first name")
            last_name = st.text_input("Last Name*", placeholder="Enter last name")
            email = st.text_input("Email*", placeholder="Enter email address")
            password = st.text_input("Password*", type="password", placeholder="Enter password")
            phone = st.text_input("Phone", placeholder="Enter phone number")
        
        with col2:
            role = st.selectbox("Role*", ["User", "Agent", "Manager", "Admin"])
            department = st.text_input("Department", placeholder="Enter department")
            
            if company_options:
                company_selection = st.selectbox("Company", company_options)
                company_id = company_selection.split(" - ")[0] if company_selection else ""
            else:
                company_id = st.text_input("Company ID", placeholder="Enter company ID")
        
        st.subheader("Permissions")
        perm_col1, perm_col2 = st.columns(2)
        
        with perm_col1:
            can_create_users = st.checkbox("Can Create Users")
            can_deactivate_users = st.checkbox("Can Deactivate Users")
            can_reset_passwords = st.checkbox("Can Reset Passwords")
            can_manage_tickets = st.checkbox("Can Manage Tickets")
        
        with perm_col2:
            can_view_all_tickets = st.checkbox("Can View All Tickets")
            can_delete_tickets = st.checkbox("Can Delete Tickets")
            can_export_data = st.checkbox("Can Export Data")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("Create User", use_container_width=True)
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state.page = 'users'
                st.rerun()
        
        if submitted:
            if username and first_name and last_name and email and password:
                user_data = {
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'password': password,
                    'phone': phone,
                    'role': role,
                    'department': department,
                    'company_id': company_id,
                    'can_create_users': can_create_users,
                    'can_deactivate_users': can_deactivate_users,
                    'can_reset_passwords': can_reset_passwords,
                    'can_manage_tickets': can_manage_tickets,
                    'can_view_all_tickets': can_view_all_tickets,
                    'can_delete_tickets': can_delete_tickets,
                    'can_export_data': can_export_data
                }
                
                if user_service.create_user(user_data, st.session_state.user['username']):
                    st.success(f"User {username} created successfully!")
                    st.session_state.page = 'users'
                    st.rerun()
                else:
                    st.error("Failed to create user. Username or email may already exist.")
            else:
                st.error("Please fill in all required fields (*)")

# Edit User Page
def show_edit_user_page():
    if not require_auth('can_create_users'):
        return
    
    if not st.session_state.selected_user:
        st.error("No user selected")
        st.session_state.page = 'users'
        st.rerun()
        return
    
    user = st.session_state.selected_user
    st.title(f"✏️ Edit User: {user['username']}")
    
    companies = user_service.get_companies()
    company_options = [f"{comp['company_id']} - {comp['company_name']}" for comp in companies]
    
    with st.form("edit_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name*", value=user['first_name'])
            last_name = st.text_input("Last Name*", value=user['last_name'])
            phone = st.text_input("Phone", value=user.get('phone', ''))
        
        with col2:
            role = st.selectbox("Role*", ["User", "Agent", "Manager", "Admin"], 
                               index=["User", "Agent", "Manager", "Admin"].index(user['role']))
            department = st.text_input("Department", value=user.get('department', ''))
            
            if company_options:
                current_company = next((i for i, comp in enumerate(company_options) 
                                      if comp.startswith(user.get('company_id', ''))), 0)
                company_selection = st.selectbox("Company", company_options, index=current_company)
                company_id = company_selection.split(" - ")[0] if company_selection else ""
            else:
                company_id = st.text_input("Company ID", value=user.get('company_id', ''))
        
        st.subheader("Permissions")
        perm_col1, perm_col2 = st.columns(2)
        
        with perm_col1:
            can_create_users = st.checkbox("Can Create Users", 
                                         value=user['permissions'].get('can_create_users', False))
            can_deactivate_users = st.checkbox("Can Deactivate Users", 
                                             value=user['permissions'].get('can_deactivate_users', False))
            can_reset_passwords = st.checkbox("Can Reset Passwords", 
                                            value=user['permissions'].get('can_reset_passwords', False))
            can_manage_tickets = st.checkbox("Can Manage Tickets", 
                                           value=user['permissions'].get('can_manage_tickets', False))
        
        with perm_col2:
            can_view_all_tickets = st.checkbox("Can View All Tickets", 
                                             value=user['permissions'].get('can_view_all_tickets', False))
            can_delete_tickets = st.checkbox("Can Delete Tickets", 
                                           value=user['permissions'].get('can_delete_tickets', False))
            can_export_data = st.checkbox("Can Export Data", 
                                        value=user['permissions'].get('can_export_data', False))
        
        # Password reset section
        st.subheader("Password Reset")
        new_password = st.text_input("New Password (leave blank to keep current)", type="password")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            submitted = st.form_submit_button("Update User", use_container_width=True)
        with col2:
            reset_password = st.form_submit_button("Reset Password Only", use_container_width=True)
        with col3:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state.page = 'users'
                st.session_state.selected_user = None
                st.rerun()
        
        if submitted:
            if first_name and last_name:
                user_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': phone,
                    'role': role,
                    'department': department,
                    'company_id': company_id,
                    'can_create_users': can_create_users,
                    'can_deactivate_users': can_deactivate_users,
                    'can_reset_passwords': can_reset_passwords,
                    'can_manage_tickets': can_manage_tickets,
                    'can_view_all_tickets': can_view_all_tickets,
                    'can_delete_tickets': can_delete_tickets,
                    'can_export_data': can_export_data
                }
                
                success = user_service.update_user(user['id'], user_data)
                
                if new_password and success:
                    success = user_service.reset_password(user['id'], new_password)
                
                if success:
                    st.success(f"User {user['username']} updated successfully!")
                    st.session_state.page = 'users'
                    st.session_state.selected_user = None
                    st.rerun()
                else:
                    st.error("Failed to update user.")
            else:
                st.error("Please fill in all required fields (*)")
        
        if reset_password:
            if new_password:
                if user_service.reset_password(user['id'], new_password):
                    st.success(f"Password reset for {user['username']}!")
                else:
                    st.error("Failed to reset password.")
            else:
                st.error("Please enter a new password.")

# New Ticket Page
def show_new_ticket_page():
    if not require_auth():
        return
    
    st.title("➕ Create New Ticket")
    
    user = st.session_state.user
    users = user_service.get_all_users()
    user_options = [f"{u['full_name']} ({u['username']})" for u in users if u['is_active']]
    companies = user_service.get_companies()
    company_options = [f"{comp['company_id']} - {comp['company_name']}" for comp in companies]
    
    with st.form("new_ticket_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Title*", placeholder="Enter ticket title")
            description = st.text_area("Description*", placeholder="Describe the issue or request", height=100)
            priority = st.selectbox("Priority*", ["Low", "Medium", "High", "Critical"])
            category = st.selectbox("Category*", [
                "General", "Technical Support", "Bug Report", "Feature Request",
                "Security", "Performance", "Integration", "Configuration",
                "Enhancement", "Infrastructure", "Email System"
            ])
            subcategory = st.text_input("Subcategory", placeholder="Enter subcategory")
        
        with col2:
            if user_options:
                assigned_to_selection = st.selectbox("Assign To", ["Unassigned"] + user_options)
                assigned_to = assigned_to_selection.split(" (")[0] if assigned_to_selection != "Unassigned" else ""
            else:
                assigned_to = st.text_input("Assign To", placeholder="Enter assignee name")
            
            if company_options:
                company_selection = st.selectbox("Company", company_options)
                company_id = company_selection.split(" - ")[0] if company_selection else ""
            else:
                company_id = st.text_input("Company ID", placeholder="Enter company ID", value=user['company_id'])
            
            tags = st.text_input("Tags", placeholder="Enter tags separated by commas")
            estimated_hours = st.number_input("Estimated Hours", min_value=0.0, step=0.5)
            status = st.selectbox("Status", ["Open", "In Progress", "On Hold"])
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("Create Ticket", use_container_width=True)
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state.page = 'tickets'
                st.rerun()
        
        if submitted:
            if title and description and priority and category:
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
                    'company_id': company_id,
                    'source': 'Manual'
                }
                
                ticket_id = ticket_service.create_ticket(ticket_data, user['full_name'], user['id'])
                if ticket_id > 0:
                    st.success(f"Ticket #{ticket_id} created successfully!")
                    st.session_state.page = 'tickets'
                    st.rerun()
                else:
                    st.error("Failed to create ticket.")
            else:
                st.error("Please fill in all required fields (*)")

# Settings Page
def show_settings_page():
    if not require_auth():
        return
    
    user = st.session_state.user
    st.title("⚙️ System Settings")
    
    tab1, tab2, tab3, tab4 = st.tabs(["User Profile", "Email Settings", "Company Management", "System Configuration"])
    
    with tab1:
        st.subheader("👤 Your Profile")
        
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input("Username", value=user['username'], disabled=True)
                st.text_input("Email", value=user['email'], disabled=True)
                st.text_input("Full Name", value=user['full_name'], disabled=True)
            
            with col2:
                st.text_input("Role", value=user['role'], disabled=True)
                st.text_input("Department", value=user['department'], disabled=True)
                st.text_input("Company", value=user['company_id'], disabled=True)
            
            new_password = st.text_input("Change Password", type="password", placeholder="Enter new password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm new password")
            
            if st.form_submit_button("Update Password"):
                if new_password and confirm_password:
                    if new_password == confirm_password:
                        if user_service.reset_password(user['id'], new_password):
                            st.success("Password updated successfully!")
                        else:
                            st.error("Failed to update password.")
                    else:
                        st.error("Passwords don't match.")
                else:
                    st.error("Please enter and confirm your new password.")
    
    with tab2:
        st.subheader("📧 Email Configuration")
        
        if user['permissions'].get('can_create_users', False):
            st.info("Email-to-ticket automation configuration will be available here.")
            
            with st.form("email_settings_form"):
                email_server = st.text_input("Email Server", placeholder="imap.gmail.com")
                email_port = st.number_input("Port", value=993, min_value=1, max_value=65535)
                email_username = st.text_input("Email Username", placeholder="support@company.com")
                email_password = st.text_input("Email Password", type="password")
                
                st.subheader("Field Mapping")
                col1, col2 = st.columns(2)
                
                with col1:
                    subject_to_title = st.checkbox("Map Subject to Title", value=True)
                    body_to_description = st.checkbox("Map Body to Description", value=True)
                    sender_to_reporter = st.checkbox("Map Sender to Reporter", value=True)
                
                with col2:
                    auto_assign = st.checkbox("Auto-assign based on keywords")
                    default_priority = st.selectbox("Default Priority", ["Low", "Medium", "High"])
                    default_category = st.selectbox("Default Category", ["Email Support", "General"])
                
                if st.form_submit_button("Save Email Settings"):
                    st.success("Email settings saved! (Feature in development)")
        else:
            st.warning("You don't have permission to configure email settings.")
    
    with tab3:
        st.subheader("🏢 Company Management")
        
        if user['permissions'].get('can_create_users', False):
            companies = user_service.get_companies()
            
            st.markdown("### Current Companies")
            for company in companies:
                status_icon = "🟢" if company['is_active'] else "🔴"
                st.markdown(f"""
                **{status_icon} {company['company_name']} ({company['company_id']})**  
                📧 {company['contact_email']} | 📞 {company['phone']}  
                📍 {company['address']}
                """)
            
            with st.expander("➕ Add New Company"):
                with st.form("new_company_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        company_id = st.text_input("Company ID*", placeholder="COMP001")
                        company_name = st.text_input("Company Name*", placeholder="Company Name")
                        contact_email = st.text_input("Contact Email", placeholder="contact@company.com")
                    
                    with col2:
                        phone = st.text_input("Phone", placeholder="+1-555-0000")
                        address = st.text_area("Address", placeholder="Company address")
                    
                    if st.form_submit_button("Add Company"):
                        st.success(f"Company {company_name} added! (Feature in development)")
        else:
            st.warning("You don't have permission to manage companies.")
    
    with tab4:
        st.subheader("🔧 System Configuration")
        
        if user['role'] == 'Admin':
            st.markdown("### System Information")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Users", len(user_service.get_all_users(include_inactive=True)))
            
            with col2:
                st.metric("Active Users", len(user_service.get_all_users(include_inactive=False)))
            
            with col3:
                tickets = ticket_service.get_all_tickets(user['id'], user['permissions'], user['full_name'])
                st.metric("Total Tickets", len(tickets))
            
            st.markdown("### System Settings")
            
            with st.form("system_settings_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    auto_assignment = st.checkbox("Enable Auto-assignment")
                    email_notifications = st.checkbox("Enable Email Notifications", value=True)
                    ticket_numbering = st.selectbox("Ticket Numbering", ["Sequential", "Random"])
                
                with col2:
                    default_due_hours = st.number_input("Default Due Hours", value=24, min_value=1)
                    max_file_size = st.number_input("Max File Size (MB)", value=10, min_value=1)
                    session_timeout = st.number_input("Session Timeout (minutes)", value=60, min_value=5)
                
                if st.form_submit_button("Save System Settings"):
                    st.success("System settings saved! (Feature in development)")
        else:
            st.warning("You don't have permission to access system configuration.")

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
                    <small>{user['department']} | {user['company_id']}</small>
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
            
            if user['permissions'].get('can_create_users', False):
                if st.button("👥 Users", use_container_width=True):
                    st.session_state.page = 'users'
                    st.rerun()
            
            if st.button("⚙️ Settings", use_container_width=True):
                st.session_state.page = 'settings'
                st.rerun()
            
            st.markdown("---")
            
            # Display user permissions
            st.markdown("### 🔐 Your Permissions")
            permissions = user['permissions']
            
            perm_display = []
            if permissions.get('can_create_users'): perm_display.append("👥 Manage Users")
            if permissions.get('can_manage_tickets'): perm_display.append("🎫 Manage Tickets")
            if permissions.get('can_view_all_tickets'): perm_display.append("👁️ View All Tickets")
            if permissions.get('can_export_data'): perm_display.append("📊 Export Data")
            if permissions.get('can_delete_tickets'): perm_display.append("🗑️ Delete Tickets")
            
            if perm_display:
                for perm in perm_display:
                    st.markdown(f"• {perm}")
            else:
                st.markdown("• Basic User Access")
            
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.page = 'login'
                st.session_state.selected_ticket = None
                st.session_state.selected_user = None
                st.rerun()

# Placeholder pages for ticket details and editing
def show_ticket_details_page():
    if not require_auth():
        return
    
    st.title("🎫 Ticket Details")
    
    if st.session_state.selected_ticket:
        ticket = st.session_state.selected_ticket
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"#{ticket['id']} - {ticket['title']}")
            st.write("**Description:**")
            st.write(ticket['description'])
            
            if ticket['resolution']:
                st.write("**Resolution:**")
                st.write(ticket['resolution'])
        
        with col2:
            st.write("**Priority:**", ticket['priority'])
            st.write("**Status:**", ticket['status'])
            st.write("**Category:**", ticket['category'])
            st.write("**Assigned To:**", ticket['assigned_to'])
            st.write("**Reporter:**", ticket['reporter'])
            st.write("**Company:**", ticket['company_id'])
            st.write("**Source:**", ticket['source'])
            st.write("**Created:**", format_date(ticket['created_date']))
            st.write("**Due:**", format_date(ticket['due_date']))
            if ticket['tags']:
                st.write("**Tags:**", ticket['tags'])
    else:
        st.error("No ticket selected")
    
    if st.button("← Back to Tickets"):
        st.session_state.page = 'tickets'
        st.session_state.selected_ticket = None
        st.rerun()

def show_edit_ticket_page():
    if not require_auth('can_manage_tickets'):
        return
    
    st.title("✏️ Edit Ticket")
    st.info("Ticket editing interface coming soon!")
    
    if st.button("← Back to Tickets"):
        st.session_state.page = 'tickets'
        st.session_state.selected_ticket = None
        st.rerun()

# Main App Router
def main():
    try:
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
            show_new_ticket_page()
        elif st.session_state.page == 'users':
            show_users_page()
        elif st.session_state.page == 'new_user':
            show_new_user_page()
        elif st.session_state.page == 'edit_user':
            show_edit_user_page()
        elif st.session_state.page == 'settings':
            show_settings_page()
        elif st.session_state.page == 'ticket_details':
            show_ticket_details_page()
        elif st.session_state.page == 'edit_ticket':
            show_edit_ticket_page()
        else:
            st.session_state.page = 'login'
            st.rerun()
            
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please refresh the page to continue.")

if __name__ == "__main__":
    main() __init__(self, db_path="flowtls_professional.db"):
        self.db_path = db_path
        self._init_database()
    
    def get_connection(self):
        try:
            conn = sqlite3.connect(
                self.db_path, 
                check_same_thread=False,
                timeout=20.0,
                isolation_level=None
            )
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=1000")
            conn.execute("PRAGMA temp_store=MEMORY")
            return conn
        except Exception as e:
            st.error(f"Database connection error: {str(e)}")
            raise
    
    def _init_database(self):
        with db_lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                # Enhanced user table with permissions
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
                        email_notifications INTEGER DEFAULT 1
                    );
                    
                    CREATE TABLE IF NOT EXISTS tickets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        priority TEXT DEFAULT 'Medium',
                        status TEXT DEFAULT 'Open',
                        assigned_to TEXT DEFAULT '',
                        assigned_to_id INTEGER DEFAULT 0,
                        category TEXT DEFAULT 'General',
                        subcategory TEXT DEFAULT '',
                        created_date TEXT NOT NULL,
                        updated_date TEXT,
                        due_date TEXT,
                        reporter TEXT DEFAULT '',
                        reporter_id INTEGER DEFAULT 0,
                        resolution TEXT DEFAULT '',
                        tags TEXT DEFAULT '',
                        estimated_hours REAL DEFAULT 0,
                        actual_hours REAL DEFAULT 0,
                        company_id TEXT DEFAULT '',
                        source TEXT DEFAULT 'Manual',
                        email_thread_id TEXT DEFAULT ''
                    );
                    
                    CREATE TABLE IF NOT EXISTS ticket_comments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticket_id INTEGER NOT NULL,
                        user_name TEXT NOT NULL,
                        user_id INTEGER DEFAULT 0,
                        comment TEXT NOT NULL,
                        is_internal INTEGER DEFAULT 0,
                        created_date TEXT NOT NULL,
                        FOREIGN KEY (ticket_id) REFERENCES tickets (id)
                    );
                    
                    CREATE TABLE IF NOT EXISTS email_settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        setting_name TEXT UNIQUE NOT NULL,
                        setting_value TEXT NOT NULL,
                        created_date TEXT NOT NULL,
                        updated_date TEXT
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
                
                # Check and create default data
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
            {
                'username': 'admin',
                'email': 'admin@flowtls.com',
                'password': 'admin123',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'Admin',
                'department': 'IT',
                'phone': '+1-555-0001',
                'company_id': 'FLOWTLS001',
                'can_create_users': 1,
                'can_deactivate_users': 1,
                'can_reset_passwords': 1,
                'can_manage_tickets': 1,
                'can_view_all_tickets': 1,
                'can_delete_tickets': 1,
                'can_export_data': 1
            },
            {
                'username': 'jsmith',
                'email': 'john.smith@flowtls.com',
                'password': 'password123',
                'first_name': 'John',
                'last_name': 'Smith',
                'role': 'Manager',
                'department': 'Support',
                'phone': '+1-555-0002',
                'company_id': 'FLOWTLS001',
                'can_create_users': 0,
                'can_deactivate_users': 0,
                'can_reset_passwords': 0,
                'can_manage_tickets': 1,
                'can_view_all_tickets': 1,
                'can_delete_tickets': 0,
                'can_export_data': 1
            },
            {
                'username': 'achen',
                'email': 'alice.chen@flowtls.com',
                'password': 'password123',
                'first_name': 'Alice',
                'last_name': 'Chen',
                'role': 'Agent',
                'department': 'Technical',
                'phone': '+1-555-0003',
                'company_id': 'FLOWTLS001',
                'can_create_users': 0,
                'can_deactivate_users': 0,
                'can_reset_passwords': 0,
                'can_manage_tickets': 1,
                'can_view_all_tickets': 1,
                'can_delete_tickets': 0,
                'can_export_data': 0
            },
            {
                'username': 'sjohnson',
                'email': 'sarah.johnson@flowtls.com',
                'password': 'password123',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': 'User',
                'department': 'Operations',
                'phone': '+1-555-0005',
                'company_id': 'CLIENT001',
                'can_create_users': 0,
                'can_deactivate_users': 0,
                'can_reset_passwords': 0,
                'can_manage_tickets': 0,
                'can_view_all_tickets': 0,
                'can_delete_tickets': 0,
                'can_export_data': 0
            }
        ]
        
        for user_data in users:
            try:
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
                    datetime.now().isoformat(), 'System',
                    user_data['can_create_users'], user_data['can_deactivate_users'],
                    user_data['can_reset_passwords'], user_data['can_manage_tickets'],
                    user_data['can_view_all_tickets'], user_data['can_delete_tickets'],
                    user_data['can_export_data']
                ))
            except Exception as e:
                st.error(f"Error creating user {user_data['username']}: {str(e)}")
    
    def _create_sample_tickets(self, cursor):
        sample_tickets = [
            ("FlowTLS Integration Critical Error", "System integration completely failing - production down", "Critical", "Open", "John Smith", "Integration", "System Integration", "Sarah Johnson", "urgent,integration,flowtls,production", "CLIENT001"),
            ("User Authentication SSO Issues", "Multiple users unable to login with SSO affecting entire department", "High", "In Progress", "Alice Chen", "Security", "Authentication", "System Administrator", "sso,login,authentication,department", "CLIENT002"),
            ("Database Performance Degradation", "Customer reports taking 30+ seconds to load, needs immediate optimization", "High", "Open", "Alice Chen", "Performance", "Database", "John Smith", "performance,database,reports,slow", "CLIENT001"),
            ("UI Modernization Project", "Update interface design to match new corporate brand guidelines", "Medium", "Open", "Alice Chen", "Enhancement", "User Interface", "Sarah Johnson", "ui,enhancement,design,branding", "FLOWTLS001"),
            ("Email Notification System", "Configure automated email alerts for high priority tickets", "Medium", "Resolved", "John Smith", "Configuration", "Email System", "System Administrator", "email,notifications,alerts", "FLOWTLS001"),
        ]
        
        for i, (title, desc, priority, status, assigned_to, category, subcategory, reporter, tags, company_id) in enumerate(sample_tickets):
            try:
                hours_to_add = {"Critical": 4, "High": 8, "Medium": 24, "Low": 72}[priority]
                due_date = datetime.now() + timedelta(hours=hours_to_add)
                
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
            ("CLIENT002", "TechStart Inc", "help@techstart.com", "+1-555-2000", "789 Innovation Dr, Austin, TX"),
        ]
        
        for company_id, name, email, phone, address in companies:
            try:
                cursor.execute("""
                    INSERT INTO companies (company_id, company_name, contact_email, phone, address, created_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (company_id, name, email, phone, address, datetime.now().isoformat()))
            except Exception as e:
                st.error(f"Error creating company {company_id}: {str(e)}")

# Enhanced Authentication Service
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
                    'company_id': user[9],
                    'permissions': {
                        'can_create_users': bool(user[11]),
                        'can_deactivate_users': bool(user[12]),
                        'can_reset_passwords': bool(user[13]),
                        'can_manage_tickets': bool(user[14]),
                        'can_view_all_tickets': bool(user[15]),
                        'can_delete_tickets': bool(user[16]),
                        'can_export_data': bool(user[17])
                    }
                }
                
                conn.commit()
                conn.close()
                
                return True, user_data, ""
                
            except Exception as e:
                return False, None, f"Authentication error: {str(e)}"

# Enhanced User Management Service
class UserService:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_all_users(self, include_inactive=False):
        with db_lock:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                if include_inactive:
                    cursor.execute("""
                        SELECT id, username, email, first_name, last_name, role, department, 
                               company_id, is_active, created_date, last_login_date, created_by,
                               can_create_users, can_deactivate_users, can_reset_passwords,
                               can_manage_tickets, can_view_all_tickets, can_delete_tickets,
                               can_export_data, phone
                        FROM users ORDER BY created_date DESC
                    """)
                else:
                    cursor.execute("""
                        SELECT id, username, email, first_name, last_name, role, department, 
                               company_id, is_active, created_date, last_login_date, created_by,
                               can_create_users, can_deactivate_users, can_reset_passwords,
                               can_manage_tickets, can_view_all_tickets, can_delete_tickets,
                               can_export_data, phone
                        FROM users WHERE is_active = 1 ORDER BY created_date DESC
                    """)
                
                users = []
                for row in cursor.fetchall():
                    user = {
                        'id': row[0],
                        'username': row[1],
                        'email': row[2],
                        'first_name': row[3],
                        'last_name': row[4],
                        'full_name': f"{row[3]} {row[4]}".strip(),
                        'role': row[5],
                        'department': row[6],
                        'company_id': row[7],
                        'is_active': bool(row[8]),
                        'created_date': row[9],
                        'last_login_date': row[10],
                        'created_by': row[11],
                        'permissions': {
                            'can_create_users': bool(row[12]),
                            'can_deactivate_users': bool(row[13]),
                            'can_reset_passwords': bool(row[14]),
                            'can_manage_tickets': bool(row[15]),
                            'can_view_all_tickets': bool(row[16]),
                            'can_delete_tickets': bool(row[17]),
                            'can_export_data': bool(row[18])
                        },
                        'phone': row[19]
                    }
                    users.append(user)
                
                conn.close()
                return users
                
            except Exception as e:
                st.error(f"Error retrieving users: {str(e)}")
                return []
    
    def create_user(self, user_data: Dict, created_by: str) -> bool:
        with db_lock:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                # Generate salt and hash password
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
                    user_data['department'], user_data.get('phone', ''), user_data.get('company_id', ''),
                    datetime.now().isoformat(), created_by,
                    user_data.get('can_create_users', 0), user_data.get('can_deactivate_users', 0),
                    user_data.get('can_reset_passwords', 0), user_data.get('can_manage_tickets', 0),
                    user_data.get('can_view_all_tickets', 0), user_data.get('can_delete_tickets', 0),
                    user_data.get('can_export_data', 0)
                ))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                st.error(f"Error creating user: {str(e)}")
                return False
    
    def update_user(self, user_id: int, user_data: Dict) -> bool:
        with db_lock:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE users SET first_name=?, last_name=?, role=?, department=?, phone=?,
                                   company_id=?, can_create_users=?, can_deactivate_users=?,
                                   can_reset_passwords=?, can_manage_tickets=?, can_view_all_tickets=?,
                                   can_delete_tickets=?, can_export_data=?
                    WHERE id=?
                """, (
                    user_data['first_name'], user_data['last_name'], user_data['role'],
                    user_data['department'], user_data.get('phone', ''), user_data.get('company_id', ''),
                    user_data.get('can_create_users', 0), user_data.get('can_deactivate_users', 0),
                    user_data.get('can_reset_passwords', 0), user_data.get('can_manage_tickets', 0),
                    user_data.get('can_view_all_tickets', 0), user_data.get('can_delete_tickets', 0),
                    user_data.get('can_export_data', 0), user_id
                ))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                st.error(f"Error updating user: {str(e)}")
                return False
    
    def
"""
Smart College Queue Token Management System
Single file Streamlit application - Run with: streamlit run app.py
"""

import streamlit as st
from datetime import datetime
import time

# ------------------------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SmartQueue · College Token System",
    page_icon="🎟️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------------------------
# Initialize session state (our "database")
# ------------------------------------------------------------------------------
if 'initialized' not in st.session_state:
    # Departments
    st.session_state.departments = ['Student Section', 'Accounts Section', 'Bus Line', 'Canteen']
    
    # Queue state for each department
    st.session_state.queue_state = {}
    for dept in st.session_state.departments:
        st.session_state.queue_state[dept] = {
            'current': 10,        # current serving token
            'last': 15,           # last issued token
            'paused': False,
            'avg_wait_min': 2      # minutes per token for estimation
        }
    
    # Time slots
    st.session_state.time_slots = {
        'Slot 1': '8:30 AM - 10:30 AM',
        'Slot 2': '11:00 AM - 1:00 PM',
        'Slot 3': '2:00 PM - 4:30 PM'
    }
    
    # Student data
    st.session_state.students = {
        'S001': {'name': 'Alex Johnson', 'password': 'pass123', 'dept': None, 'token': None, 'slot': None},
        'S002': {'name': 'Maria Garcia', 'password': 'pass123', 'dept': None, 'token': None, 'slot': None},
        'S003': {'name': 'Kim Lee', 'password': 'pass123', 'dept': None, 'token': None, 'slot': None},
    }
    
    # Admin credentials
    st.session_state.admins = {
        'admin1': {'password': 'admin123', 'dept': None}
    }
    
    # Navigation state
    st.session_state.page = 'home'
    st.session_state.logged_in = False
    st.session_state.user_type = None
    st.session_state.user_id = None
    st.session_state.selected_dept = None
    
    st.session_state.initialized = True

# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------
def get_queue_data(dept):
    """Return queue state for a department"""
    return st.session_state.queue_state.get(dept, {'current': 0, 'last': 0, 'paused': False})

def get_next_token(dept):
    """Generate next token for department"""
    st.session_state.queue_state[dept]['last'] += 1
    return st.session_state.queue_state[dept]['last']

def people_ahead(dept, token):
    """Calculate number of people ahead of given token"""
    state = st.session_state.queue_state.get(dept)
    if not state or token is None:
        return 0
    if token <= state['current']:
        return 0
    return token - state['current'] - 1

def waiting_time(dept, token):
    """Estimate waiting time in minutes"""
    ahead = people_ahead(dept, token)
    avg = st.session_state.queue_state.get(dept, {}).get('avg_wait_min', 2)
    return ahead * avg

def logout():
    st.session_state.logged_in = False
    st.session_state.user_type = None
    st.session_state.user_id = None
    st.session_state.page = 'home'
    st.rerun()

# ------------------------------------------------------------------------------
# Custom CSS for modern UI with darker headings
# ------------------------------------------------------------------------------
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(145deg, #f0f5fe 0%, #e9f0fa 100%);
    }
    
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 1rem;
    }
    
    /* Darker headings */
    h1, h2, h3, h4, h5, h6 {
        color: #0a1e3c !important;
        font-weight: 700 !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
    }
    
    h2 {
        font-size: 2rem !important;
        font-weight: 700 !important;
        border-bottom: 3px solid #2563eb30;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem !important;
    }
    
    h3 {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
    }
    
    /* Card styles */
    .custom-card {
        background: white;
        border-radius: 2.5rem;
        padding: 2.5rem 2rem;
        text-align: center;
        box-shadow: 0 12px 30px -8px rgba(25, 60, 120, 0.15);
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.8);
        margin: 1rem 0;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 25px 35px -10px rgba(37, 99, 235, 0.3);
    }
    
    .portal-icon {
        background: #dbeafe;
        width: 80px;
        height: 80px;
        border-radius: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.5rem;
        font-size: 2.2rem;
        color: #2563eb;
    }
    
    /* Token badge */
    .token-badge {
        background: #2563eb;
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        padding: 0.5rem 2rem;
        border-radius: 4rem;
        display: inline-block;
        margin: 0.5rem 0;
    }
    
    .token-badge-small {
        background: #1e293b;
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        padding: 0.3rem 1.5rem;
        border-radius: 3rem;
        display: inline-block;
    }
    
    /* Confirmation badge */
    .confirmation-badge {
        background: #10b981;
        color: white;
        font-size: 1.2rem;
        font-weight: 600;
        padding: 0.8rem 2rem;
        border-radius: 3rem;
        display: inline-block;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    /* Stat cards */
    .stat-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-item {
        background: #f8fafc;
        border-radius: 1.5rem;
        padding: 1.2rem 1.5rem;
        flex: 1 1 140px;
        border-left: 4px solid #2563eb;
    }
    
    .stat-label {
        color: #475569;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    
    /* Paused warning */
    .paused-warning {
        background: #fff3cd;
        border: 1px solid #ffe69c;
        border-radius: 3rem;
        padding: 1rem 2rem;
        color: #856404;
        font-weight: 600;
        margin: 1.5rem 0;
    }
    
    /* Admin bar */
    .admin-bar {
        background: #f1f5f9;
        border-radius: 2rem;
        padding: 1.5rem 2rem;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        margin: 1.5rem 0;
        gap: 1rem;
    }
    
    .big-number {
        font-size: 2.8rem;
        font-weight: 700;
        color: #0a1e3c;
        line-height: 1;
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        border-radius: 2rem !important;
        border: 1.5px solid #e2e8f0 !important;
        padding: 0.8rem 1.2rem !important;
    }
    
    .stSelectbox > div > div > select {
        border-radius: 2rem !important;
        border: 1.5px solid #e2e8f0 !important;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 3rem !important;
        font-weight: 600 !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.2s !important;
    }
    
    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Divider */
    .custom-divider {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #2563eb40, transparent);
        margin: 2rem 0;
    }
    
    /* Welcome message styling */
    .welcome-text {
        color: #0a1e3c;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    /* Slot card */
    .slot-card {
        background: #f0f9ff;
        border: 2px solid #bae6fd;
        border-radius: 1.5rem;
        padding: 1rem;
        text-align: center;
        font-weight: 600;
        color: #0369a1;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# Header with home button
# ------------------------------------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("🏠 Home", use_container_width=True):
        logout()
with col2:
    st.markdown("<h2 style='text-align: center; color: #0a1e3c; font-weight: 800;'>🎟️ SmartQueue · College</h2>", unsafe_allow_html=True)
with col3:
    if st.session_state.logged_in:
        st.markdown(f"<p style='text-align: right; color: #1e293b; font-weight: 600;'>👤 {st.session_state.user_type}</p>", unsafe_allow_html=True)

st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# Page routing
# ------------------------------------------------------------------------------
if not st.session_state.logged_in:
    # HOME PAGE
    if st.session_state.page == 'home':
        st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>Welcome to SmartQueue</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class='custom-card'>
                <div class='portal-icon'>👨‍🎓</div>
                <h3>Student Portal</h3>
                <p style='color: #4b5563;'>Get token, track queue</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Student Portal", key="student_home", use_container_width=True):
                st.session_state.page = 'student_login'
                st.rerun()
        
        with col2:
            st.markdown("""
            <div class='custom-card'>
                <div class='portal-icon'>👩‍🏫</div>
                <h3>Admin Portal</h3>
                <p style='color: #4b5563;'>Manage queues & tokens</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Admin Portal", key="admin_home", use_container_width=True):
                st.session_state.page = 'admin_login'
                st.rerun()
        
        st.markdown("<p style='text-align: center; color: #475569; font-weight: 500; margin-top: 2rem;'>⬆️ choose a portal to continue</p>", unsafe_allow_html=True)
    
    # STUDENT LOGIN PAGE
    elif st.session_state.page == 'student_login':
        st.markdown("<h1 style='text-align: center; margin-bottom: 1rem;'>🔐 Student Login</h1>", unsafe_allow_html=True)
        
        with st.form("student_login_form"):
            student_id = st.text_input("Student ID", placeholder="Enter any ID")
            password = st.text_input("Password", type="password", placeholder="Enter any password")
            department = st.selectbox("Department", st.session_state.departments)
            
            submitted = st.form_submit_button("Login & Continue", use_container_width=True)
            
            if submitted:
                # Accept any credentials - no validation
                st.session_state.logged_in = True
                st.session_state.user_type = 'student'
                st.session_state.user_id = student_id if student_id else "Guest"
                
                # Create student entry if doesn't exist
                if student_id not in st.session_state.students:
                    st.session_state.students[student_id] = {
                        'name': f'Student {student_id}' if student_id else 'Guest Student',
                        'password': password,
                        'dept': department,
                        'token': None,
                        'slot': None
                    }
                
                st.session_state.selected_dept = department
                st.session_state.students[student_id]['dept'] = department
                st.session_state.students[student_id]['token'] = None
                st.session_state.students[student_id]['slot'] = None
                st.session_state.page = 'student_dashboard'
                st.rerun()
        
        if st.button("← Back to Home"):
            st.session_state.page = 'home'
            st.rerun()
    
    # ADMIN LOGIN PAGE
    elif st.session_state.page == 'admin_login':
        st.markdown("<h1 style='text-align: center; margin-bottom: 1rem;'>👩‍🏫 Admin Login</h1>", unsafe_allow_html=True)
        
        with st.form("admin_login_form"):
            admin_id = st.text_input("Admin ID", placeholder="Enter any admin ID")
            password = st.text_input("Password", type="password", placeholder="Enter any password")
            department = st.selectbox("Department", st.session_state.departments)
            
            submitted = st.form_submit_button("Access Dashboard", use_container_width=True)
            
            if submitted:
                # Accept any credentials - no validation
                st.session_state.logged_in = True
                st.session_state.user_type = 'admin'
                st.session_state.user_id = admin_id if admin_id else "Admin"
                
                # Create admin entry if doesn't exist
                if admin_id not in st.session_state.admins:
                    st.session_state.admins[admin_id] = {
                        'password': password,
                        'dept': department
                    }
                
                st.session_state.selected_dept = department
                st.session_state.admins[admin_id]['dept'] = department
                st.session_state.page = 'admin_dashboard'
                st.rerun()
        
        if st.button("← Back to Home"):
            st.session_state.page = 'home'
            st.rerun()

else:
    # STUDENT DASHBOARD
    if st.session_state.user_type == 'student':
        student_id = st.session_state.user_id
        student = st.session_state.students.get(student_id, {'name': f'Student {student_id}'})
        dept = st.session_state.selected_dept
        q = st.session_state.queue_state[dept]
        my_token = student.get('token')
        my_slot = student.get('slot')
        ahead = people_ahead(dept, my_token) if my_token else 0
        wait = waiting_time(dept, my_token) if my_token else 0
        total_waiting = q['last'] - q['current']
        
        st.markdown(f"<h1 class='welcome-text'>👋 Welcome, {student['name']}</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🚪 Logout", use_container_width=True):
                logout()
        
        st.markdown(f"<h2 style='margin-top: 1rem;'>{dept}</h2>", unsafe_allow_html=True)
        
        if q['paused']:
            st.markdown("""
            <div class='paused-warning'>
                ⏸️ Queue has been temporarily paused. Please wait.
            </div>
            """, unsafe_allow_html=True)
        
        # Token display
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<p class='stat-label'>Current serving</p>", unsafe_allow_html=True)
            st.markdown(f"<div class='token-badge'>{q['current']}</div>", unsafe_allow_html=True)
        
        if my_token:
            with col2:
                st.markdown("<p class='stat-label'>Your token</p>", unsafe_allow_html=True)
                st.markdown(f"<div class='token-badge-small'>{my_token}</div>", unsafe_allow_html=True)
        
        # Token generation with time slot selection
        if not my_token:
            st.markdown("<h3>Select Time Slot</h3>", unsafe_allow_html=True)
            
            # Display time slots
            slot_cols = st.columns(3)
            selected_slot = None
            
            with slot_cols[0]:
                st.markdown(f"""
                <div class='slot-card'>
                    🕐 Slot 1<br>
                    {st.session_state.time_slots['Slot 1']}
                </div>
                """, unsafe_allow_html=True)
                if st.button("Select Slot 1", key="slot1", use_container_width=True):
                    selected_slot = 'Slot 1'
            
            with slot_cols[1]:
                st.markdown(f"""
                <div class='slot-card'>
                    🕑 Slot 2<br>
                    {st.session_state.time_slots['Slot 2']}
                </div>
                """, unsafe_allow_html=True)
                if st.button("Select Slot 2", key="slot2", use_container_width=True):
                    selected_slot = 'Slot 2'
            
            with slot_cols[2]:
                st.markdown(f"""
                <div class='slot-card'>
                    🕒 Slot 3<br>
                    {st.session_state.time_slots['Slot 3']}
                </div>
                """, unsafe_allow_html=True)
                if st.button("Select Slot 3", key="slot3", use_container_width=True):
                    selected_slot = 'Slot 3'
            
            if selected_slot:
                new_token = get_next_token(dept)
                st.session_state.students[student_id]['token'] = new_token
                st.session_state.students[student_id]['slot'] = selected_slot
                st.rerun()
        
        else:
            # Confirmation message
            st.markdown(f"""
            <div style='text-align: center; margin: 1.5rem 0;'>
                <div class='confirmation-badge'>
                    ✅ YOUR SEAT HAS BEEN CONFIRMED!
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display selected slot
            if my_slot:
                st.markdown(f"""
                <div style='background: #dbeafe; border-radius: 2rem; padding: 1rem; margin: 1rem 0; text-align: center;'>
                    <span style='font-weight: 600; color: #1e40af;'>📅 Your selected time: {st.session_state.time_slots[my_slot]}</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Statistics
            cols = st.columns(3)
            with cols[0]:
                st.markdown("""
                <div class='stat-item'>
                    <div class='stat-label'>People ahead</div>
                    <div class='stat-value'>{}<div>
                </div>
                """.format(ahead), unsafe_allow_html=True)
            with cols[1]:
                st.markdown("""
                <div class='stat-item'>
                    <div class='stat-label'>Est. waiting</div>
                    <div class='stat-value'>{} min<div>
                </div>
                """.format(wait), unsafe_allow_html=True)
            with cols[2]:
                st.markdown("""
                <div class='stat-item'>
                    <div class='stat-label'>Total waiting</div>
                    <div class='stat-value'>{}<div>
                </div>
                """.format(total_waiting), unsafe_allow_html=True)
            
            st.markdown("<p style='color: #1e293b;'><i class='fas fa-sync-alt'></i> 🔄 Refresh page for updates</p>", unsafe_allow_html=True)
    
    # ADMIN DASHBOARD
    elif st.session_state.user_type == 'admin':
        dept = st.session_state.selected_dept
        q = st.session_state.queue_state[dept]
        waiting_count = q['last'] - q['current']
        next_token = q['current'] + 1 if q['current'] < q['last'] else q['current']
        
        st.markdown(f"<h1>⚙️ {dept}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='margin-top: 0;'>Admin Panel</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🚪 Logout", use_container_width=True):
                logout()
        
        # Admin control bar
        st.markdown("""
        <div class='admin-bar'>
            <div>
                <span class='stat-label'>Current token</span>
                <div class='big-number'>{}</div>
            </div>
            <div>
                <span class='stat-label'>Last token</span>
                <div class='big-number'>{}</div>
            </div>
            <div>
                <span class='stat-label'>Waiting</span>
                <div class='big-number'>{}</div>
            </div>
        </div>
        """.format(q['current'], q['last'], waiting_count), unsafe_allow_html=True)
        
        # Control buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("➡️ NEXT", use_container_width=True):
                if not q['paused'] and q['current'] < q['last']:
                    st.session_state.queue_state[dept]['current'] += 1
                    st.rerun()
                elif q['paused']:
                    st.warning("Queue is paused. Resume first.")
                else:
                    st.warning("No more tokens waiting.")
        
        with col2:
            if not q['paused']:
                if st.button("⏸️ STOP", use_container_width=True):
                    st.session_state.queue_state[dept]['paused'] = True
                    st.rerun()
        
        with col3:
            if q['paused']:
                if st.button("▶️ RESUME", use_container_width=True):
                    st.session_state.queue_state[dept]['paused'] = False
                    st.rerun()
        
        # Status display
        status_color = "#047857" if not q['paused'] else "#b45309"
        status_text = "▶️ RUNNING" if not q['paused'] else "⏸️ PAUSED"
        
        st.markdown(f"""
        <div style="background:white; border-radius:2rem; padding:1.5rem; margin-top:2rem; border: 1px solid #e2e8f0;">
            <p style="font-weight: 600; color: #0a1e3c;"><strong>Queue status:</strong> <span style="color:{status_color};">{status_text}</span></p>
            <p style="font-weight: 600; color: #0a1e3c;"><strong>Next token to call:</strong> {next_token}</p>
            <p style="font-weight: 600; color: #0a1e3c;"><strong>Department:</strong> {dept}</p>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------------------
st.markdown("""
<div style='text-align: center; margin-top: 3rem; padding: 1rem; color: #475569; font-size: 0.9rem; font-weight: 500;'>
    <hr style='margin: 1rem 0; border: none; border-top: 1px solid #94a3b8;'>
    🎟️ digital token system · college mini project
</div>
""", unsafe_allow_html=True)
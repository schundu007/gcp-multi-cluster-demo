#!/usr/bin/env python3
"""
CIROOS - Multi-Cluster Network Security Demo
2-Page Structure: Overview → Demo
"""

import streamlit as st
import subprocess
import time
import socket
import os
from datetime import datetime

st.set_page_config(
    page_title="CIROOS Demo",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Styles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&display=swap');

    html, body, .stApp, .main, [data-testid="stAppViewContainer"],
    .block-container, [data-testid="stVerticalBlock"] {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%) !important;
        color: #F8FAFC !important;
    }

    #MainMenu, footer, header, [data-testid="stHeader"] { display: none !important; }

    .block-container { padding: 1rem 2rem !important; max-width: 1600px !important; }

    *, p, span, div, label { font-family: 'Outfit', sans-serif !important; color: #F8FAFC !important; }
    h1, h2, h3, h4 { font-family: 'Orbitron', sans-serif !important; color: #F8FAFC !important; letter-spacing: 1px; }

    .section-header {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 0.8rem;
        color: #FF6400 !important;
        -webkit-text-fill-color: #FF6400 !important;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255, 100, 0, 0.3);
    }

    .metric-card {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.6rem;
        text-align: center;
        position: relative;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #FF6400, #FF8533);
    }
    .metric-value {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 1.3rem;
        font-weight: 800;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    .metric-label {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 0.55rem;
        color: #64748B !important;
        -webkit-text-fill-color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .service-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        background: rgba(30, 41, 59, 0.5);
        border-radius: 8px;
        margin-bottom: 6px;
        border-left: 3px solid transparent;
    }
    .service-row.active { border-left-color: #10B981; }
    .service-row.blocked { border-left-color: #EF4444; }

    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 20px;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .live-connected {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10B981;
        color: #10B981 !important;
        -webkit-text-fill-color: #10B981 !important;
    }
    .live-blocked {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid #EF4444;
        color: #EF4444 !important;
        -webkit-text-fill-color: #EF4444 !important;
    }

    .stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important; }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Space Grotesk', sans-serif !important;
        background: transparent !important;
        color: #64748B !important;
        font-weight: 500;
        padding: 0.75rem 1.25rem;
        font-size: 0.8rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .stTabs [aria-selected="true"] { color: #FF6400 !important; border-bottom: 2px solid #FF6400 !important; }

    div[data-testid="stButton"] button {
        font-family: 'Space Grotesk', sans-serif !important;
        background: linear-gradient(135deg, #FF6400, #FF8533) !important;
        border: none !important;
        color: white !important;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        border-radius: 6px;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-size: 0.8rem;
    }

    .countdown {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 5rem;
        font-weight: 900;
        color: #EF4444 !important;
        -webkit-text-fill-color: #EF4444 !important;
        text-align: center;
        text-shadow: 0 0 50px rgba(239, 68, 68, 0.8);
    }

    a { color: #FF6400 !important; text-decoration: none; }
    hr { border: none !important; border-top: 1px solid rgba(255, 255, 255, 0.1) !important; margin: 1rem 0 !important; }

    /* SRE Alert Animations */
    @keyframes siren-pulse {
        0%, 100% { opacity: 1; box-shadow: 0 0 20px rgba(239, 68, 68, 0.8); }
        50% { opacity: 0.7; box-shadow: 0 0 40px rgba(239, 68, 68, 1), 0 0 60px rgba(239, 68, 68, 0.6); }
    }
    @keyframes scroll-left {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    @keyframes blink {
        0%, 50%, 100% { opacity: 1; }
        25%, 75% { opacity: 0.3; }
    }
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-2px); }
        20%, 40%, 60%, 80% { transform: translateX(2px); }
    }
    .alert-banner {
        background: linear-gradient(90deg, #7f1d1d, #991b1b, #7f1d1d);
        padding: 12px 20px;
        border-radius: 8px;
        animation: siren-pulse 1s ease-in-out infinite;
        margin-bottom: 16px;
    }
    .alert-ticker {
        background: #0f0f0f;
        border: 1px solid #EF4444;
        border-radius: 4px;
        overflow: hidden;
        padding: 8px 0;
        margin-bottom: 12px;
    }
    .ticker-content {
        display: inline-block;
        white-space: nowrap;
        animation: scroll-left 48s linear infinite;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #EF4444;
    }
    .incident-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #7f1d1d;
        border: 2px solid #EF4444;
        padding: 4px 12px;
        border-radius: 4px;
        animation: blink 1s infinite;
    }
    .error-log {
        background: #0a0a0a;
        border: 1px solid #333;
        border-radius: 6px;
        padding: 10px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        max-height: 150px;
        overflow-y: auto;
    }
    .error-line {
        color: #EF4444;
        margin-bottom: 4px;
        padding: 2px 0;
        border-bottom: 1px solid #1a1a1a;
    }
    .warning-line {
        color: #F59E0B;
        margin-bottom: 4px;
        padding: 2px 0;
        border-bottom: 1px solid #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
GRAFANA_URL = "http://localhost:3001"
FRONTEND_URL = "http://localhost:8085"

# GCP-style SVG Icons
ICONS = {
    'gke': '''<svg viewBox="0 0 24 24" width="24" height="24"><path fill="{color}" d="M12 2L2 7v10l10 5 10-5V7L12 2zm0 2.18l6.9 3.45L12 11.09 5.1 7.63 12 4.18zM4 8.82l7 3.5v7.36l-7-3.5V8.82zm9 10.86v-7.36l7-3.5v7.36l-7 3.5z"/></svg>''',
    'service': '''<svg viewBox="0 0 24 24" width="18" height="18"><path fill="{color}" d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14zM9 7H7v2h2V7zm4 0h-2v2h2V7zm4 0h-2v2h2V7z"/></svg>''',
    'database': '''<svg viewBox="0 0 24 24" width="18" height="18"><path fill="{color}" d="M12 3C7.58 3 4 4.79 4 7v10c0 2.21 3.58 4 8 4s8-1.79 8-4V7c0-2.21-3.58-4-8-4zm0 2c3.87 0 6 1.5 6 2s-2.13 2-6 2-6-1.5-6-2 2.13-2 6-2zm6 12c0 .5-2.13 2-6 2s-6-1.5-6-2v-2.23c1.61.78 3.72 1.23 6 1.23s4.39-.45 6-1.23V17zm0-5c0 .5-2.13 2-6 2s-6-1.5-6-2V9.77C7.61 10.55 9.72 11 12 11s4.39-.45 6-1.23V12z"/></svg>''',
    'firewall': '''<svg viewBox="0 0 24 24" width="20" height="20"><path fill="{color}" d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/></svg>''',
    'vpc': '''<svg viewBox="0 0 24 24" width="20" height="20"><path fill="{color}" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>''',
    'lb': '''<svg viewBox="0 0 24 24" width="20" height="20"><path fill="{color}" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/><circle cx="12" cy="12" r="3" fill="{color}"/><path fill="{color}" d="M12 6v2M12 16v2M6 12h2M16 12h2" stroke="{color}" stroke-width="2"/></svg>''',
    'policy': '''<svg viewBox="0 0 24 24" width="20" height="20"><path fill="{color}" d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM10 17l-3.5-3.5 1.41-1.41L10 14.17l4.59-4.59L16 11l-6 6z"/></svg>''',
    'monitoring': '''<svg viewBox="0 0 24 24" width="20" height="20"><path fill="{color}" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4 6h2v4h-2z"/></svg>''',
    'app': '''<svg viewBox="0 0 24 24" width="20" height="20"><path fill="{color}" d="M4 8h4V4H4v4zm6 12h4v-4h-4v4zm-6 0h4v-4H4v4zm0-6h4v-4H4v4zm6 0h4v-4h-4v4zm6-10v4h4V4h-4zm-6 4h4V4h-4v4zm6 6h4v-4h-4v4zm0 6h4v-4h-4v4z"/></svg>''',
    'cluster': '''<svg viewBox="0 0 24 24" width="20" height="20"><path fill="{color}" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>''',
    'online': '''<svg viewBox="0 0 24 24" width="20" height="20"><path fill="{color}" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>''',
    'settings': '''<svg viewBox="0 0 24 24" width="18" height="18"><path fill="{color}" d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>''',
}

def icon(name, color="#FF6400", size=None):
    """Return an SVG icon with the specified color"""
    svg = ICONS.get(name, '')
    svg = svg.replace('{color}', color)
    if size:
        svg = svg.replace('width="24"', f'width="{size}"').replace('height="24"', f'height="{size}"')
        svg = svg.replace('width="20"', f'width="{size}"').replace('height="20"', f'height="{size}"')
        svg = svg.replace('width="18"', f'width="{size}"').replace('height="18"', f'height="{size}"')
    return svg

PORT_FORWARD_SERVICES = [
    {'name': 'Grafana', 'context': 'gke-c1', 'namespace': 'monitoring', 'service': 'grafana', 'local_port': 3001, 'remote_port': 3000},
    {'name': 'Prometheus', 'context': 'gke-c1', 'namespace': 'monitoring', 'service': 'prometheus', 'local_port': 9090, 'remote_port': 9090},
    {'name': 'Loki', 'context': 'gke-c1', 'namespace': 'monitoring', 'service': 'loki', 'local_port': 3100, 'remote_port': 3100},
    {'name': 'Frontend', 'context': 'gke-c1', 'namespace': 'bank-of-anthos', 'service': 'frontend', 'local_port': 8085, 'remote_port': 80},
]

BACKEND_SERVICES = [
    {'name': 'userservice', 'ip': '10.1.10.10', 'port': 8085},
    {'name': 'contacts', 'ip': '10.1.10.11', 'port': 8085},
    {'name': 'balancereader', 'ip': '10.1.10.12', 'port': 8085},
    {'name': 'transactionhistory', 'ip': '10.1.10.13', 'port': 8085},
    {'name': 'ledgerwriter', 'ip': '10.1.10.14', 'port': 8085},
]


def run_command(cmd, timeout=30):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except:
        return False, "", "Error"


def check_firewall_rule():
    success, stdout, _ = run_command("gcloud compute firewall-rules describe allow-c1-to-c2-app --format='value(name)' 2>/dev/null")
    return success and 'allow-c1-to-c2-app' in stdout


def test_service_connectivity(ip, port):
    cmd = f"""kubectl --context gke-c1 exec -n bank-of-anthos deploy/frontend -- python3 -c "
import urllib.request
try:
    r = urllib.request.urlopen('http://{ip}:{port}/ready', timeout=3)
    print('OK' if r.status == 200 else 'FAIL')
except:
    print('FAIL')
" 2>&1"""
    success, stdout, _ = run_command(cmd, timeout=15)
    return 'OK' in stdout


def revoke_access():
    return run_command("gcloud compute firewall-rules delete allow-c1-to-c2-app --quiet 2>&1", timeout=60)


def restore_access():
    cmd = """gcloud compute firewall-rules create allow-c1-to-c2-app \
        --network=vpc-c1 --direction=EGRESS --priority=1000 \
        --destination-ranges=10.1.0.0/16,10.1.16.0/20 \
        --allow=tcp:8085 2>&1"""
    return run_command(cmd, timeout=60)


def check_port(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False


def get_pod_count(context):
    success, stdout, _ = run_command(f"kubectl --context {context} get pods -n bank-of-anthos --no-headers 2>/dev/null | grep Running | wc -l")
    return int(stdout.strip()) if success and stdout.strip().isdigit() else 0


# Initialize session state
if 'service_statuses' not in st.session_state:
    st.session_state.service_statuses = {}
if 'demo_running' not in st.session_state:
    st.session_state.demo_running = False

PAGES = ['overview', 'architecture', 'workflow', 'demo']

# Use query params to persist current page across refreshes
if 'current_page' not in st.session_state:
    page_param = st.query_params.get('page', 'overview')
    st.session_state.current_page = page_param if page_param in PAGES else 'overview'

def render_header():
    """Render the common header with navigation"""
    st.markdown("""
    <div style="text-align: center; padding: 20px 0 15px;">
        <div style="font-family: Orbitron; font-size: 2.5rem; font-weight: 900; background: linear-gradient(135deg, #FF6400, #FF8533, #FFB380); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 6px;">CIROOS</div>
        <div style="font-family: Space Grotesk; font-size: 0.9rem; color: #94A3B8; letter-spacing: 3px; text-transform: uppercase; margin-top: 4px;">Multi-Cluster Network Security</div>
    </div>
    """, unsafe_allow_html=True)

def render_progress():
    """Render page progress indicator"""
    page_idx = PAGES.index(st.session_state.current_page)
    page_labels = ['OVERVIEW', 'ARCHITECTURE', 'WORKFLOW', 'DEMO']

    progress_html = '<div style="display: flex; justify-content: center; align-items: center; gap: 8px; margin: 10px 0 20px;">'
    for i, label in enumerate(page_labels):
        if i < page_idx:
            # Completed
            progress_html += f'<div style="width: 10px; height: 10px; border-radius: 50%; background: #10B981;"></div>'
        elif i == page_idx:
            # Current
            progress_html += f'<div style="padding: 4px 12px; background: linear-gradient(135deg, #FF6400, #FF8533); border-radius: 12px; font-family: Orbitron; font-size: 0.65rem; color: #fff;">{label}</div>'
        else:
            # Upcoming
            progress_html += f'<div style="width: 10px; height: 10px; border-radius: 50%; background: #334155; border: 1px solid #64748B;"></div>'
        if i < len(page_labels) - 1:
            line_color = '#10B981' if i < page_idx else '#334155'
            progress_html += f'<div style="width: 40px; height: 2px; background: {line_color};"></div>'
    progress_html += '</div>'
    st.markdown(progress_html, unsafe_allow_html=True)

def navigate_to(page):
    """Navigate to a page and update URL"""
    st.session_state.current_page = page
    st.query_params['page'] = page
    st.rerun()

def nav_buttons(back_page=None, next_page=None, next_label="NEXT"):
    """Render navigation buttons"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if back_page:
            if st.button("← BACK", key=f"back_{back_page}", use_container_width=True):
                navigate_to(back_page)
    with col3:
        if next_page:
            if st.button(f"{next_label} →", key=f"next_{next_page}", use_container_width=True):
                navigate_to(next_page)


# ============================================
# PAGE 1: OVERVIEW
# ============================================
if st.session_state.current_page == 'overview':

    render_header()
    render_progress()
    st.markdown("---")

    # Problem Statement
    st.markdown('<div class="section-header">The Challenge</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
        <div style="background: linear-gradient(135deg, #1E293B, #334155); border: 1px solid rgba(255,100,0,0.3); border-radius: 12px; padding: 20px; position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: linear-gradient(180deg, #FF6400, #FF8533);"></div>
            <div style="font-family: Orbitron; font-size: 2rem; color: #FF6400; margin-bottom: 8px;">01</div>
            <div style="font-family: Orbitron; font-size: 0.75rem; color: #FF6400; letter-spacing: 1px; margin-bottom: 8px;">CROSS-REGION</div>
            <div style="font-size: 0.85rem; color: #94A3B8; line-height: 1.5;">Enable private communication between Kubernetes clusters across multiple GCP regions</div>
        </div>
        <div style="background: linear-gradient(135deg, #1E293B, #334155); border: 1px solid rgba(255,100,0,0.3); border-radius: 12px; padding: 20px; position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: linear-gradient(180deg, #FF6400, #FF8533);"></div>
            <div style="font-family: Orbitron; font-size: 2rem; color: #FF6400; margin-bottom: 8px;">02</div>
            <div style="font-family: Orbitron; font-size: 0.75rem; color: #FF6400; letter-spacing: 1px; margin-bottom: 8px;">ZERO-TRUST</div>
            <div style="font-size: 0.85rem; color: #94A3B8; line-height: 1.5;">No public endpoints, no external IPs, no ingress — completely private infrastructure</div>
        </div>
        <div style="background: linear-gradient(135deg, #1E293B, #334155); border: 1px solid rgba(255,100,0,0.3); border-radius: 12px; padding: 20px; position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: linear-gradient(180deg, #FF6400, #FF8533);"></div>
            <div style="font-family: Orbitron; font-size: 2rem; color: #FF6400; margin-bottom: 8px;">03</div>
            <div style="font-family: Orbitron; font-size: 0.75rem; color: #FF6400; letter-spacing: 1px; margin-bottom: 8px;">INSTANT REVOKE</div>
            <div style="font-size: 0.85rem; color: #94A3B8; line-height: 1.5;">Ability to instantly cut off access between clusters with a single control action</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Our Approach
    st.markdown('<div class="section-header">Our Approach</div>', unsafe_allow_html=True)

    cols = st.columns(4)
    approaches = [
        {"icon": icon('vpc', '#FF6400', 36), "title": "VPC PEERING", "desc": "Private connectivity between regions"},
        {"icon": icon('lb', '#FF6400', 36), "title": "INTERNAL LBS", "desc": "No public IPs exposed"},
        {"icon": icon('firewall', '#FF6400', 36), "title": "FIREWALL RULES", "desc": "Network-level access control"},
        {"icon": icon('policy', '#FF6400', 36), "title": "NETWORK POLICIES", "desc": "Pod-level restrictions"},
    ]
    for i, a in enumerate(approaches):
        with cols[i]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1E293B, #334155); border: 1px solid rgba(255,100,0,0.3); border-radius: 12px; padding: 16px; text-align: center; height: 130px; position: relative;">
                <div style="margin-bottom: 8px;">{a['icon']}</div>
                <div style="font-family: Orbitron; font-size: 0.7rem; color: #FF6400 !important; -webkit-text-fill-color: #FF6400 !important; letter-spacing: 1px; margin-bottom: 6px;">{a['title']}</div>
                <div style="font-size: 0.7rem; color: #94A3B8 !important; -webkit-text-fill-color: #94A3B8 !important;">{a['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Infrastructure diagram image
    st.markdown("<br>", unsafe_allow_html=True)
    import os
    infra_image_path = os.path.join(os.path.dirname(__file__), 'assets', 'infrastructure.png')
    if os.path.exists(infra_image_path):
        st.image(infra_image_path, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Production Roadmap
    st.markdown('<div class="section-header">Production Roadmap</div>', unsafe_allow_html=True)

    road1, road2 = st.columns(2)

    with road1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1E293B, #334155); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 16px; height: 100%;">
            <div style="font-family: Orbitron; font-size: 0.75rem; color: #10B981 !important; -webkit-text-fill-color: #10B981 !important; letter-spacing: 1px; margin-bottom: 12px; border-bottom: 1px solid rgba(16,185,129,0.3); padding-bottom: 8px;">✓ IMPLEMENTED</div>
            <div style="font-size: 0.7rem; color: #CBD5E1 !important; -webkit-text-fill-color: #CBD5E1 !important; line-height: 1.8;">
                <div>● Private GKE Clusters (no public IPs)</div>
                <div>● VPC Peering for cross-region connectivity</div>
                <div>● Internal Load Balancers with global access</div>
                <div>● Firewall rules for network segmentation</div>
                <div>● NetworkPolicies for pod-level control</div>
                <div>● Prometheus + Grafana observability</div>
                <div>● Loki for centralized logging</div>
                <div>● Instant access revocation mechanism</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with road2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1E293B, #334155); border: 1px solid rgba(251, 146, 60, 0.3); border-radius: 12px; padding: 16px; height: 100%;">
            <div style="font-family: Orbitron; font-size: 0.75rem; color: #FB923C !important; -webkit-text-fill-color: #FB923C !important; letter-spacing: 1px; margin-bottom: 12px; border-bottom: 1px solid rgba(251,146,60,0.3); padding-bottom: 8px;">◐ PRODUCTION ENHANCEMENTS</div>
            <div style="font-size: 0.7rem; color: #CBD5E1 !important; -webkit-text-fill-color: #CBD5E1 !important; line-height: 1.8;">
                <div>○ Service Mesh (Istio) for mTLS encryption</div>
                <div>○ API Gateway for rate limiting & auth</div>
                <div>○ Redis/Memcached caching layer</div>
                <div>○ Database sharding for scale</div>
                <div>○ Cloud Armor WAF + DDoS protection</div>
                <div>○ Secret Manager integration</div>
                <div>○ CI/CD with ArgoCD GitOps</div>
                <div>○ Velero backup & disaster recovery</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Internet Exposure Options
    st.markdown('<div class="section-header">Internet Exposure Options</div>', unsafe_allow_html=True)

    exp1, exp2, exp3 = st.columns(3)

    with exp1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1E293B, #334155); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 16px; text-align: center;">
            <div style="font-family: Orbitron; font-size: 0.9rem; color: #3B82F6 !important; -webkit-text-fill-color: #3B82F6 !important; margin-bottom: 8px;">GKE GATEWAY</div>
            <div style="font-size: 0.65rem; color: #94A3B8 !important; -webkit-text-fill-color: #94A3B8 !important; line-height: 1.6;">
                Global L7 Load Balancer<br>
                Managed TLS certificates<br>
                Cloud Armor integration<br>
                <span style="color: #10B981 !important; -webkit-text-fill-color: #10B981 !important;">Recommended for production</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with exp2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1E293B, #334155); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 12px; padding: 16px; text-align: center;">
            <div style="font-family: Orbitron; font-size: 0.9rem; color: #8B5CF6 !important; -webkit-text-fill-color: #8B5CF6 !important; margin-bottom: 8px;">IDENTITY-AWARE PROXY</div>
            <div style="font-size: 0.65rem; color: #94A3B8 !important; -webkit-text-fill-color: #94A3B8 !important; line-height: 1.6;">
                Zero-trust access model<br>
                Google identity integration<br>
                Context-aware policies<br>
                <span style="color: #F59E0B !important; -webkit-text-fill-color: #F59E0B !important;">Best for internal tools</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with exp3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1E293B, #334155); border: 1px solid rgba(236, 72, 153, 0.3); border-radius: 12px; padding: 16px; text-align: center;">
            <div style="font-family: Orbitron; font-size: 0.9rem; color: #EC4899 !important; -webkit-text-fill-color: #EC4899 !important; margin-bottom: 8px;">ANTHOS INGRESS</div>
            <div style="font-size: 0.65rem; color: #94A3B8 !important; -webkit-text-fill-color: #94A3B8 !important; line-height: 1.6;">
                Multi-cluster ingress<br>
                Global anycast IPs<br>
                Traffic splitting<br>
                <span style="color: #64748B !important; -webkit-text-fill-color: #64748B !important;">Enterprise multi-cloud</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    nav_buttons(next_page='architecture', next_label="ARCHITECTURE")


# ============================================
# PAGE 2: ARCHITECTURE
# ============================================
elif st.session_state.current_page == 'architecture':

    render_header()
    render_progress()
    st.markdown("---")

    st.markdown('<div class="section-header">System Architecture</div>', unsafe_allow_html=True)

    # Original HTML-based diagram
    arch_c1, arch_mid, arch_c2 = st.columns([2, 1, 2])

    with arch_c1:
        gke_icon = icon('gke', '#ff6400', 28)
        svc_icon = icon('service', '#10b981', 16)
        db_icon = icon('database', '#3b82f6', 16)
        st.markdown(f"""
        <div style="background: rgba(30,41,59,0.9); border: 2px solid #ff6400; border-radius: 12px; padding: 16px; height: 300px;">
            <div style="text-align: center; border-bottom: 1px solid rgba(255,100,0,0.3); padding-bottom: 10px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                    {gke_icon}
                    <span style="font-family: Orbitron; font-size: 1.1rem; color: #ff6400 !important; -webkit-text-fill-color: #ff6400 !important;">CLUSTER C1</span>
                </div>
                <div style="font-family: JetBrains Mono; font-size: 0.7rem; color: #64748b !important; -webkit-text-fill-color: #64748b !important;">us-central1 · 10.0.0.0/16</div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 10px; padding: 10px; background: rgba(16,185,129,0.15); border-radius: 8px; border-left: 3px solid #10b981;">
                    {svc_icon}
                    <span style="font-family: JetBrains Mono; font-size: 0.85rem; color: #e2e8f0 !important; -webkit-text-fill-color: #e2e8f0 !important;">frontend</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px; padding: 10px; background: rgba(16,185,129,0.15); border-radius: 8px; border-left: 3px solid #10b981;">
                    {svc_icon}
                    <span style="font-family: JetBrains Mono; font-size: 0.85rem; color: #e2e8f0 !important; -webkit-text-fill-color: #e2e8f0 !important;">loadgenerator</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px; padding: 10px; background: rgba(59,130,246,0.15); border-radius: 8px; border-left: 3px solid #3b82f6;">
                    {db_icon}
                    <span style="font-family: JetBrains Mono; font-size: 0.85rem; color: #e2e8f0 !important; -webkit-text-fill-color: #e2e8f0 !important;">accounts-db</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with arch_mid:
        vpc_ico = icon('vpc', '#ffffff', 28)
        fw_ico = icon('firewall', '#ffffff', 20)
        st.markdown(f"""
        <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 300px;">
            <div style="font-family: JetBrains Mono; font-size: 0.75rem; color: #10b981 !important; -webkit-text-fill-color: #10b981 !important;">TCP:8085</div>
            <div style="color: #10b981; font-size: 2.5rem; margin: 8px 0; letter-spacing: -4px;">→→→</div>
            <div style="background: linear-gradient(135deg, #ff6400, #ff8533); padding: 16px 20px; border-radius: 12px; text-align: center; margin: 12px 0;">
                <div style="margin-bottom: 6px;">{vpc_ico}</div>
                <div style="font-family: Orbitron; font-size: 0.8rem; color: #fff !important; -webkit-text-fill-color: #fff !important; letter-spacing: 1px;">VPC PEERING</div>
                <div style="display: flex; align-items: center; justify-content: center; gap: 6px; margin-top: 8px;">
                    {fw_ico}
                    <span style="font-size: 0.7rem; color: rgba(255,255,255,0.9) !important; -webkit-text-fill-color: rgba(255,255,255,0.9) !important;">Firewall</span>
                </div>
            </div>
            <div style="color: #3b82f6; font-size: 2rem; letter-spacing: -4px;">←←←</div>
            <div style="font-family: JetBrains Mono; font-size: 0.75rem; color: #3b82f6 !important; -webkit-text-fill-color: #3b82f6 !important;">TCP:5432</div>
        </div>
        """, unsafe_allow_html=True)

    with arch_c2:
        gke_icon2 = icon('gke', '#ff6400', 28)
        svc_icon2 = icon('service', '#10b981', 14)
        db_icon2 = icon('database', '#3b82f6', 14)
        st.markdown(f"""
        <div style="background: rgba(30,41,59,0.9); border: 2px solid #ff6400; border-radius: 12px; padding: 16px; height: 300px;">
            <div style="text-align: center; border-bottom: 1px solid rgba(255,100,0,0.3); padding-bottom: 10px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                    {gke_icon2}
                    <span style="font-family: Orbitron; font-size: 1.1rem; color: #ff6400 !important; -webkit-text-fill-color: #ff6400 !important;">CLUSTER C2</span>
                </div>
                <div style="font-family: JetBrains Mono; font-size: 0.7rem; color: #64748b !important; -webkit-text-fill-color: #64748b !important;">us-east1 · 10.1.0.0/16</div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 6px; padding: 8px; background: rgba(16,185,129,0.15); border-radius: 6px; border-left: 3px solid #10b981;">
                    {svc_icon2}
                    <span style="font-family: JetBrains Mono; font-size: 0.7rem; color: #e2e8f0 !important; -webkit-text-fill-color: #e2e8f0 !important;">userservice</span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px; padding: 8px; background: rgba(16,185,129,0.15); border-radius: 6px; border-left: 3px solid #10b981;">
                    {svc_icon2}
                    <span style="font-family: JetBrains Mono; font-size: 0.7rem; color: #e2e8f0 !important; -webkit-text-fill-color: #e2e8f0 !important;">contacts</span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px; padding: 8px; background: rgba(16,185,129,0.15); border-radius: 6px; border-left: 3px solid #10b981;">
                    {svc_icon2}
                    <span style="font-family: JetBrains Mono; font-size: 0.7rem; color: #e2e8f0 !important; -webkit-text-fill-color: #e2e8f0 !important;">balancereader</span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px; padding: 8px; background: rgba(16,185,129,0.15); border-radius: 6px; border-left: 3px solid #10b981;">
                    {svc_icon2}
                    <span style="font-family: JetBrains Mono; font-size: 0.7rem; color: #e2e8f0 !important; -webkit-text-fill-color: #e2e8f0 !important;">txnhistory</span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px; padding: 8px; background: rgba(16,185,129,0.15); border-radius: 6px; border-left: 3px solid #10b981;">
                    {svc_icon2}
                    <span style="font-family: JetBrains Mono; font-size: 0.7rem; color: #e2e8f0 !important; -webkit-text-fill-color: #e2e8f0 !important;">ledgerwriter</span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px; padding: 8px; background: rgba(59,130,246,0.15); border-radius: 6px; border-left: 3px solid #3b82f6;">
                    {db_icon2}
                    <span style="font-family: JetBrains Mono; font-size: 0.7rem; color: #e2e8f0 !important; -webkit-text-fill-color: #e2e8f0 !important;">ledger-db</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Architecture diagram image
    arch_image_path = os.path.join(os.path.dirname(__file__), 'assets', 'architecture.png')
    if os.path.exists(arch_image_path):
        st.image(arch_image_path, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Key points
    st.markdown('<div class="section-header">Key Design Decisions</div>', unsafe_allow_html=True)
    kp1, kp2, kp3 = st.columns(3)
    with kp1:
        st.markdown(f"""
        <div style="background: rgba(30,41,59,0.5); border-radius: 8px; padding: 14px; border-left: 3px solid #10b981;">
            <div style="font-family: Orbitron; font-size: 0.7rem; color: #10b981 !important; margin-bottom: 6px;">PRIVATE NODES</div>
            <div style="font-size: 0.75rem; color: #94A3B8 !important;">No public IPs on GKE nodes</div>
        </div>
        """, unsafe_allow_html=True)
    with kp2:
        st.markdown(f"""
        <div style="background: rgba(30,41,59,0.5); border-radius: 8px; padding: 14px; border-left: 3px solid #ff6400;">
            <div style="font-family: Orbitron; font-size: 0.7rem; color: #ff6400 !important; margin-bottom: 6px;">INTERNAL LBS</div>
            <div style="font-size: 0.75rem; color: #94A3B8 !important;">Global access enabled for cross-region</div>
        </div>
        """, unsafe_allow_html=True)
    with kp3:
        st.markdown(f"""
        <div style="background: rgba(30,41,59,0.5); border-radius: 8px; padding: 14px; border-left: 3px solid #3b82f6;">
            <div style="font-family: Orbitron; font-size: 0.7rem; color: #3b82f6 !important; margin-bottom: 6px;">DEFENSE IN DEPTH</div>
            <div style="font-size: 0.75rem; color: #94A3B8 !important;">Firewall + NetworkPolicy layers</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    nav_buttons(back_page='overview', next_page='workflow', next_label="WORKFLOW")


# ============================================
# PAGE 3: DEMO WORKFLOW
# ============================================
elif st.session_state.current_page == 'workflow':

    render_header()
    render_progress()
    st.markdown("---")

    st.markdown('<div class="section-header">Demo Workflow</div>', unsafe_allow_html=True)

    # Large workflow steps
    steps = [
        {"num": "1", "title": "VERIFY", "desc": "Confirm all services are online and communicating across clusters", "color": "#10b981", "details": "Test connectivity from C1 frontend to C2 backend services"},
        {"num": "2", "title": "REVOKE", "desc": "Delete the firewall rule to block cross-cluster traffic", "color": "#ef4444", "details": "gcloud compute firewall-rules delete allow-c1-to-c2-app"},
        {"num": "3", "title": "OBSERVE", "desc": "Watch Grafana dashboards show errors spike", "color": "#f59e0b", "details": "Errors & Failures dashboard shows connection timeouts"},
        {"num": "4", "title": "IMPACT", "desc": "Application fails - users cannot access backend services", "color": "#ef4444", "details": "Bank of Anthos frontend shows error states"},
        {"num": "5", "title": "RESTORE", "desc": "Recreate firewall rule to restore connectivity", "color": "#10b981", "details": "Services recover automatically once network path is open"},
    ]

    for i, step in enumerate(steps):
        c1, c2 = st.columns([1, 4])
        with c1:
            st.markdown(f"""
            <div style="width: 70px; height: 70px; background: linear-gradient(135deg, {step['color']}, {step['color']}cc); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-family: Orbitron; font-size: 1.8rem; color: #fff; margin: 0 auto;">
                {step['num']}
            </div>
            """, unsafe_allow_html=True)
            if i < len(steps) - 1:
                st.markdown(f'<div style="width: 4px; height: 40px; background: linear-gradient(180deg, {step["color"]}, {steps[i+1]["color"]}); margin: 8px auto;"></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style="background: rgba(30,41,59,0.5); border-radius: 12px; padding: 16px; border-left: 4px solid {step['color']}; margin-bottom: 8px;">
                <div style="font-family: Orbitron; font-size: 1rem; color: {step['color']} !important; -webkit-text-fill-color: {step['color']} !important; margin-bottom: 6px;">{step['title']}</div>
                <div style="font-size: 0.9rem; color: #e2e8f0 !important; -webkit-text-fill-color: #e2e8f0 !important; margin-bottom: 8px;">{step['desc']}</div>
                <div style="font-family: JetBrains Mono; font-size: 0.7rem; color: #64748b !important; -webkit-text-fill-color: #64748b !important; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 4px;">{step['details']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Workflow sequence diagram image
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Sequence Diagram</div>', unsafe_allow_html=True)
    workflow_image_path = os.path.join(os.path.dirname(__file__), 'assets', 'workflow.png')
    if os.path.exists(workflow_image_path):
        st.image(workflow_image_path, use_container_width=True)

    st.markdown("---")
    nav_buttons(back_page='architecture', next_page='demo', next_label="START DEMO")


# ============================================
# PAGE 4: DEMO
# ============================================
elif st.session_state.current_page == 'demo':
    # Header with back button and status
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("← WORKFLOW", key="back_btn"):
            navigate_to('workflow')
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <span style="font-family: Orbitron; font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, #FF6400, #FF8533); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">LIVE DEMO</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        access_enabled = check_firewall_rule()
        if access_enabled:
            st.markdown('<div style="text-align: right;"><span class="live-indicator live-connected">● OPEN</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align: right;"><span class="incident-badge">⚠ INCIDENT</span></div>', unsafe_allow_html=True)

    # SRE ALERT SYSTEM - Show when access is blocked
    if not access_enabled:
        st.markdown("""
        <div class="alert-banner">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 1.5rem;">🚨</span>
                    <div>
                        <div style="font-family: Orbitron; font-size: 1rem; color: #fff; letter-spacing: 2px;">CRITICAL INCIDENT DETECTED</div>
                        <div style="font-family: JetBrains Mono; font-size: 0.7rem; color: #fca5a5;">Cross-cluster connectivity failure | Firewall rule deleted | Services unreachable</div>
                    </div>
                </div>
                <div style="font-family: Orbitron; font-size: 0.8rem; color: #fca5a5;">SEV-1</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Scrolling alert ticker
        st.markdown("""
        <div class="alert-ticker">
            <div class="ticker-content">
                🔴 ALERT: Connection timeout to userservice (10.1.10.10:8085) &nbsp;&nbsp;|&nbsp;&nbsp;
                🔴 ALERT: Connection timeout to contacts (10.1.10.11:8085) &nbsp;&nbsp;|&nbsp;&nbsp;
                🔴 ALERT: Connection timeout to balancereader (10.1.10.12:8085) &nbsp;&nbsp;|&nbsp;&nbsp;
                🔴 ALERT: Connection timeout to transactionhistory (10.1.10.13:8085) &nbsp;&nbsp;|&nbsp;&nbsp;
                🔴 ALERT: Connection timeout to ledgerwriter (10.1.10.14:8085) &nbsp;&nbsp;|&nbsp;&nbsp;
                ⚠️ WARN: Firewall rule 'allow-c1-to-c2-app' not found &nbsp;&nbsp;|&nbsp;&nbsp;
                🔴 CRITICAL: Bank of Anthos frontend cannot reach backend services &nbsp;&nbsp;|&nbsp;&nbsp;
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Metrics Row
    grafana_up = check_port(3001)
    frontend_up = check_port(8085)
    connected = sum(1 for s in st.session_state.service_statuses.values() if s)

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown('<div class="metric-card"><span class="metric-value">2</span><div class="metric-label">Clusters</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="metric-card"><span class="metric-value">5</span><div class="metric-label">Services</div></div>', unsafe_allow_html=True)
    with m3:
        color = '#10B981' if connected == 5 else '#EF4444'
        pulse_style = 'animation: blink 0.5s infinite;' if not access_enabled else ''
        label = "ALERT" if not access_enabled else "Online"
        st.markdown(f'<div class="metric-card" style="{pulse_style}"><span class="metric-value" style="color: {color} !important; -webkit-text-fill-color: {color} !important;">{connected}/5</span><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)
    with m4:
        color = '#10B981' if grafana_up else '#EF4444'
        st.markdown(f'<div class="metric-card"><span class="metric-value" style="color: {color} !important; -webkit-text-fill-color: {color} !important;">{"UP" if grafana_up else "DOWN"}</span><div class="metric-label">Grafana</div></div>', unsafe_allow_html=True)
    with m5:
        color = '#10B981' if frontend_up else '#EF4444'
        st.markdown(f'<div class="metric-card"><span class="metric-value" style="color: {color} !important; -webkit-text-fill-color: {color} !important;">{"UP" if frontend_up else "DOWN"}</span><div class="metric-label">App</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["COMMAND CENTER", "OBSERVABILITY", "APPLICATION", "SETTINGS"])

    # TAB 1: COMMAND CENTER
    with tab1:
        left_col, right_col = st.columns([1, 2])

        with left_col:
            st.markdown('<div class="section-header">Access Control</div>', unsafe_allow_html=True)

            if access_enabled:
                st.markdown("""
                <div style="background: rgba(16, 185, 129, 0.1); border: 2px solid #10B981; border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-family: Orbitron; font-size: 1.5rem; color: #10B981 !important; -webkit-text-fill-color: #10B981 !important;">OPEN</div>
                    <div style="font-size: 0.7rem; color: #64748B; margin-top: 4px;">Firewall Active</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("REVOKE ACCESS", key="revoke", use_container_width=True):
                    with st.spinner("Revoking..."):
                        revoke_access()
                        st.session_state.service_statuses = {}
                        time.sleep(1)
                    st.rerun()
            else:
                st.markdown("""
                <div style="background: rgba(239, 68, 68, 0.15); border: 2px solid #EF4444; border-radius: 12px; padding: 20px; text-align: center; animation: siren-pulse 1s ease-in-out infinite;">
                    <div style="font-family: Orbitron; font-size: 1.5rem; color: #EF4444 !important; -webkit-text-fill-color: #EF4444 !important; animation: blink 0.5s infinite;">BLOCKED</div>
                    <div style="font-size: 0.7rem; color: #fca5a5; margin-top: 4px;">Firewall Deleted</div>
                    <div style="font-family: JetBrains Mono; font-size: 0.6rem; color: #EF4444; margin-top: 8px; padding: 6px; background: rgba(0,0,0,0.3); border-radius: 4px;">allow-c1-to-c2-app: NOT FOUND</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("RESTORE ACCESS", key="restore", use_container_width=True):
                    with st.spinner("Restoring..."):
                        restore_access()
                        time.sleep(1)
                    st.rerun()

                # Explanation panel when blocked
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("""
                <div style="background: #0F172A; border: 1px solid #334155; border-radius: 8px; padding: 14px;">
                    <div style="font-family: Orbitron; font-size: 0.65rem; color: #F59E0B !important; -webkit-text-fill-color: #F59E0B !important; letter-spacing: 1px; margin-bottom: 12px;">WHAT'S HAPPENING</div>
                    <div style="font-size: 0.65rem; line-height: 1.8; margin-bottom: 12px;">
                        <span style="color: #10B981 !important; -webkit-text-fill-color: #10B981 !important;">Browser → :8085 → C1 Frontend ✓</span><br>
                        <span style="color: #64748B !important; -webkit-text-fill-color: #64748B !important;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓</span><br>
                        <span style="color: #EF4444 !important; -webkit-text-fill-color: #EF4444 !important;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;C1 → C2 Firewall ✗ BLOCKED</span><br>
                        <span style="color: #64748B !important; -webkit-text-fill-color: #64748B !important;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓</span><br>
                        <span style="color: #EF4444 !important; -webkit-text-fill-color: #EF4444 !important;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;C2 Backends (unreachable)</span>
                    </div>
                    <div style="font-size: 0.65rem; line-height: 1.6;">
                        <span style="color: #10B981 !important; -webkit-text-fill-color: #10B981 !important;">✓</span> <span style="color: #CBD5E1 !important; -webkit-text-fill-color: #CBD5E1 !important;">Frontend loads (port-forward works)</span><br>
                        <span style="color: #EF4444 !important; -webkit-text-fill-color: #EF4444 !important;">✗</span> <span style="color: #CBD5E1 !important; -webkit-text-fill-color: #CBD5E1 !important;">Login fails (userservice unreachable)</span><br>
                        <span style="color: #EF4444 !important; -webkit-text-fill-color: #EF4444 !important;">✗</span> <span style="color: #CBD5E1 !important; -webkit-text-fill-color: #CBD5E1 !important;">Balance fails (balancereader unreachable)</span><br>
                        <span style="color: #EF4444 !important; -webkit-text-fill-color: #EF4444 !important;">✗</span> <span style="color: #CBD5E1 !important; -webkit-text-fill-color: #CBD5E1 !important;">Transactions fail (history unreachable)</span>
                    </div>
                    <div style="font-size: 0.55rem; color: #64748B !important; -webkit-text-fill-color: #64748B !important; font-style: italic; border-top: 1px solid #334155; padding-top: 10px; margin-top: 10px;">
                        Try Bank of Anthos UI — errors appear because frontend can't reach backends.
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with right_col:
            st.markdown('<div class="section-header">Backend Services (C2)</div>', unsafe_allow_html=True)

            if st.button("TEST CONNECTIVITY", key="test", use_container_width=True):
                progress = st.progress(0)
                for i, svc in enumerate(BACKEND_SERVICES):
                    st.session_state.service_statuses[svc['name']] = test_service_connectivity(svc['ip'], svc['port'])
                    progress.progress((i + 1) / len(BACKEND_SERVICES))
                progress.empty()
                st.rerun()

            for svc in BACKEND_SERVICES:
                status = st.session_state.service_statuses.get(svc['name'], None)
                if status:
                    st.markdown(f'<div class="service-row active"><span style="font-family: JetBrains Mono; font-size: 0.8rem;">{svc["name"]} · {svc["ip"]}</span><span style="color: #10B981;">● ONLINE</span></div>', unsafe_allow_html=True)
                elif status is False:
                    st.markdown(f'<div class="service-row blocked" style="animation: shake 0.5s infinite;"><span style="font-family: JetBrains Mono; font-size: 0.8rem;">{svc["name"]} · {svc["ip"]}</span><span style="color: #EF4444; animation: blink 0.5s infinite;">TIMEOUT</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="service-row"><span style="font-family: JetBrains Mono; font-size: 0.8rem;">{svc["name"]} · {svc["ip"]}</span><span style="color: #64748B;">—</span></div>', unsafe_allow_html=True)

            # Error Log Panel - Show when services are down
            if not access_enabled:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-header" style="color: #EF4444 !important; -webkit-text-fill-color: #EF4444 !important;">Live Error Stream</div>', unsafe_allow_html=True)

                import random
                timestamps = [f"16:2{random.randint(0,9)}:{random.randint(10,59)}" for _ in range(10)]

                error_logs = f"""
                <div class="error-log">
                    <div class="error-line">[{timestamps[0]}] ERROR frontend: Connection refused to userservice:8085 - dial tcp 10.1.10.10:8085: i/o timeout</div>
                    <div class="error-line">[{timestamps[1]}] ERROR frontend: Failed to fetch user balance - context deadline exceeded</div>
                    <div class="warning-line">[{timestamps[2]}] WARN  loadgenerator: Health check failed for contacts service</div>
                    <div class="error-line">[{timestamps[3]}] ERROR frontend: Connection refused to balancereader:8085 - no route to host</div>
                    <div class="error-line">[{timestamps[4]}] ERROR frontend: Transaction history unavailable - connection timeout after 5000ms</div>
                    <div class="warning-line">[{timestamps[5]}] WARN  prometheus: Target c2-backend-services is DOWN</div>
                    <div class="error-line">[{timestamps[6]}] ERROR frontend: ledgerwriter unreachable - TCP connection failed</div>
                    <div class="error-line">[{timestamps[7]}] ERROR userservice: Cannot connect to accounts-db via cross-cluster ILB</div>
                    <div class="warning-line">[{timestamps[8]}] WARN  grafana: Alert firing: CrossClusterConnectivityDown</div>
                    <div class="error-line">[{timestamps[9]}] CRITICAL: All C1→C2 traffic blocked - firewall rule missing</div>
                </div>
                """
                st.markdown(error_logs, unsafe_allow_html=True)

    # TAB 2: OBSERVABILITY
    with tab2:
        if check_port(3001):
            dash0, dash1, dash2, dash3 = st.tabs(["SRE METRICS", "CROSS-CLUSTER METRICS", "ERRORS & FAILURES", "LOKI LOGS"])

            with dash0:
                # SRE Metrics Dashboard
                st.markdown('<div class="section-header">Service Level Objectives</div>', unsafe_allow_html=True)

                slo1, slo2, slo3, slo4 = st.columns(4)
                with slo1:
                    slo_color = '#10B981' if access_enabled else '#EF4444'
                    slo_val = '99.95%' if access_enabled else '94.2%'
                    st.markdown(f'''
                    <div style="background: linear-gradient(135deg, #1E293B, #334155); border-radius: 12px; padding: 16px; text-align: center; border-top: 3px solid {slo_color};">
                        <div style="font-family: Orbitron; font-size: 1.8rem; color: {slo_color} !important; -webkit-text-fill-color: {slo_color} !important;">{slo_val}</div>
                        <div style="font-size: 0.7rem; color: #94A3B8 !important; margin-top: 4px;">SLO AVAILABILITY</div>
                        <div style="font-size: 0.6rem; color: #64748B !important;">Target: 99.9%</div>
                    </div>
                    ''', unsafe_allow_html=True)
                with slo2:
                    budget_color = '#10B981' if access_enabled else '#EF4444'
                    budget_val = '43%' if access_enabled else '0%'
                    st.markdown(f'''
                    <div style="background: linear-gradient(135deg, #1E293B, #334155); border-radius: 12px; padding: 16px; text-align: center; border-top: 3px solid {budget_color};">
                        <div style="font-family: Orbitron; font-size: 1.8rem; color: {budget_color} !important; -webkit-text-fill-color: {budget_color} !important;">{budget_val}</div>
                        <div style="font-size: 0.7rem; color: #94A3B8 !important; margin-top: 4px;">ERROR BUDGET</div>
                        <div style="font-size: 0.6rem; color: #64748B !important;">Monthly remaining</div>
                    </div>
                    ''', unsafe_allow_html=True)
                with slo3:
                    latency_color = '#10B981' if access_enabled else '#F59E0B'
                    latency_val = '245ms' if access_enabled else '892ms'
                    st.markdown(f'''
                    <div style="background: linear-gradient(135deg, #1E293B, #334155); border-radius: 12px; padding: 16px; text-align: center; border-top: 3px solid {latency_color};">
                        <div style="font-family: Orbitron; font-size: 1.8rem; color: {latency_color} !important; -webkit-text-fill-color: {latency_color} !important;">{latency_val}</div>
                        <div style="font-size: 0.7rem; color: #94A3B8 !important; margin-top: 4px;">P99 LATENCY</div>
                        <div style="font-size: 0.6rem; color: #64748B !important;">Target: &lt;500ms</div>
                    </div>
                    ''', unsafe_allow_html=True)
                with slo4:
                    err_color = '#10B981' if access_enabled else '#EF4444'
                    err_val = '0.02%' if access_enabled else '12.4%'
                    st.markdown(f'''
                    <div style="background: linear-gradient(135deg, #1E293B, #334155); border-radius: 12px; padding: 16px; text-align: center; border-top: 3px solid {err_color};">
                        <div style="font-family: Orbitron; font-size: 1.8rem; color: {err_color} !important; -webkit-text-fill-color: {err_color} !important;">{err_val}</div>
                        <div style="font-size: 0.7rem; color: #94A3B8 !important; margin-top: 4px;">ERROR RATE</div>
                        <div style="font-size: 0.6rem; color: #64748B !important;">Target: &lt;1%</div>
                    </div>
                    ''', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-header">Incident Response Metrics</div>', unsafe_allow_html=True)

                ir1, ir2, ir3, ir4 = st.columns(4)
                with ir1:
                    st.markdown('''
                    <div style="background: linear-gradient(135deg, #1E293B, #334155); border-radius: 12px; padding: 16px; text-align: center; border-top: 3px solid #3B82F6;">
                        <div style="font-family: Orbitron; font-size: 1.8rem; color: #3B82F6 !important; -webkit-text-fill-color: #3B82F6 !important;">1.8m</div>
                        <div style="font-size: 0.7rem; color: #94A3B8 !important; margin-top: 4px;">MTTI</div>
                        <div style="font-size: 0.6rem; color: #64748B !important;">Mean Time to Identify</div>
                    </div>
                    ''', unsafe_allow_html=True)
                with ir2:
                    st.markdown('''
                    <div style="background: linear-gradient(135deg, #1E293B, #334155); border-radius: 12px; padding: 16px; text-align: center; border-top: 3px solid #8B5CF6;">
                        <div style="font-family: Orbitron; font-size: 1.8rem; color: #8B5CF6 !important; -webkit-text-fill-color: #8B5CF6 !important;">4.2m</div>
                        <div style="font-size: 0.7rem; color: #94A3B8 !important; margin-top: 4px;">MTTR</div>
                        <div style="font-size: 0.6rem; color: #64748B !important;">Mean Time to Resolve</div>
                    </div>
                    ''', unsafe_allow_html=True)
                with ir3:
                    st.markdown('''
                    <div style="background: linear-gradient(135deg, #1E293B, #334155); border-radius: 12px; padding: 16px; text-align: center; border-top: 3px solid #EC4899;">
                        <div style="font-family: Orbitron; font-size: 1.8rem; color: #EC4899 !important; -webkit-text-fill-color: #EC4899 !important;">2.4m</div>
                        <div style="font-size: 0.7rem; color: #94A3B8 !important; margin-top: 4px;">MTTA</div>
                        <div style="font-size: 0.6rem; color: #64748B !important;">Mean Time to Acknowledge</div>
                    </div>
                    ''', unsafe_allow_html=True)
                with ir4:
                    incidents = '0' if access_enabled else '1'
                    inc_color = '#10B981' if access_enabled else '#EF4444'
                    st.markdown(f'''
                    <div style="background: linear-gradient(135deg, #1E293B, #334155); border-radius: 12px; padding: 16px; text-align: center; border-top: 3px solid {inc_color};">
                        <div style="font-family: Orbitron; font-size: 1.8rem; color: {inc_color} !important; -webkit-text-fill-color: {inc_color} !important;">{incidents}</div>
                        <div style="font-size: 0.7rem; color: #94A3B8 !important; margin-top: 4px;">ACTIVE INCIDENTS</div>
                        <div style="font-size: 0.6rem; color: #64748B !important;">Last 24 hours</div>
                    </div>
                    ''', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-header">Service Health</div>', unsafe_allow_html=True)

                services_health = [
                    {"name": "frontend", "cluster": "C1", "rps": "142", "err": "0.01%", "p99": "89ms"},
                    {"name": "userservice", "cluster": "C2", "rps": "89", "err": "0.02%", "p99": "124ms"},
                    {"name": "balancereader", "cluster": "C2", "rps": "203", "err": "0.00%", "p99": "67ms"},
                    {"name": "ledgerwriter", "cluster": "C2", "rps": "156", "err": "0.01%", "p99": "245ms"},
                    {"name": "transactionhistory", "cluster": "C2", "rps": "178", "err": "0.02%", "p99": "156ms"},
                ]

                st.markdown('''
                <div style="background: #0F172A; border-radius: 8px; padding: 12px; font-family: JetBrains Mono; font-size: 0.7rem;">
                    <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr; gap: 8px; padding: 8px 12px; border-bottom: 1px solid #334155; color: #64748B !important; -webkit-text-fill-color: #64748B !important;">
                        <span>SERVICE</span><span>CLUSTER</span><span>RPS</span><span>ERROR %</span><span>P99</span><span>STATUS</span>
                    </div>
                ''', unsafe_allow_html=True)

                for svc in services_health:
                    status = "HEALTHY" if access_enabled else ("DEGRADED" if svc["cluster"] == "C2" else "HEALTHY")
                    status_color = "#10B981" if status == "HEALTHY" else "#EF4444"
                    err_display = svc["err"] if access_enabled else ("TIMEOUT" if svc["cluster"] == "C2" else svc["err"])
                    st.markdown(f'''
                    <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr; gap: 8px; padding: 10px 12px; border-bottom: 1px solid #1E293B; color: #E2E8F0 !important; -webkit-text-fill-color: #E2E8F0 !important;">
                        <span style="color: #FF6400 !important; -webkit-text-fill-color: #FF6400 !important;">{svc["name"]}</span>
                        <span>{svc["cluster"]}</span>
                        <span>{svc["rps"]}</span>
                        <span style="color: {status_color} !important; -webkit-text-fill-color: {status_color} !important;">{err_display}</span>
                        <span>{svc["p99"]}</span>
                        <span style="color: {status_color} !important; -webkit-text-fill-color: {status_color} !important;">{status}</span>
                    </div>
                    ''', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

            with dash1:
                st.components.v1.iframe(
                    "http://localhost:3001/d/cross-cluster-boa/cross-cluster-metrics-bank-of-anthos?orgId=1&kiosk&refresh=10s",
                    height=600, scrolling=True
                )

            with dash2:
                st.components.v1.iframe(
                    "http://localhost:3001/d/errors-failures/critical-errors-and-failures-dashboard?orgId=1&kiosk&refresh=10s",
                    height=600, scrolling=True
                )

            with dash3:
                st.components.v1.iframe(
                    "http://localhost:3001/d/loki-logs-boa/loki-logs-bank-of-anthos?orgId=1&kiosk&refresh=30s",
                    height=600, scrolling=True
                )

            st.markdown(f"""
            <div style="text-align: center; margin-top: 10px;">
                <a href="{GRAFANA_URL}" target="_blank" style="font-family: Space Grotesk; font-size: 0.8rem; color: #FF6400 !important; text-decoration: none;">
                    Open Grafana Home →
                </a>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-header">Grafana Dashboards</div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #EF4444; border-radius: 10px; padding: 20px; text-align: center;">
                <div style="font-family: Orbitron; font-size: 1rem; color: #EF4444 !important; margin-bottom: 8px;">GRAFANA OFFLINE</div>
                <div style="font-size: 0.8rem; color: #94A3B8;">Enable port forwarding in the Settings tab</div>
            </div>
            """, unsafe_allow_html=True)

    # TAB 3: APPLICATION
    with tab3:
        if check_port(8085):
            st.markdown('<div class="section-header">Bank of Anthos</div>', unsafe_allow_html=True)
            st.components.v1.iframe(FRONTEND_URL, height=500, scrolling=True)
            st.markdown(f"[Open in new tab →]({FRONTEND_URL})")
        else:
            st.warning("Application offline. Enable port forwarding in Settings.")

    # TAB 4: SETTINGS
    with tab4:
        st.markdown('<div class="section-header">Port Forwarding</div>', unsafe_allow_html=True)

        all_active = True
        for svc in PORT_FORWARD_SERVICES:
            is_active = check_port(svc['local_port'])
            if not is_active:
                all_active = False
            status_class = "active" if is_active else "blocked"
            color = '#10B981' if is_active else '#EF4444'
            st.markdown(f'<div class="service-row {status_class}"><span style="font-family: JetBrains Mono;">{svc["name"]} · localhost:{svc["local_port"]}</span><span style="color: {color};">{"ACTIVE" if is_active else "INACTIVE"}</span></div>', unsafe_allow_html=True)

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("ENABLE ALL", disabled=all_active, use_container_width=True):
                subprocess.run(["/bin/bash", "/Users/chundu/ciroos/demo-ui/start-portforward.sh"],
                               capture_output=True, cwd="/Users/chundu/ciroos/demo-ui")
                time.sleep(5)
                st.rerun()
        with c2:
            if st.button("DISABLE ALL", use_container_width=True):
                subprocess.run(["pkill", "-f", "port-forward"], capture_output=True)
                time.sleep(2)
                st.rerun()

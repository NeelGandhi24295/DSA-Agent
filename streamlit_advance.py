import streamlit as st
import asyncio
import os
import json
from typing import AsyncGenerator

from config.docker_utils import get_docker_executor, start_docker_executor, stop_docker_executor
from config.model_client import get_model_client
from autogen_agentchat.messages import TextMessage
from agents.problem_solver_agent import get_problem_solver_agent
from agents.code_executor_agent import get_code_executor_agent
from team.dsa_solver_team import get_team
from config.constants import DOCKER_WORK_DIR

# --- Page Setup ---
st.set_page_config(page_title="DSA Solver Agent", layout="wide")

# --- Animated Banner at Very Top ---
st.markdown("""
<div style="text-align: center; margin: 0; padding: 2rem; border-radius: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4); border: 2px solid rgba(255, 255, 255, 0.2); margin-bottom: 2rem;">
    <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=36&color=%23FFFFFF&center=true&vCenter=true&width=800&height=120&speed=120&pause=2500&lines=%F0%9F%9A%80+Lightning-Fast+DSA+Solutions;🤖+Agentic+Automation+for+Coding;🧠+Complexity+Reduction;🧪+Code-Execution+%2B+Unit+Testing" 
         alt="Agentic DSA Solver" 
         style="max-width: 100%; height: auto; border-radius: 12px;">
</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    #MainMenu, header, footer {visibility: hidden;}
    
    /* Global styles with larger fonts and light grey background */
    .stApp {
        background: #f8f9fa;
        background-attachment: fixed;
        font-size: 18px !important;
        line-height: 1.8 !important;
    }
    
    /* Main content area with subtle background */
    .main {
        background: #ffffff;
        border-radius: 20px;
        margin: 1rem;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Override default sidebar behavior */
    .css-1d391kg {
        background: #f1f3f4;
        border-right: 4px solid #667eea;
        transition: all 0.3s ease-in-out;
        font-size: 16px;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Enhanced sidebar header with larger font */
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        margin: -1rem -1rem 1.5rem -1rem;
        border-radius: 15px 15px 0 0;
        font-weight: bold;
        font-size: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        text-align: center;
        position: relative;
    }
    
    /* Chat message styling with larger fonts and beautiful backgrounds */
    .chat-message {
        padding: 2rem;
        margin: 1.5rem 0;
        border-radius: 20px;
        max-width: 100%;
        font-size: 20px;
        line-height: 1.8;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .chat-message:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
    }
    
    .user-message {
        background: #e3f2fd;
        border-left: 6px solid #2196f3;
        border: 2px solid rgba(33, 150, 243, 0.2);
    }
    
    .assistant-message {
        background: #fff3e0;
        border-left: 6px solid #ff9800;
        border: 2px solid rgba(255, 152, 0, 0.2);
    }
    
    .message-content {
        margin: 0;
        line-height: 1.8;
        font-size: 20px;
        color: #2c3e50;
        font-weight: 400;
    }
    
    .message-label {
        font-weight: 700;
        margin-bottom: 1rem;
        font-size: 18px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #2196f3;
    }
    
    .assistant-label {
        color: #ff9800;
    }
    
    /* Enhanced headings with larger fonts */
    .main h1, .main h2, .main h3 {
        color: #2c3e50 !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main h1 {
        font-size: 36px !important;
    }
    
    .main h2 {
        font-size: 32px !important;
    }
    
    .main h3 {
        font-size: 28px !important;
    }
    
    /* Enhanced paragraph and list styling */
    .main p, .main li {
        font-size: 20px !important;
        line-height: 1.8 !important;
        color: #34495e !important;
        margin-bottom: 1rem !important;
    }
    
    .main ul li {
        margin-bottom: 0.8rem !important;
        padding-left: 0.5rem !important;
    }
    
    /* ENHANCED INPUT FIELD - BIGGER SIZE, COMPLETE RECTANGLE */
    .stTextInput {
        margin: 2rem 0 !important;
    }
    
    .stTextInput > div {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    .stTextInput > div > div {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    .stTextInput > div > div > input {
        font-size: 24px !important;
        padding: 2.5rem !important;
        line-height: 1.8 !important;
        border-radius: 20px !important;
        border: 4px solid #e2e8f0 !important;
        background: #ffffff !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
        transition: all 0.3s ease !important;
        height: auto !important;
        min-height: 90px !important;
        width: 100% !important;
        max-width: 100% !important;
        display: block !important;
        box-sizing: border-box !important;
        text-align: left !important;
        vertical-align: middle !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #9ca3af !important;
        font-size: 22px !important;
        line-height: 1.8 !important;
        font-weight: 400 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 6px rgba(102, 126, 234, 0.25) !important;
        transform: translateY(-3px) !important;
        outline: none !important;
    }
    
    /* Input label with larger font */
    .stTextInput > label {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #2c3e50 !important;
        margin-bottom: 1.5rem !important;
        display: block !important;
    }
    
    /* Sidebar button styling with larger fonts */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        font-weight: 600;
        font-size: 18px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        line-height: 1.6;
        text-transform: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Sidebar conversation count with larger font */
    .conversation-count {
        background: #ffffff;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        font-size: 18px;
        font-weight: 700;
        color: #667eea;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 2px solid rgba(102, 126, 234, 0.2);
    }
    
    .sidebar-footer {
        margin-top: 2rem;
        padding: 2rem;
        background: #ffffff;
        border-radius: 15px;
        text-align: center;
        font-size: 18px;
        line-height: 1.8;
        color: #4a5568;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 2px solid rgba(102, 126, 234, 0.1);
    }
    
    /* Divider styling */
    hr {
        border: none !important;
        height: 3px !important;
        background: #dee2e6 !important;
        border-radius: 2px !important;
        margin: 2rem 0 !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Welcome section styling */
    .welcome-section {
        background: #ffffff;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 2px solid rgba(102, 126, 234, 0.1);
        margin-bottom: 2rem;
    }
    
    /* Empty state styling */
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #6b7280;
        font-size: 18px;
        background: #f9fafb;
        border-radius: 20px;
        box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main {
            margin: 0.5rem;
            padding: 1.5rem;
        }
        
        .stTextInput > div > div > input {
            font-size: 20px !important;
            padding: 2rem !important;
            min-height: 70px !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            font-size: 18px !important;
        }
        
        .stTextInput > label {
            font-size: 20px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Ensure persistence folder exists
os.makedirs(DOCKER_WORK_DIR, exist_ok=True)
MSG_FILE = os.path.join(DOCKER_WORK_DIR, "dsa_messages.json")

# --- Helper functions ---
def normalize_history(history):
    """Ensure history contains only properly formatted dict entries"""
    normalized = []
    for entry in history:
        if isinstance(entry, dict) and 'role' in entry and 'content' in entry:
            normalized.append(entry)
        elif isinstance(entry, str):
            continue
    return normalized

def load_all_messages():
    """Load all messages from JSON file"""
    if os.path.exists(MSG_FILE):
        try:
            with open(MSG_FILE, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                return normalize_history(loaded_data)
        except (json.JSONDecodeError, TypeError, FileNotFoundError):
            return []
    return []

def save_all_messages(messages):
    """Save all messages to JSON file"""
    try:
        with open(MSG_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving messages: {e}")
        return False

def display_chat_message(role, content):
    """Display a chat message with proper styling and larger fonts"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <div class="message-label">👤 You</div>
            <div class="message-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <div class="message-label assistant-label">🤖 DSA Solver</div>
            <div class="message-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)

def get_conversation_sessions():
    """Get conversation sessions for sidebar display"""
    sessions = []
    messages = load_all_messages()
    
    current_session = []
    for msg in messages:
        if isinstance(msg, dict) and msg.get('role') in ['user', 'assistant']:
            current_session.append(msg)
            
            if len(current_session) >= 2 and current_session[-1].get('role') == 'assistant':
                first_user_msg = None
                for session_msg in current_session:
                    if session_msg.get('role') == 'user':
                        first_user_msg = session_msg.get('content', '')
                        break
                
                if first_user_msg:
                    sessions.append({
                        'first_question': first_user_msg,
                        'messages': current_session.copy(),
                        'session_id': len(sessions)
                    })
                current_session = []
    
    return sessions

# --- Session State Initialization ---
if 'dsa_history' not in st.session_state:
    st.session_state.dsa_history = load_all_messages()

if not st.session_state.dsa_history:
    st.session_state.dsa_history = []

# Initialize sidebar state
if 'sidebar_expanded' not in st.session_state:
    st.session_state.sidebar_expanded = True

for key in ('dsa_team_state', 'selected_session', 'current_conversation', 'current_q', 'current_ans', 
            'processing', 'streaming_answer', 'answer_placeholder', 'input_submitted'):
    if key not in st.session_state:
        if key in ('processing', 'input_submitted'):
            st.session_state[key] = False
        elif key in ('streaming_answer', 'current_ans'):
            st.session_state[key] = ""
        elif key == 'current_conversation':
            st.session_state[key] = []
        else:
            st.session_state[key] = None

# --- Custom Expand Button (when sidebar is collapsed) ---
if not st.session_state.sidebar_expanded:
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("📋 Show Conversations", key="expand_sidebar", help="Expand conversations panel"):
            st.session_state.sidebar_expanded = True
            st.rerun()

# --- Enhanced Sidebar with Custom Controls ---
if st.session_state.sidebar_expanded:
    with st.sidebar:
        # Custom header with larger font
        st.markdown(f"""
        <div class="sidebar-header">
            <h3 style="margin: 0;">💬 Conversations</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Collapse button with larger font
        if st.button("⬅️ Hide Conversations", key="collapse_sidebar", help="Collapse sidebar", use_container_width=True):
            st.session_state.sidebar_expanded = False
            st.rerun()
        
        st.markdown("---")
        
        try:
            sessions = get_conversation_sessions()
            
            if sessions:
                # Show conversation count with enhanced styling
                st.markdown(f"""
                <div style="text-align: center; margin-bottom: 2rem;">
                    <span class="conversation-count">📊 {len(sessions)} conversations</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Display conversations
                for session in reversed(sessions):
                    first_question = session['first_question']
                    session_id = session['session_id']
                    
                    label = first_question if len(first_question) < 30 else first_question[:27] + '...'
                    
                    if st.button(f"💭 {label}", key=f'session_{session_id}', help=first_question):
                        st.session_state.selected_session = session['messages']
                        st.session_state.current_conversation = []
                        st.session_state.current_q = None
                        st.session_state.current_ans = ""
                        st.session_state.processing = False
            else:
                st.markdown("""
                <div class="empty-state">
                    <div style="font-size: 4rem;">🔍</div>
                    <p style="font-size: 20px; font-weight: 600; margin-top: 1rem;">No conversations yet!</p>
                    <p style="font-size: 18px;">Start by asking a DSA question below.</p>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error loading conversations: {e}")
        
        st.markdown("---")
        
        # New conversation button
        def start_new_conversation():
            # Save current conversation if exists
            if st.session_state.current_conversation:
                st.session_state.dsa_history.extend(st.session_state.current_conversation)
                save_all_messages(st.session_state.dsa_history)
            
            for key in ('selected_session', 'current_conversation', 'current_q', 'current_ans', 
                        'streaming_answer', 'processing', 'input_submitted', 'dsa_input_direct'):
                if key in ('current_ans', 'streaming_answer'):
                    st.session_state[key] = ""
                elif key in ('processing', 'input_submitted'):
                    st.session_state[key] = False
                elif key == 'current_conversation':
                    st.session_state[key] = []
                else:
                    st.session_state[key] = None
        
        st.button("🚀 Start New Conversation", 
                 on_click=start_new_conversation,
                 key="new_conv_btn",
                 use_container_width=True)
        
        # Sidebar footer with enhanced styling
        total_sessions = len(get_conversation_sessions())
        st.markdown(f"""
        <div class="sidebar-footer">
            <div style="margin-bottom: 1rem; font-weight: 700; font-size: 20px;">📈 Statistics</div>
            <div style="margin-bottom: 0.8rem;">Total Conversations: <strong>{total_sessions}</strong></div>
            <div>Agent Status: <strong style="color: #10b981;">🟢 Online</strong></div>
        </div>
        """, unsafe_allow_html=True)

# --- Main Content Area ---
main_container = st.container()
with main_container:
    # --- Main Title ---
    st.markdown("## 🎯 Ask Your DSA Question")

    # --- Chat Display ---
    chat_container = st.container()

    with chat_container:
        if st.session_state.selected_session is not None:
            for msg in st.session_state.selected_session:
                if isinstance(msg, dict):
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    if role and content:
                        display_chat_message(role, content)
        
        elif st.session_state.current_conversation:
            for msg in st.session_state.current_conversation:
                if isinstance(msg, dict):
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    if role and content:
                        display_chat_message(role, content)
            
            if st.session_state.current_q:
                display_chat_message("user", st.session_state.current_q)
                
                if st.session_state.processing:
                    if 'answer_placeholder' not in st.session_state or st.session_state.answer_placeholder is None:
                        st.session_state.answer_placeholder = st.empty()
                    
                    with st.session_state.answer_placeholder.container():
                        st.markdown(f"""
                        <div class="chat-message assistant-message">
                            <div class="message-label assistant-label">🤖 DSA Solver</div>
                            <div class="message-content">{st.session_state.streaming_answer}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                elif st.session_state.current_ans:
                    display_chat_message("assistant", st.session_state.current_ans)
        
        elif st.session_state.current_q:
            display_chat_message("user", st.session_state.current_q)
            
            if st.session_state.processing:
                if 'answer_placeholder' not in st.session_state or st.session_state.answer_placeholder is None:
                    st.session_state.answer_placeholder = st.empty()
                
                with st.session_state.answer_placeholder.container():
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="message-label assistant-label">🤖 DSA Solver</div>
                        <div class="message-content">{st.session_state.streaming_answer}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            elif st.session_state.current_ans:
                display_chat_message("assistant", st.session_state.current_ans)
        
        else:
            st.markdown("""
            <div class="welcome-section">
                <h3 style="color: #667eea; margin-bottom: 2rem;">🎉 Welcome to the Agentic DSA Solver!</h3>
                <p style="font-size: 22px; margin-bottom: 2rem;"><strong>Get lightning-fast solutions to any Data Structures and Algorithms question with:</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                - 🚀 **Instant Solutions** - Fast problem analysis and step-by-step explanations
                - 🤖 **Smart Automation** - AI-powered code generation and optimization
                """)
            with col2:
                st.markdown("""
                - 🧠 **Complexity Analysis** - Big O time and space complexity calculations
                - 🧪 **Live Testing** - Real-time code execution and comprehensive unit testing
                """)
            
            st.markdown("---")

# --- Async streaming function ---
async def solve_with_streaming(text: str) -> AsyncGenerator[str, None]:
    docker = get_docker_executor()
    model_client = get_model_client()
    try:
        await start_docker_executor(docker)
        solver = get_problem_solver_agent(model_client)
        executor = get_code_executor_agent(docker)
        team = get_team(solver, executor)
        
        if st.session_state.dsa_team_state:
            await team.load_state(st.session_state.dsa_team_state)
        
        async for msg in team.run_stream(task=text):
            if isinstance(msg, TextMessage):
                content = msg.content
                if content.startswith(text):
                    content = content[len(text):].strip()
                
                if content:
                    yield content
                
        st.session_state.dsa_team_state = await team.save_state()
    finally:
        await stop_docker_executor(docker)

# --- Function to handle question submission ---
def submit_question(user_input):
    """Handle question submission"""
    if user_input and not st.session_state.processing:
        st.session_state.processing = True
        st.session_state.current_q = user_input
        st.session_state.current_ans = ""
        st.session_state.streaming_answer = ""
        st.session_state.answer_placeholder = None
        st.session_state.input_submitted = True
        st.session_state.selected_session = None
        st.session_state.dsa_input_direct = ""

# --- Enhanced Input Field ---
input_container = st.container()
with input_container:
    st.markdown("---")
    
    def on_input_change():
        user_input = st.session_state.get('dsa_input_direct', '')
        if user_input and not st.session_state.processing:
            submit_question(user_input)

    st.text_input(
        "💭 Ask your DSA question here...",
        key='dsa_input_direct',
        disabled=st.session_state.processing,
        on_change=on_input_change,
        placeholder="e.g., 'How do I implement a binary search tree?' or 'What's the time complexity of quicksort?'",
        help="Press Enter to submit your question"
    )

# --- Streaming Logic ---
if st.session_state.processing and st.session_state.current_q:
    async def run_streaming():
        full_answer = ""
        try:
            if st.session_state.answer_placeholder is None:
                st.session_state.answer_placeholder = st.empty()
                
            async for chunk in solve_with_streaming(st.session_state.current_q):
                if chunk:
                    full_answer += chunk
                    st.session_state.streaming_answer = full_answer
                    
                    if st.session_state.answer_placeholder:
                        with st.session_state.answer_placeholder.container():
                            st.markdown(f"""
                            <div class="chat-message assistant-message">
                                <div class="message-label assistant-label">🤖 DSA Solver</div>
                                <div class="message-content">{full_answer}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    await asyncio.sleep(0.05)
                
        except Exception as e:
            full_answer = f"Error occurred: {str(e)}"
            st.session_state.streaming_answer = full_answer
            if st.session_state.answer_placeholder:
                with st.session_state.answer_placeholder.container():
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="message-label assistant-label">🤖 DSA Solver</div>
                        <div class="message-content">{full_answer}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.session_state.current_ans = full_answer
        st.session_state.processing = False
        st.session_state.streaming_answer = ""
        st.session_state.answer_placeholder = None
        st.session_state.input_submitted = False
        
        # FIXED: Proper conversation history saving
        if st.session_state.current_q and st.session_state.current_ans:
            st.session_state.current_conversation.extend([
                {'role': 'user', 'content': st.session_state.current_q},
                {'role': 'assistant', 'content': st.session_state.current_ans}
            ])
            
            # Auto-save after each Q&A pair
            st.session_state.dsa_history.extend([
                {'role': 'user', 'content': st.session_state.current_q},
                {'role': 'assistant', 'content': st.session_state.current_ans}
            ])
            save_all_messages(st.session_state.dsa_history)
            
            st.session_state.current_q = None
            st.session_state.current_ans = ""
        
        st.rerun()
    
    asyncio.run(run_streaming())

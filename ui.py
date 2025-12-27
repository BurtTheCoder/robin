"""Robin: AI-Powered Dark Web OSINT Tool - Streamlit Chat UI."""
import asyncio
import base64
from datetime import datetime

import streamlit as st

from agent import RobinAgent
from config import DEFAULT_MODEL


# Page configuration
st.set_page_config(
    page_title="Robin: Dark Web OSINT Agent",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
    }
    .tool-badge {
        background-color: #1f1f1f;
        border: 1px solid #333;
        border-radius: 4px;
        padding: 2px 8px;
        margin: 2px;
        font-size: 12px;
        display: inline-block;
    }
    .agent-status {
        color: #888;
        font-size: 14px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "tool_calls" not in st.session_state:
    st.session_state.tool_calls = []
if "investigation_active" not in st.session_state:
    st.session_state.investigation_active = False


# Sidebar
with st.sidebar:
    st.title("🕵️ Robin")
    st.caption("Dark Web OSINT Agent")
    st.markdown("---")

    # New session button
    if st.button("🔄 New Investigation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent = None
        st.session_state.tool_calls = []
        st.rerun()

    st.markdown("---")

    # Model selection (optional override)
    model = st.selectbox(
        "Model",
        options=[
            "claude-sonnet-4-5-20250514",
            "claude-opus-4-5-20250514",
        ],
        index=0,
    )
    st.session_state.model = model

    st.markdown("---")

    # Tool calls log
    with st.expander("🔧 Agent Actions", expanded=False):
        if st.session_state.tool_calls:
            for i, tool_call in enumerate(st.session_state.tool_calls[-15:]):
                st.markdown(f"**{i+1}. {tool_call['name']}**")
                if tool_call.get('input'):
                    # Show truncated input
                    input_str = str(tool_call['input'])[:100]
                    st.code(input_str, language="json")
        else:
            st.caption("No tools used yet")

    st.markdown("---")

    # Help
    with st.expander("💡 Tips", expanded=False):
        st.markdown("""
        **Example queries:**
        - "ransomware payments 2024"
        - "threat actor APT28"
        - "credential dumps discord"

        **Follow-up examples:**
        - "dig deeper into result #3"
        - "search for more about [topic]"
        - "save the report"
        """)

    st.markdown("---")
    st.caption("Made with Claude Agent SDK")


# Main chat interface
st.title("Dark Web Investigation")

# Display message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Enter your investigation query or follow-up..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Create response container
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        status_placeholder = st.empty()

        # Initialize or reuse agent
        if st.session_state.agent is None:
            status_placeholder.markdown("*🔄 Starting new investigation session...*")

            def on_tool_use(name: str, input_data: dict):
                st.session_state.tool_calls.append({
                    "name": name,
                    "input": input_data,
                    "time": datetime.now().isoformat()
                })

            st.session_state.agent = RobinAgent(
                on_tool_use=on_tool_use,
                model=st.session_state.get("model", DEFAULT_MODEL),
            )

        agent = st.session_state.agent

        # Run async investigation in sync context
        async def run_investigation():
            full_response = ""
            async for chunk in agent.investigate(prompt):
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")
            return full_response

        # Execute async code
        try:
            st.session_state.investigation_active = True
            status_placeholder.markdown("*🔍 Investigating...*")

            # Run the async investigation using asyncio.run()
            response = asyncio.run(run_investigation())

            # Display final response
            response_placeholder.markdown(response)
            status_placeholder.empty()

            # Add to message history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

            # Show download button
            if response:
                now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"robin_report_{now}.md"
                b64 = base64.b64encode(response.encode()).decode()
                download_link = f'<a href="data:file/markdown;base64,{b64}" download="{filename}">📥 Download Report</a>'
                st.markdown(download_link, unsafe_allow_html=True)

        except Exception as e:
            error_msg = f"Investigation failed: {str(e)}"
            response_placeholder.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ {error_msg}"
            })
        finally:
            st.session_state.investigation_active = False


# Footer with session info
if st.session_state.agent and st.session_state.agent.session_id:
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"Session: {st.session_state.agent.session_id[:8]}...")
    with col2:
        st.caption(f"Tools used: {len(st.session_state.tool_calls)}")

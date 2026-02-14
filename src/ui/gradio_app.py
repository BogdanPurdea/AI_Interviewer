"""
Gradio Web Interface for AI Interviewer

This module provides a web-based chat interface for conducting AI interviews.
Users can start interviews on any topic and interact through a conversational UI.
"""

import sys
import os
import threading
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
from core.session import InterviewSession
from config.loader import RESPONSES

# ============================================================================
# SESSION STORAGE
# ============================================================================
# Global dictionary to store active interview sessions
# Key: session_id (string), Value: InterviewSession object
sessions = {}


# ============================================================================
# BACKEND FUNCTIONS
# ============================================================================

def start_interview(topic: str):
    """
    Initialize a new interview session.
    
    This function:
    1. Creates a unique session ID
    2. Initializes an InterviewSession
    3. Generates the interview plan
    4. Returns the opening message
    
    Args:
        topic: The interview topic entered by the user
        
    Returns:
        tuple: (status_message, session_id, chat_history)
            - status_message: Success/error message to display
            - session_id: Hidden state to track this session
            - chat_history: Initial chat with AI's opening message
    """
    # Validate input
    if not topic or not topic.strip():
        return "Please enter a topic", None, []
    
    # Create unique session ID
    session_id = f"session_{len(sessions)}_{int(time.time())}"
    
    # Initialize session with your InterviewSession class
    session = InterviewSession(session_id=session_id)
    
    try:
        # Call your existing start() method
        start_msg = session.start(topic)
        
        # Get opening message from interviewer
        opening_msg = session.get_opening_message(topic)
        
        # Store session in global dictionary
        sessions[session_id] = session
        
        # Return results
        # - Green checkmark + plan message for status
        # - session_id stored in hidden State component
        # - Chat history starts with AI's opening message
        return (
            f"{start_msg}",
            session_id,
            [{"role": "assistant", "content": opening_msg}]  # AI speaks first
        )
        
    except ValueError as e:
        # Safety violation or other error
        return {str(e)}, None, []
    except Exception as e:
        # Unexpected error
        return f"System error: {str(e)}", None, []


def send_message(user_message: str, session_id: str, history: list):
    """
    Process user's message and get AI response.
    
    This function:
    1. Validates the session exists
    2. Adds user message to history immediately
    3. Calls process_user_input() on the session
    4. Handles the SessionResponse (success/error)
    5. Updates chat history with AI response
    6. Ends session if interview is complete
    
    Args:
        user_message: The user's input
        session_id: Current session ID
        history: Chat history list
        
    Returns:
        tuple: (updated_history, empty_string_to_clear_input)
    """
    try:
        # Ignore empty messages
        if not user_message or not user_message.strip():
            return history, "", gr.File(visible=False)  # Ignore empty messages
        
        if not session_id or session_id not in sessions:
            gr.Warning("Session not found. Please start a new interview.")
            return history, "", gr.File(visible=False)
        
        # Add user message to history immediately for instant feedback
        history.append({"role": "user", "content": user_message})
        
        # Yield to show user message immediately (Gradio will update UI)
        yield history, "", gr.File(visible=False)
    
        # Get the session object
        session = sessions[session_id]
        
        # Call your process_user_input() - returns SessionResponse
        result = session.process_user_input(user_message)
        
        # Check if the operation was successful
        if not result.success:
            gr.Warning(result.error)
            # Remove the user message we just added since there was an error
            history.pop()
            yield history, "", gr.File(visible=False)
            return
        
        # Add AI response to chat history
        # (User message already added above for immediate display)
        history.append({"role": "assistant", "content": result.message})
        
        # Check if interview has ended
        if not session.is_active:
            # Get analysis
            filepath, analysis = session.end_session()
            
            # Format analysis for display using template
            key_points_text = "\n".join(f"• {point}" for point in analysis.get("key_points", []))
            if not key_points_text:
                key_points_text = "• No key points extracted"
            
            analysis_text = RESPONSES["analysis_complete"].format(
                summary=analysis.get('summary', 'No summary available'),
                key_points=key_points_text,
                sentiment_label=analysis.get('sentiment_label', 'N/A'),
                sentiment_score=analysis.get('sentiment_score', 0),
                filepath=filepath
            )
            
            history.append({
                "role": "assistant", 
                "content": analysis_text
            })
            
            # Clean up session from memory
            del sessions[session_id]
            
            # Show success notification
            gr.Info("Interview completed and saved!")
            
            # Return updated history, empty string, and visible file download
            yield history, "", gr.File(value=filepath, visible=True)
            return
        
        # Return updated history and empty string (clears input box)
        yield history, "", gr.File(visible=False)
        
    except Exception as e:
        # Handle unexpected errors
        gr.Warning(f"Error: {str(e)}")
        yield history, "", gr.File(visible=False)


def cleanup_expired_sessions():
    """
    Background task to remove inactive sessions.
    
    Runs every 5 minutes and removes sessions that have been
    inactive for more than 30 minutes.
    """
    while True:
        time.sleep(300)  # Sleep 5 minutes
        
        # Find expired sessions
        expired = [
            sid for sid, session in sessions.items()
            if session.is_expired(timeout_minutes=30)
        ]
        
        # Remove them
        for sid in expired:
            del sessions[sid]
        
        if expired:
            print(f"Cleaned up {len(expired)} expired session(s)")


# ============================================================================
# GRADIO UI
# ============================================================================

# Create the interface using Blocks (allows custom layouts)
with gr.Blocks(
    title="AI Interviewer",
) as app:
    
    # ========================================================================
    # HEADER
    # ========================================================================
    gr.Markdown(
        """
        # AI Interviewer
        
        Start a conversation about any topic. The AI will ask thoughtful questions
        to understand your perspective and gather insights.
        """
    )
    
    # ========================================================================
    # HIDDEN STATE
    # ========================================================================
    # This component stores the session_id but is invisible to users
    # It persists across function calls to track which session belongs to this user
    session_state = gr.State(value=None)
    
    # ========================================================================
    # INTERVIEW START SECTION
    # ========================================================================
    with gr.Row():
        # Topic input box
        topic_input = gr.Textbox(
            label="Interview Topic",
            placeholder="Choose a topic (e.g., 'productivity', 'ai in the workplace')",
            lines=1,
            scale=3
        )
        
        # Start button
        start_btn = gr.Button(
            "Start Interview",
            variant="primary",
            scale=1,
        )
    
    # Status message box (shows success/error from start_interview)
    status_box = gr.Textbox(
        label="Status",
        interactive=False,  # Read-only
        lines=1
    )
    
    # ========================================================================
    # CHAT SECTION
    # ========================================================================
    # Chatbot component displays the conversation
    chatbot = gr.Chatbot(
        label="Interview Conversation",
        height=500,
    )
    
    # Download button (initially hidden)
    analysis_download = gr.File(
        label="Download Analysis JSON",
        visible=False,
        interactive=False
    )
    
    # Message input area
    with gr.Row():
        msg_input = gr.Textbox(
            label="Your Response",
            placeholder="Type your answer here...",
            lines=1,
            scale=4
        )
        send_btn = gr.Button(
            "Send",
            variant="primary",
            scale=1,
        )
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    gr.Markdown(
        """
        **Tips:**
        - You can skip questions you don't want to answer through the chat interface
        - You can stop the interview at any time through the chat interface
        - Interviews are automatically saved when completed

        **Created by:** Bogdan Purdea
        """
    )
    
    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================
    # These connect UI components to backend functions
    
    # When "Start Interview" button is clicked
    # Clear chatbot first, then start interview
    start_btn.click(
        fn=lambda: ([], gr.File(visible=False)),  # Clear chatbot and hide download
        inputs=None,
        outputs=[chatbot, analysis_download]
    ).then(
        fn=start_interview,           # Function to call
        inputs=[topic_input],          # Pass topic text
        outputs=[                      # Update these components
            status_box,                # Show status message
            session_state,             # Store session_id
            chatbot                    # Show opening message
        ]
    )
    
    # Start interview when Enter is pressed in topic input
    # Clear chatbot first, then start interview
    topic_input.submit(
        fn=lambda: ([], gr.File(visible=False)),  # Clear chatbot and hide download
        inputs=None,
        outputs=[chatbot, analysis_download]
    ).then(
        fn=start_interview,
        inputs=[topic_input],
        outputs=[status_box, session_state, chatbot]
    )
    
    # Send message when button is clicked
    send_btn.click(
        fn=send_message,              # Function to call
        inputs=[                       # Pass these values
            msg_input,                 # User's message
            session_state,             # Current session_id
            chatbot                    # Current chat history
        ],
        outputs=[                      # Update these components
            chatbot,                   # Updated chat history
            msg_input,                 # Clear the input (empty string)
            analysis_download          # Show/Hide download button
        ]
    )
    
    # When user presses Enter in message box (same as clicking Send)
    msg_input.submit(
        fn=send_message,
        inputs=[msg_input, session_state, chatbot],
        outputs=[chatbot, msg_input, analysis_download]
    )


# ============================================================================
# LAUNCH
# ============================================================================

if __name__ == "__main__":
    # Start background cleanup thread
    cleanup_thread = threading.Thread(
        target=cleanup_expired_sessions,
        daemon=True  # Thread dies when main program exits
    )
    cleanup_thread.start()
    
    # Launch the Gradio app
    app.launch(
        server_name="0.0.0.0",  # Listen on all network interfaces
        server_port=7860,        # Default Gradio port
        share=False,             # Set to True for public URL
        show_error=True,         # Show detailed errors in UI
    )

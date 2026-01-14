
from agent.intent import detect_intent
from agent.rag import retrieve_answer
from agent.tools import mock_lead_capture

def agent_step(state, user_message):
    # Ensure conversation_history exists (for backward compatibility)
    if not hasattr(state, 'conversation_history'):
        from typing import List, Tuple
        state.conversation_history: List[Tuple[str, str]] = []
    
    # Add user message to conversation history
    state.conversation_history.append(("user", user_message))
    
    # If we're in the middle of collecting lead info, check if user is asking a question
    if state.intent == "high_intent" and not state.lead_captured:
        user_msg_lower = user_message.lower()
        
        # Check if user is asking a question instead of providing information
        is_question = any(phrase in user_msg_lower for phrase in [
            "why", "what", "how", "when", "where", "who", "which",
            "do you need", "do you ask", "do you want", "do you require",
            "need my", "ask for", "want my", "require my", "why do", "why did"
        ]) or user_message.strip().endswith("?")
        
        if is_question:
            # User is asking a question, answer it based on what we're collecting
            if not state.name:
                response = (
                    "I need your name to personalize your AutoStream account and set up your profile. "
                    "This helps us provide you with a better experience. Could you please share your name?"
                )
            elif not state.email:
                response = (
                    "I need your email address to create your account and send you important updates "
                    "about your subscription and account. Could you please share your email?"
                )
            elif not state.platform:
                response = (
                    "I need to know which platform you create content on (like YouTube, Instagram, TikTok, etc.) "
                    "so we can tailor our video editing features to your needs. Which platform do you use?"
                )
            else:
                # Shouldn't reach here, but handle it
                response = "Could you please provide that information?"
        else:
            # User provided information, collect it
            if not state.name:
                state.name = user_message
                response = "Thanks! Could you share your email?"
            elif not state.email:
                state.email = user_message
                response = "Which platform do you create content on? (YouTube, Instagram, etc.)"
            elif not state.platform:
                state.platform = user_message
                # All fields collected, capture the lead
                state.lead_captured = True
                result = mock_lead_capture(state.name, state.email, state.platform)
                response = f"{result['status']}"
        
        # Add agent response to history
        state.conversation_history.append(("assistant", response))
        return response
    
    # Check for questions about lead capture process (especially right after capture)
    user_msg_lower = user_message.lower()
    # Check if the last agent message was about lead capture
    last_agent_msg = state.conversation_history[-1][1] if state.conversation_history and state.conversation_history[-1][0] == "assistant" else ""
    
    # More flexible detection - check for key words that indicate questions about data collection
    has_why_question = any(word in user_msg_lower for word in ["why", "what for", "purpose", "reason"])
    has_details_reference = any(phrase in user_msg_lower for phrase in [
        "details", "information", "data", "my", "you need", "you ask", "you collect",
        "you require", "you want", "you needed", "you asked", "you collected"
    ])
    has_what_does = "what does" in user_msg_lower or "what do" in user_msg_lower
    
    is_lead_capture_question = (
        state.lead_captured and
        (
            (has_why_question and has_details_reference) or
            (has_what_does and ("that" in user_msg_lower or "this" in user_msg_lower or "lead" in last_agent_msg.lower() or "captured" in last_agent_msg.lower())) or
            any(phrase in user_msg_lower for phrase in [
                "why these", "why my", "what about my", "what will you do", "what happens to"
            ])
        )
    )
    
    if is_lead_capture_question:
        response = (
            "I collected your details (name, email, and platform) to create your account and "
            "set up your AutoStream subscription. This information helps us:\n"
            "- Personalize your experience\n"
            "- Send you important updates about your account\n"
            "- Understand which platform you create content on to provide relevant features\n\n"
            "Your information is secure and will only be used for account management and service delivery."
        )
    else:
        # Check for gratitude/thanks messages
        user_msg_lower = user_message.lower().strip()
        is_gratitude = any(phrase in user_msg_lower for phrase in [
            "thanks", "thank you", "thank", "appreciate", "grateful", "ty", "thx"
        ])
        
        if is_gratitude:
            response = "You're welcome! Is there anything else I can help you with?"
        else:
            # Detect intent for new messages
            state.intent = detect_intent(user_message)

            if state.intent == "greeting":
                response = "Hi! How can I help you with AutoStream today?"
            elif state.intent == "product_inquiry":
                # Use conversation history to provide context-aware answers
                response = retrieve_answer(user_message, state.conversation_history)
            elif state.intent == "high_intent":
                # Reset lead capture state if starting a new high_intent flow
                if state.lead_captured:
                    # Reset for new lead
                    state.name = None
                    state.email = None
                    state.platform = None
                    state.lead_captured = False
                response = "Great! May I know your name?"
            else:
                response = "How else can I help?"
    
    # Add agent response to history
    state.conversation_history.append(("assistant", response))
    return response

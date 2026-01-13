
import json
from pathlib import Path

def load_knowledge():
    # Get the project root directory (parent of 'agent' folder)
    project_root = Path(__file__).parent.parent
    kb_path = project_root / "data" / "knowledge_base.json"
    with open(kb_path) as f:
        return json.load(f)

def retrieve_answer(query: str, conversation_history=None) -> str:
    kb = load_knowledge()
    q = query.lower()
    
    # Check for questions about what AutoStream is
    is_about_autostream = (
        any(phrase in q for phrase in [
            "what is autostream", "what's autostream", "what does autostream",
            "tell me about autostream", "describe autostream", "explain autostream"
        ]) or
        (any(word in q for word in ["what", "tell me", "describe", "explain"]) and "autostream" in q)
    )
    
    if is_about_autostream:
        basic = kb['pricing']['basic']
        pro = kb['pricing']['pro']
        return (
            "AutoStream is a SaaS product that provides automated video editing tools for content creators. "
            "We help creators edit their videos efficiently with features like:\n\n"
            f"**Our Plans:**\n"
            f"- **Basic Plan** ({basic['price']}): {basic['videos']}, {basic['resolution']} resolution\n"
            f"- **Pro Plan** ({pro['price']}): {pro['videos']} videos, {pro['resolution']} resolution, "
            f"{', '.join(pro.get('features', []))}\n\n"
            "Would you like to know more about our pricing plans or specific features?"
        )
    
    # Check for comparison/difference requests FIRST (these should always return both plans)
    is_comparison_request = any(phrase in q for phrase in [
        "difference", "compare", "comparison", "both plans", "two plans", 
        "all plans", "each plan", "versus", "vs", "which plan"
    ])
    
    # Check for specific plan mentions in CURRENT query (use word boundaries to avoid partial matches)
    # Split query into words to avoid matching "basic" inside "difference"
    q_words = q.split()
    is_pro_plan_current = any(word in ["pro", "professional", "premium"] for word in q_words) or \
                         any(phrase in q for phrase in ["pro plan", "professional plan", "premium plan"])
    is_basic_plan_current = any(word in ["basic", "starter", "standard"] for word in q_words) or \
                           any(phrase in q for phrase in ["basic plan", "starter plan", "standard plan"])
    
    # Only use conversation history if current query is ambiguous but related to plans
    # AND doesn't explicitly mention a plan
    use_history_for_plans = (
        conversation_history and 
        not is_pro_plan_current and 
        not is_basic_plan_current and
        any(word in q for word in ["plan", "price", "pricing", "cost", "subscription", "monthly", "fee"])
    )
    
    if use_history_for_plans:
        # Look through recent conversation for plan mentions
        recent_context = " ".join([msg for role, msg in conversation_history[-6:] if role == "user"]).lower()
        is_pro_plan_history = any(word in recent_context for word in ["pro", "professional", "premium"])
        is_basic_plan_history = any(word in recent_context for word in ["basic", "starter", "standard"])
        is_pro_plan = is_pro_plan_history
        is_basic_plan = is_basic_plan_history
    else:
        # Use current query only
        is_pro_plan = is_pro_plan_current
        is_basic_plan = is_basic_plan_current

    # Check for general inquiries about plans (tell me about, information about, etc.)
    is_general_plan_inquiry = (
        (is_pro_plan_current or is_basic_plan_current) and
        any(phrase in q for phrase in ["tell me", "about", "information", "details", "what is", "what's"])
    )
    
    # Policy inquiries - check BEFORE plan inquiries to handle "policy on this plan" questions
    is_policy_inquiry = any(word in q for word in ["policy", "policies", "refund", "money back", "cancel", "cancellation", "support"])
    
    if is_policy_inquiry:
        # Check if asking about policy for a specific plan
        if is_pro_plan_current:
            return (
                f"**Pro Plan Policies:**\n"
                f"- Refund: {kb['policies']['refund']}\n"
                f"- Support: {kb['policies']['support']}"
            )
        elif is_basic_plan_current:
            return (
                f"**Basic Plan Policies:**\n"
                f"- Refund: {kb['policies']['refund']}\n"
                f"- Support: 24/7 support is only available on the Pro plan"
            )
        elif "refund" in q or "money back" in q or "cancel" in q or "cancellation" in q:
            return f"Our refund policy: {kb['policies']['refund']}"
        elif "support" in q and not any(phrase in q for phrase in ["what can", "what do", "how can", "how do"]):
            return f"Support information: {kb['policies']['support']}"
        else:
            # General policy question
            return (
                f"**Company Policies:**\n"
                f"- Refund Policy: {kb['policies']['refund']}\n"
                f"- Support: {kb['policies']['support']}"
            )
    
    # Pricing/plan inquiries
    if any(word in q for word in ["price", "pricing", "plan", "cost", "subscription", "monthly", "fee"]) or is_comparison_request or is_general_plan_inquiry:
        # If asking for comparison, always return both plans
        if is_comparison_request:
            basic = kb['pricing']['basic']
            pro = kb['pricing']['pro']
            response = (
                f"Here's a comparison of our plans:\n\n"
                f"**Basic Plan:** {basic['price']}\n"
                f"- {basic['videos']}\n"
                f"- {basic['resolution']} resolution\n\n"
                f"**Pro Plan:** {pro['price']}\n"
                f"- {pro['videos']} videos\n"
                f"- {pro['resolution']} resolution\n"
            )
            if 'features' in pro:
                response += f"- Includes: {', '.join(pro['features'])}\n"
            response += (
                f"\n**Key Differences:**\n"
                f"- Pro Plan offers unlimited videos vs Basic's 10 videos/month\n"
                f"- Pro Plan has 4K resolution vs Basic's 720p\n"
                f"- Pro Plan includes AI captions (not available in Basic)"
            )
            return response
        # If user asks about a specific plan, return only that plan
        elif is_pro_plan and not is_basic_plan:
            pro = kb['pricing']['pro']
            response = (
                f"**Pro Plan:** {pro['price']}\n"
                f"- {pro['videos']} videos\n"
                f"- {pro['resolution']} resolution\n"
            )
            if 'features' in pro:
                response += f"- Includes: {', '.join(pro['features'])}\n"
            return response
        elif is_basic_plan and not is_pro_plan:
            basic = kb['pricing']['basic']
            response = (
                f"**Basic Plan:** {basic['price']}\n"
                f"- {basic['videos']}\n"
                f"- {basic['resolution']} resolution\n"
            )
            return response
        else:
            # User asked about plans in general, return both
            basic = kb['pricing']['basic']
            pro = kb['pricing']['pro']
            response = (
                f"Here are our pricing plans:\n\n"
                f"**Basic Plan:** {basic['price']}\n"
                f"- {basic['videos']}\n"
                f"- {basic['resolution']} resolution\n\n"
                f"**Pro Plan:** {pro['price']}\n"
                f"- {pro['videos']} videos\n"
                f"- {pro['resolution']} resolution\n"
            )
            if 'features' in pro:
                response += f"- Includes: {', '.join(pro['features'])}\n"
            return response


    # Feature inquiries - general questions about what the service provides
    if any(word in q for word in ["feature", "what can", "capabilities", "do", "offer", "provide", "provides", "include", "includes", "service", "services"]):
        # Only return specific plan if explicitly mentioned in CURRENT query
        # General questions like "what do you provide?" should get general answer
        if is_pro_plan_current:
            pro = kb['pricing']['pro']
            response = (
                f"The Pro Plan includes:\n"
                f"- {pro['videos']} videos\n"
                f"- {pro['resolution']} resolution\n"
            )
            if 'features' in pro:
                response += f"- {', '.join(pro['features'])}\n"
            response += f"\nPrice: {pro['price']}"
            return response
        elif is_basic_plan_current:
            basic = kb['pricing']['basic']
            response = (
                f"The Basic Plan includes:\n"
                f"- {basic['videos']}\n"
                f"- {basic['resolution']} resolution\n"
                f"\nPrice: {basic['price']}"
            )
            return response
        else:
            # General question - provide overview of the service
            basic = kb['pricing']['basic']
            pro = kb['pricing']['pro']
            response = (
                "AutoStream is a video editing SaaS platform that helps content creators edit their videos. "
                "We offer two plans:\n\n"
                f"**Basic Plan** ({basic['price']}): {basic['videos']}, {basic['resolution']} resolution\n"
                f"**Pro Plan** ({pro['price']}): {pro['videos']} videos, {pro['resolution']} resolution, "
                f"{', '.join(pro.get('features', []))}\n\n"
                "Would you like to know more about a specific plan?"
            )
            return response

    # General capability questions
    if any(phrase in q for phrase in ["what can you help", "what can you do", "what do you do", 
                                      "how can you help", "what are you", "what services"]):
        return (
            "I can help you with:\n"
            "• Information about AutoStream's pricing plans (Basic and Pro)\n"
            "• Details about our video editing features and capabilities\n"
            "• Company policies (refunds, support)\n"
            "• Signing up for an AutoStream account\n\n"
            "What would you like to know more about?"
        )
    
    return "I can help you with pricing plans, refund policies, and support information. Could you please clarify your question?"

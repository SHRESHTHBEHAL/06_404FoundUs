"""
Conversation Summarization Service.

Handles compression and summarization of conversation history
to maintain context in long sessions without overwhelming the LLM.
"""

import time
from typing import List
from ..models import ConversationTurn, ConversationSummary, SharedState
from ..llm import generate_text


# Configuration
SUMMARIZATION_THRESHOLD = 10  # Summarize when we have more than this many turns
KEEP_RECENT_TURNS = 6  # Always keep the last N turns unsummarized


def should_summarize(history: List[ConversationTurn]) -> bool:
    """
    Determine if conversation history should be summarized.
    
    Args:
        history: List of conversation turns
    
    Returns:
        True if summarization is needed
    """
    return len(history) > SUMMARIZATION_THRESHOLD


def summarize_conversation(turns: List[ConversationTurn]) -> str:
    """
    Create a concise summary of conversation turns using Gemini.
    
    Args:
        turns: List of conversation turns to summarize
    
    Returns:
        Summary text
    """
    if not turns:
        return ""
    
    # Build conversation text
    conversation_text = "\n".join([
        f"{turn.sender.upper()}: {turn.text}"
        for turn in turns
    ])
    
    system_prompt = """You are a conversation summarizer. Create a concise summary of this travel planning conversation that captures:
1. What the user was searching for (destinations, dates, preferences)
2. Key results or information provided
3. Any decisions or selections made
4. Important user preferences mentioned

Keep the summary brief (2-3 sentences) but informative enough to maintain context.
Focus on facts, not conversational pleasantries."""

    user_message = f"Summarize this conversation segment:\n\n{conversation_text}"
    
    try:
        summary = generate_text(system_prompt, user_message, temperature=0.3)
        return summary.strip()
    except Exception as e:
        print(f"Error summarizing conversation: {e}")
        # Fallback: simple concatenation
        return f"Discussion about travel plans involving {len(turns)} messages."


def compress_history(state: SharedState) -> SharedState:
    """
    Compress conversation history by summarizing older turns.
    Keeps recent turns intact, summarizes older ones.
    
    Args:
        state: Current shared state
    
    Returns:
        Updated state with compressed history
    """
    history = state.conversation_history
    
    # Check if summarization is needed
    if not should_summarize(history):
        return state
    
    # Split history: old turns to summarize, recent turns to keep
    turns_to_summarize = history[:-KEEP_RECENT_TURNS] if len(history) > KEEP_RECENT_TURNS else []
    recent_turns = history[-KEEP_RECENT_TURNS:] if len(history) > KEEP_RECENT_TURNS else history
    
    if not turns_to_summarize:
        return state
    
    print(f"[Summarization] Compressing {len(turns_to_summarize)} turns, keeping {len(recent_turns)} recent")
    
    # Generate summary
    summary_text = summarize_conversation(turns_to_summarize)
    
    # Create summary object
    summary = ConversationSummary(
        summary_text=summary_text,
        turn_count=len(turns_to_summarize),
        start_timestamp=turns_to_summarize[0].timestamp,
        end_timestamp=turns_to_summarize[-1].timestamp
    )
    
    # Update state
    state.conversation_summaries.append(summary)
    state.conversation_history = recent_turns
    
    print(f"[Summarization] Created summary: {summary_text[:100]}...")
    
    return state


def get_full_context(state: SharedState) -> str:
    """
    Get full conversation context including summaries and recent turns.
    Useful for providing context to LLM.
    
    Args:
        state: Current shared state
    
    Returns:
        Formatted context string
    """
    context_parts = []
    
    # Add summaries of older conversations
    if state.conversation_summaries:
        summaries_text = "\n\n".join([
            f"[Earlier conversation - {s.turn_count} messages]: {s.summary_text}"
            for s in state.conversation_summaries
        ])
        context_parts.append(f"Previous conversation context:\n{summaries_text}")
    
    # Add recent conversation
    if state.conversation_history:
        recent_text = "\n".join([
            f"{turn.sender}: {turn.text}"
            for turn in state.conversation_history[-5:]  # Last 5 turns
        ])
        context_parts.append(f"Recent conversation:\n{recent_text}")
    
    return "\n\n".join(context_parts) if context_parts else ""

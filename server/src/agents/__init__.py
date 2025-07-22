"""
AI Hedge Fund Agents Module

This module contains all the AI analyst agents that perform financial analysis
using different investment strategies and methodologies.
"""

# Import all agent functions
from .warren_buffett import warren_buffett_agent
from .ben_graham import ben_graham_agent
from .charlie_munger import charlie_munger_agent
from .peter_lynch import peter_lynch_agent
from .phil_fisher import phil_fisher_agent
from .cathie_wood import cathie_wood_agent
from .michael_burry import michael_burry_agent
from .stanley_druckenmiller import stanley_druckenmiller_agent
from .bill_ackman import bill_ackman_agent
from .sentiment import sentiment_agent

# Define available agents
AVAILABLE_AGENTS = {
    "warren_buffett": warren_buffett_agent,
    "ben_graham": ben_graham_agent,
    "charlie_munger": charlie_munger_agent,
    "peter_lynch": peter_lynch_agent,
    "phil_fisher": phil_fisher_agent,
    "cathie_wood": cathie_wood_agent,
    "michael_burry": michael_burry_agent,
    "stanley_druckenmiller": stanley_druckenmiller_agent,
    "bill_ackman": bill_ackman_agent,
    "sentiment": sentiment_agent,
}

# Agent categories for organization
VALUE_INVESTORS = ["warren_buffett", "ben_graham", "charlie_munger"]
GROWTH_INVESTORS = ["peter_lynch", "phil_fisher", "cathie_wood"]
SPECIALISTS = ["michael_burry", "stanley_druckenmiller", "bill_ackman"]
TECHNICAL_ANALYSTS = ["sentiment"]

# Agent descriptions
AGENT_DESCRIPTIONS = {
    "warren_buffett": "Value investing legend focusing on intrinsic value, moats, and management quality",
    "ben_graham": "Father of value investing, emphasizes margin of safety and fundamental analysis",
    "charlie_munger": "Mental models and quality business analysis with psychological insights",
    "peter_lynch": "Growth investing expert who looks for companies you can understand",
    "phil_fisher": "Growth investor focusing on quality management and long-term business prospects",
    "cathie_wood": "Innovation-focused growth investor specializing in disruptive technologies",
    "michael_burry": "Contrarian investor known for identifying market bubbles and short opportunities",
    "stanley_druckenmiller": "Macro trader focusing on big picture economic trends and currency movements",
    "bill_ackman": "Activist investor who takes concentrated positions in high-conviction ideas",
    "sentiment": "Market sentiment analysis using news, social media, and technical indicators",
}

def get_agent(agent_name: str):
    """
    Get an agent function by name.
    
    Args:
        agent_name: Name of the agent to retrieve
        
    Returns:
        Agent function if found, None otherwise
    """
    return AVAILABLE_AGENTS.get(agent_name)

def get_all_agents():
    """
    Get all available agents.
    
    Returns:
        Dictionary mapping agent names to their functions
    """
    return AVAILABLE_AGENTS.copy()

def get_agents_by_category(category: str):
    """
    Get agents by category.
    
    Args:
        category: Category name ('value_investors', 'growth_investors', 'specialists', 'technical_analysts')
        
    Returns:
        Dictionary of agents in the specified category
    """
    category_map = {
        "value_investors": VALUE_INVESTORS,
        "growth_investors": GROWTH_INVESTORS,
        "specialists": SPECIALISTS,
        "technical_analysts": TECHNICAL_ANALYSTS,
    }
    
    agent_names = category_map.get(category, [])
    return {name: AVAILABLE_AGENTS[name] for name in agent_names if name in AVAILABLE_AGENTS}

def get_agent_description(agent_name: str) -> str:
    """
    Get description for a specific agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Agent description if found, empty string otherwise
    """
    return AGENT_DESCRIPTIONS.get(agent_name, "")

# Export all agent functions for direct import
__all__ = [
    "warren_buffett_agent",
    "ben_graham_agent", 
    "charlie_munger_agent",
    "peter_lynch_agent",
    "phil_fisher_agent",
    "cathie_wood_agent",
    "michael_burry_agent",
    "stanley_druckenmiller_agent",
    "bill_ackman_agent",
    "sentiment_agent",
    "AVAILABLE_AGENTS",
    "VALUE_INVESTORS",
    "GROWTH_INVESTORS", 
    "SPECIALISTS",
    "TECHNICAL_ANALYSTS",
    "AGENT_DESCRIPTIONS",
    "get_agent",
    "get_all_agents",
    "get_agents_by_category",
    "get_agent_description",
]

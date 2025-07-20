from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination


def get_team(problem_solver_agent, code_executor_agent):
    """
    Create a team with the problem solver agent and the code executor agent.

    Args:
        problem_solver_agent: The agent responsible for solving problems.
        code_executor_agent: The agent responsible for executing code.

    Returns:
        RoundRobinGroupChat: A team that includes both agents.
    """
    team = RoundRobinGroupChat(
        participants=[problem_solver_agent, code_executor_agent],
        termination_condition=TextMentionTermination("STOP"),
        max_turns=15,
    )

    return team
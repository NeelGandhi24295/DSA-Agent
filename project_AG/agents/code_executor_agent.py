from autogen_agentchat.agents import CodeExecutorAgent



def get_code_executor_agent(docker_executor):
    """
    Create a CodeExecutorAgent with the provided Docker executor.

    Args:
        docker_executor: The Docker executor to be used by the agent.

    Returns:
        CodeExecutorAgent: An instance of CodeExecutorAgent configured with the Docker executor.
    """
    code_executor_agent = CodeExecutorAgent(
        name="CodeExecutorAgent",
        description="An agent that executes code in a Docker container.",
        code_executor=docker_executor
    )

    return code_executor_agent
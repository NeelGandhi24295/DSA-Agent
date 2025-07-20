import streamlit as st
import asyncio
import os
import json

from config.docker_utils import get_docker_executor, start_docker_executor, stop_docker_executor
from config.model_client import get_model_client
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult
from agents.problem_solver_agent import get_problem_solver_agent
from agents.code_executor_agent import get_code_executor_agent
from team.dsa_solver_team import get_team
from config.constants import DOCKER_WORK_DIR

st.title('DSA Solver Agent')

# ensure persistence folder exists
os.makedirs(DOCKER_WORK_DIR, exist_ok=True)
MSG_FILE = os.path.join(DOCKER_WORK_DIR, "dsa_messages.json")

# load or init messages
if 'dsa_messages' not in st.session_state:
    if os.path.exists(MSG_FILE):
        with open(MSG_FILE, 'r') as f:
            st.session_state['dsa_messages'] = json.load(f)
    else:
        st.session_state['dsa_messages'] = []

if 'dsa_team_state' not in st.session_state:
    st.session_state['dsa_team_state'] = None

task = st.chat_input("Describe the DSA problem you want solved")

async def run_dsa_team(docker, model_client, task):
    try:
        await start_docker_executor(docker)
        problem_solver = get_problem_solver_agent(model_client)
        code_executor = get_code_executor_agent(docker)
        team = get_team(problem_solver, code_executor)

        if st.session_state.dsa_team_state:
            await team.load_state(st.session_state.dsa_team_state)

        async for message in team.run_stream(task=task):
            if isinstance(message, TextMessage):
                msg = f"{message.source}: {message.content}"
            else:  # TaskResult
                msg = f"Task Result: {message.stop_reason}"

            st.markdown(f"> {msg}")
            st.session_state.dsa_messages.append(msg)

            # persist immediately
            with open(MSG_FILE, 'w') as f:
                json.dump(st.session_state.dsa_messages, f)

        st.session_state.dsa_team_state = await team.save_state()

    except Exception as e:
        st.error(f"Error running DSA solver team: {e}")
    finally:
        await stop_docker_executor(docker)

# display history
for m in st.session_state.dsa_messages:
    st.markdown(f"> {m}")

if task:
    docker = get_docker_executor()
    model_client = get_model_client()
    asyncio.run(run_dsa_team(docker, model_client, task))

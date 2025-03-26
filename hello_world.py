from agents import Agent, Runner
import agentops

# Initialize AgentOps
agentops.init()

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

# Output:
# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.
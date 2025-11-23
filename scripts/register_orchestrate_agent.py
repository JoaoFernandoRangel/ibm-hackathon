"""Example: register the orchestrate tools with IBM watsonx Orchestrate AgentBuilder.

This is an illustrative example. The exact AgentBuilder API may vary with SDK versions.
Check IBM watsonx Orchestrate documentation for the correct registration/deployment steps.
"""
try:
    from ibm_watsonx_orchestrate.agent_builder import AgentBuilder
except Exception:
    AgentBuilder = None

from src.orchestrate_tools import (
    orchestrate_followup_workflow,
    send_followup_email if 'send_followup_email' in globals() else None,
)


def main():
    if AgentBuilder is None:
        print("AgentBuilder SDK not available. Install `ibm-watsonx-orchestrate` package and retry.")
        return

    builder = AgentBuilder(name="followup-agent")

    # Register tools exported by our module
    # The `@tool` decorator already registers metadata; AgentBuilder may accept functions directly.
    builder.add_tool(orchestrate_followup_workflow)

    agent = builder.build()

    # For demonstration only: print agent manifest / metadata (if available)
    try:
        manifest = agent.to_dict()
        print("Agent manifest:")
        import json
        print(json.dumps(manifest, indent=2))
    except Exception:
        print("Agent built. Refer to IBM documentation to deploy this agent into Orchestrate.")


if __name__ == '__main__':
    main()

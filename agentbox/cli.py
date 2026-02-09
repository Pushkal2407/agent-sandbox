"""CLI interface for AgentBox."""

import argparse
import sys

from agentbox import AgentRuntime
from agentbox.logger import AuditLogger
from agentbox.model.openai_client import OpenAIClient
from agentbox.policy import Policy
from agentbox.runtime import BudgetExceededError, MaxIterationsError
from agentbox.tools.filesystem import ReadFileTool
from agentbox.tools.web import WebRequestTool


def main():
    """CLI entrypoint for AgentBox."""
    parser = argparse.ArgumentParser(
        description="AgentBox - AI agent runtime with policy enforcement",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # 'run' subcommand
    run_parser = subparsers.add_parser(
        "run",
        help="Run an agent with a prompt and policy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agentbox run --prompt "Research the API" --policy examples/policies/restricted.yaml
  agentbox run --prompt "Fetch data" --policy policy.yaml --log audit.jsonl
  agentbox run --prompt "Task" --policy policy.yaml --model gpt-4o
        """
    )
    
    run_parser.add_argument(
        "--prompt",
        required=True,
        help="User prompt/task for the agent"
    )
    
    run_parser.add_argument(
        "--policy",
        required=True,
        help="Path to policy YAML file"
    )
    
    run_parser.add_argument(
        "--log",
        help="Path to audit log file (JSONL format)"
    )
    
    run_parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)"
    )
    
    run_parser.add_argument(
        "--max-iterations",
        type=int,
        default=10,
        help="Maximum runtime iterations (default: 10)"
    )
    
    args = parser.parse_args()
    
    # Require a subcommand
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Initialize components
        print(f"Loading policy: {args.policy}")
        policy = Policy.load(args.policy)
        
        print(f"Initializing model: {args.model}")
        model = OpenAIClient(model=args.model)
        
        tools = [ReadFileTool(), WebRequestTool()]
        print(f"Tools available: {[t.name for t in tools]}")
        
        # Initialize logger if specified
        logger = None
        if args.log:
            print(f"Audit logging to: {args.log}")
            logger = AuditLogger(args.log)
        
        # Create runtime
        runtime = AgentRuntime(model, tools, policy, logger)
        
        # Execute agent
        print("\n" + "=" * 60)
        print(f"PROMPT: {args.prompt}")
        print("=" * 60 + "\n")
        
        messages = [{"role": "user", "content": args.prompt}]
        response = runtime.run(messages, max_iterations=args.max_iterations)
        
        print("\n" + "=" * 60)
        print("AGENT RESPONSE:")
        print("=" * 60)
        print(response)
        print()
        
        if logger:
            logger.close()
            print(f"\n✓ Audit log saved to: {args.log}")
        
        print("\n✓ Task completed successfully")
        
    except BudgetExceededError as e:
        print(f"\n⛔ Budget exceeded: {e}", file=sys.stderr)
        if logger:
            logger.close()
        sys.exit(1)
    
    except MaxIterationsError as e:
        print(f"\n⚠ Max iterations reached: {e}", file=sys.stderr)
        if logger:
            logger.close()
        sys.exit(1)
    
    except FileNotFoundError as e:
        print(f"\n✗ File not found: {e}", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        if logger:
            logger.close()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

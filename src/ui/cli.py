import sys
import os
from rich.console import Console
from rich.panel import Panel
from langchain_core.messages import HumanMessage, AIMessage

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.graphs.workflow import InterviewWorkflow

console = Console()


def main():
    console.print(
        Panel(
            "[bold magenta]AI Research Interviewer[/bold magenta]\n[dim]Powered by LangGraph & Ollama[/dim]",
            subtitle="CLI Version 3.0 (Graph)",
        )
    )

    # 1. Input Topic
    topic = console.input(
        "\n[bold green]What topic would you like to discuss today? > [/]"
    )
    if not topic:
        console.print("[red]Topic cannot be empty.[/red]")
        return

    # 2. Initialize Workflow
    # The graph expects a state with "topic".
    # The initial run will trigger the Planner, then the Interviewer (providing the first question).
    workflow = InterviewWorkflow()
    state = {"topic": topic, "messages": []}

    console.print(f"\n[dim]Initializing interview on topic: {topic}...[/dim]")

    try:
        # Initial Invoke
        with console.status(
            "[bold cyan]Planning & Generating First Question...[/bold cyan]"
        ):
            output = workflow.invoke(state)

        # Update our local state tracker with the output
        state = output

        # Display Plan (Optional, maybe debug only? Or nice for user?)
        if "interview_plan" in output and output["interview_plan"]:
            plan = output["interview_plan"]
            console.print(f"[dim]Plan: {plan.interview_goal}[/dim]")
            # console.print(f"[dim]Phases: {', '.join(plan.phases)}[/dim]")

        # Display First Question
        if "messages" in output and output["messages"]:
            last_msg = output["messages"][-1]
            if isinstance(last_msg, AIMessage):
                console.print(f"\n[bold cyan]AI:[/bold cyan] {last_msg.content}")

        # 3. Interview Loop
        while True:
            # Check if analysis is already present (e.g. if the graph decided to end immediately, unlikely)
            if "insights" in state and state["insights"]:
                break

            # Get User Input
            user_input = console.input("\n[bold yellow]User:[/bold yellow] ")

            if user_input.lower() in ["/quit", "/exit"]:
                console.print("[red]Exiting...[/red]")
                return

            # Append User Message to State
            # Note: We append to the list key "messages" in the dictionary we pass to invoke.
            # Since `state` is a dict returned by invoke, it has the full history if we didn't use a checkpointer.
            # If we are stateless (dict passing), we need to ensure we pass the UPDATED list.
            # `output` from invoke contains the full updated state.

            # Create new inputs for the next turn
            # We can just pass the user message if the graph handles distinct inputs,
            # BUT our graph definition uses `InterviewState` which expects the full state or partial updates.
            # Since we are running the compiled graph on a dict state without persistence ID,
            # safe bet is to pass the current accumulated state + new message.

            # Actually, standard LangGraph `invoke` with a dict returns the new state.
            # So `state` variable holds the full history.
            # We just need to append the new message to `state["messages"]`.
            state["messages"].append(HumanMessage(content=user_input))

            with console.status("[dim]Thinking...[/dim]"):
                output = app.invoke(state)

            state = output

            # Display AI Response
            if ("messages" in output and output["messages"]) or ("interview_complete" in state and state["interview_complete"]):
                last_msg = output["messages"][-1]
                if isinstance(last_msg, AIMessage):
                    console.print(f"\n[bold cyan]AI:[/bold cyan] {last_msg.content}")

        # 4. End & Analysis
        console.print("\n[bold magenta]Interview Complete![/bold magenta]")

        if "insights" in state and state["insights"]:
            insights = state["insights"]
            console.print(
                Panel(
                    f"[bold]Summary:[/bold] {insights.summary}\n\n[bold]Sentiment Score:[/bold] {insights.sentiment_score}/5",
                    title="Analysis Results",
                )
            )
            console.print(f"[dim]Transcript saved to JSON file.[/dim]")

    except Exception as e:
        console.print(f"[bold red]System Error:[/bold red] {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

import sys
import os
from rich.console import Console
from rich.panel import Panel

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.session import InterviewSession

console = Console()


def main():
    console.print(
        Panel(
            "[bold magenta]AI Research Interviewer[/bold magenta]\n[dim]Powered by Ollama[/dim]",
            subtitle="CLI Version 2.0 (Modular)",
        )
    )

    session = InterviewSession()

    # 1. Input Topic
    topic = console.input(
        "\n[bold green]What topic would you like to discuss today? > [/]"
    )
    if not topic:
        console.print("[red]Topic cannot be empty.[/red]")
        return

    # 2. Start Session (Safety + Planning)
    try:
        with console.status("[bold cyan]Initializing Session...[/bold cyan]"):
            start_msg = session.start(topic)
        console.print(f"\n[bold green]✓ {start_msg}[/bold green]\n")
    except ValueError as e:
        console.print(f"[bold red]{e}[/bold red]")
        return
    except Exception as e:
        console.print(f"[bold red]System Error:[/bold red] {e}")
        return

    # 3. Handshake
    opening_msg = session.get_opening_message(topic)
    console.print(f"\n[bold cyan]AI:[/bold cyan] {opening_msg}")

    try:
        user_input = console.input("\n[bold yellow]User:[/bold yellow] ")
        # Initial user input processing (Handshake response)
        # Note: Session expects next call to be process_user_input which triggers the first phase response
        # We need to feed this handshake response in.

        # However, sesssion.process_user_input immediately generates the NEXT AI question.
        # So we pass the handshake answer, and get back the Phase 1 Question.

        while True:
            with console.status("[dim]Thinking...[/dim]"):
                ai_response = session.process_user_input(user_input)

            console.print(f"\n[bold cyan]AI:[/bold cyan] {ai_response}")

            if not session.is_active:
                break

            user_input = console.input("\n[bold yellow]User:[/bold yellow] ")

    except ValueError as e:  # Safety Violation
        console.print(f"\n[bold red]{e}[/bold red]")
        return
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        return

    # 4. End & Save
    console.print("\n[bold magenta]Interview Complete![/bold magenta] Analyzing...")
    try:
        with console.status("[bold cyan]Generating Analysis...[/bold cyan]"):
            filepath = session.end_session()
        console.print(f"\n[dim]Interview saved to: {filepath}[/dim]")
    except Exception as e:
        console.print(f"[red]Error saving analysis:[/red] {e}")


if __name__ == "__main__":
    main()

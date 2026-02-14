import sys
import os
from rich.console import Console
from rich.panel import Panel

# Add project root to path
# Add project root/src to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from core.session import InterviewSession

console = Console()


def main():
    console.print(
        Panel(
            "[bold magenta]AI Research Interviewer[/bold magenta]",
            subtitle="CLI Interviewer",
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

        while True:
            with console.status("[dim]Thinking...[/dim]"):
                response = session.process_user_input(user_input)

            # Extract message from SessionResponse
            if response.success:
                console.print(f"\n[bold cyan]AI:[/bold cyan] {response.message}")
            else:
                console.print(f"\n[bold red]Error:[/bold red] {response.error}")
                break

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
            filepath, analysis = session.end_session()
        console.print(f"\n[dim]Interview saved to: {filepath}[/dim]")
    except Exception as e:
        console.print(f"[red]Error saving analysis:[/red] {e}")


if __name__ == "__main__":
    main()

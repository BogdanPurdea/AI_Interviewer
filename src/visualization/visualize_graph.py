import sys
import os

# Ensure src is in path regardless of where script is run
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(
    os.path.dirname(current_dir)
)  # Up from src/visualization to root
sys.path.append(os.path.join(project_root, "src"))

from core.graphs.workflow import InterviewWorkflow
from core.graphs.interviewer_graph import InterviewerGraph

def visualize():
    # Save outputs in the same directory as the script
    output_dir = current_dir
    output_path = os.path.join(output_dir, "workflow_graph.png")
    mermaid_path = os.path.join(output_dir, "workflow_graph.mmd")

    print("Generating Mermaid Graph...")
    graph = InterviewerGraph().graph.get_graph()
    # Save Mermaid content
    mermaid_content = graph.draw_mermaid()
    with open(mermaid_path, "w") as f:
        f.write(mermaid_content)
    print(f"Mermaid file saved to {mermaid_path}")

    # Try to generate PNG
    try:
        print("Attempting to generate PNG...")
        png_bytes = graph.draw_mermaid_png()
        with open(output_path, "wb") as f:
            f.write(png_bytes)
        print(f"Graph visualization saved to {output_path}")
    except Exception as e:
        print(
            f"Could not generate PNG (likely missing dependencies like graphviz/io): {e}"
        )
        print("You can view the .mmd file in a Mermaid live editor.")


if __name__ == "__main__":
    visualize()

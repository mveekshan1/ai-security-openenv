"""
Gradio UI for OpenEnv AI Security Environment
Interactive cybersecurity threat detection evaluation
"""

import gradio as gr
import os
from inference import run_benchmark


def run_agent() -> str:
    """Run agent inference safely"""
    try:
        result = run_benchmark(num_episodes=1)
        return result
    except Exception as e:
        return f"Error: {str(e)}"


def get_tasks() -> list[str]:
    """Get available tasks"""
    return [
        "Data Leakage Prevention (Easy)",
        "Threat Detection (Medium)",
        "Advanced Threat Response (Hard)"
    ]


def create_ui() -> gr.Blocks:
    """Create Gradio interface"""

    with gr.Blocks(title="AI Security OpenEnv", theme=gr.themes.Soft()) as demo:

        gr.Markdown("""
        # Security OpenEnv

        Evaluate AI cybersecurity threat detection and response
        """)

        with gr.Row():
            task_dropdown = gr.Dropdown(
                choices=get_tasks(),
                label="Select Task",
                value=get_tasks()[0]
            )
            run_btn = gr.Button("Run", variant="primary")

        results = gr.Textbox(label="Results", lines=20)

        def execute(task_name):
            return run_agent()

        run_btn.click(fn=execute, inputs=[task_dropdown], outputs=[results])

    return demo


def main():
    """Launch UI"""
    port = int(os.environ.get("PORT", 7860))
    demo = create_ui()
    demo.launch(server_name="0.0.0.0", server_port=port, show_error=True)


if __name__ == "__main__":
    main()
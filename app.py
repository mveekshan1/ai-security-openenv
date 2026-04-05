"""
Enterprise Dashboard for AI Security OpenEnv
Threat detection and response evaluation system
"""

import gradio as gr
import json
import os
from typing import Dict, Any
from inference import run_dashboard_simulation, run_benchmark, format_benchmark_json


def create_dashboard() -> gr.Blocks:
    """Create professional enterprise dashboard"""

    with gr.Blocks(title="AI Security OpenEnv") as demo:

        # Header
        gr.Markdown("# AI Security OpenEnv")
        gr.Markdown("Threat Detection & Response Evaluation System")

        # Controls
        with gr.Row():
            num_episodes = gr.Slider(
                minimum=1, maximum=10, value=1, step=1,
                label="Episodes",
                container=True
            )
            with gr.Column(min_width=100):
                gr.Markdown("")  # Spacer
                run_button = gr.Button("Run Evaluation", size="lg")

        # Two-column panel: Event | Decision
        gr.Markdown("## Live Event")
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Event Details")
                event_id = gr.Textbox(label="Event ID", interactive=False)
                event_severity = gr.Textbox(label="Data Sensitivity", interactive=False)
                user_role = gr.Textbox(label="User Role", interactive=False)
                
                event_logs = gr.Code(
                    language="json",
                    label="Security Logs",
                    interactive=False,
                    lines=8
                )

            with gr.Column():
                gr.Markdown("### Agent Decision")
                decision_allow = gr.Textbox(label="Allow Access", interactive=False)
                detected_threat = gr.Textbox(label="Threat Type", interactive=False)
                decision_action = gr.Textbox(label="Response Action", interactive=False)
                
                decision_detail = gr.Code(
                    language="json",
                    label="Decision Details",
                    interactive=False,
                    lines=8
                )

        # Metrics row
        gr.Markdown("## Metrics")
        with gr.Row():
            avg_reward = gr.Number(label="Average Reward", interactive=False, precision=4)
            success_rate = gr.Number(label="Success Rate", interactive=False, precision=4)
            risk_level = gr.Textbox(label="Risk Level", interactive=False)

        # Execution output
        gr.Markdown("## Execution Output")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("**Simulation Results**")
                episode_details = gr.Code(
                    language="json",
                    label="",
                    interactive=False,
                    lines=15
                )
            
            with gr.Column():
                gr.Markdown("**Benchmark Results**")
                benchmark_results = gr.Code(
                    language="json",
                    label="",
                    interactive=False,
                    lines=15
                )

        # Status indicator
        status_box = gr.Textbox(
            value="Ready",
            label="Status",
            interactive=False,
            visible=False
        )

        def run_simulation(num_eps: int) -> tuple:
            """Execute simulation and return results"""
            try:
                result = run_dashboard_simulation()
                
                if "error" in result:
                    return (
                        "Error",
                        "", "", "", "", "", "",
                        "", "", "", "", "",
                        json.dumps(result, indent=2),
                        json.dumps(result, indent=2)
                    )

                event = result.get("latest_event", {})
                decision = result.get("decision", {})
                
                logs = event.get("logs", [])
                logs_formatted = json.dumps(logs, indent=2)
                
                decision_formatted = json.dumps(decision, indent=2)
                risk = result.get("risk_level", "unknown")
                
                benchmark = run_benchmark(num_episodes=int(num_eps))
                benchmark_formatted = format_benchmark_json(benchmark)

                return (
                    "Complete",
                    event.get("event_id", "Unknown"),
                    event.get("data_sensitivity", "Unknown"),
                    event.get("user_role", "Unknown"),
                    logs_formatted,
                    str(decision.get("allow", False)).lower(),
                    decision.get("threat_type", "none"),
                    decision.get("response_action", "allow"),
                    decision_formatted,
                    result.get("average_reward", 0.0),
                    result.get("success_rate", 0.0),
                    risk,
                    json.dumps(result, indent=2),
                    benchmark_formatted
                )
            except Exception as e:
                error_msg = json.dumps({"error": str(e)}, indent=2)
                return (
                    "Error",
                    "", "", "", "", "", "", "", "",
                    0.0, 0.0, "error",
                    error_msg,
                    error_msg
                )

        # Wire button to simulation
        run_button.click(
            fn=run_simulation,
            inputs=[num_episodes],
            outputs=[
                status_box,
                event_id,
                event_severity,
                user_role,
                event_logs,
                decision_allow,
                detected_threat,
                decision_action,
                decision_detail,
                avg_reward,
                success_rate,
                risk_level,
                episode_details,
                benchmark_results
            ]
        )

    return demo


def main():
    """Launch dashboard"""
    port = int(os.environ.get("PORT", 7860))
    demo = create_dashboard()
    demo.launch(
        theme=gr.themes.Base(),
        server_name="0.0.0.0",
        server_port=port,
        show_error=True,
        share=False
    )


if __name__ == "__main__":
    main()
"""
Professional Gradio UI for OpenEnv AI Security Environment
Allows interactive task selection and inference execution
"""

import gradio as gr
import json
import os
import subprocess
import sys
from typing import Dict, Any, List, Optional

from environment import AiSecurityEnv
from tasks import TaskRegistry


class OpenEnvUI:
    """Wrapper for OpenEnv UI interactions"""
    
    def __init__(self):
        self.env = AiSecurityEnv(seed=42)
        self.task_registry = TaskRegistry()
        self.current_state: Optional[Dict[str, Any]] = None
        
    def get_available_tasks(self) -> List[str]:
        """Get list of available tasks"""
        return [
            "Data Leakage Prevention",
            "Threat Detection", 
            "Advanced Threat Response"
        ]
    
    def run_task(self, task_name: str) -> tuple[str, str]:
        """
        Run inference for selected task
        Returns (status, results_json)
        """
        try:
            # Reset environment
            self.current_state = self.env.reset()
            
            # Find matching scenario
            scenario_map = {
                "Data Leakage Prevention": 0,
                "Threat Detection": 1,
                "Advanced Threat Response": 2
            }
            
            scenario_idx = scenario_map.get(task_name, 0)
            scenario = self.env.task_scenarios[scenario_idx]
            
            # Prepare task information
            task_info = {
                "task": task_name,
                "difficulty": scenario.get("difficulty", "N/A"),
                "event_id": scenario.get("event_id"),
                "logs": scenario.get("logs", []),
                "user_role": scenario.get("user_role"),
                "data_sensitivity": scenario.get("data_sensitivity"),
                "expected_response": scenario.get("expected", {})
            }
            
            # Format output
            status = f"✅ Task Loaded: {task_name}\n⏱️  Difficulty: {task_info['difficulty']}"
            results = json.dumps(task_info, indent=2)
            
            return status, results
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            return error_msg, json.dumps({"error": str(e)})
    
    def export_results(self, results_json: str) -> str:
        """Export results to file"""
        try:
            data = json.loads(results_json)
            output_file = "results.json"
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)
            return f"✅ Results exported to {output_file}"
        except Exception as e:
            return f"❌ Export failed: {str(e)}"


def create_ui():
    """Create Gradio interface using Blocks"""
    
    ui = OpenEnvUI()
    
    with gr.Blocks(title="OpenEnv AI Security Simulator", theme=gr.themes.Soft()) as demo:
        
        # Header
        gr.Markdown("""
        # 🔒 OpenEnv AI Security Simulator
        
        Interactive environment for testing AI threat detection & response capabilities.
        
        **Select a cybersecurity task below to begin.**
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### Task Selection")
                task_dropdown = gr.Dropdown(
                    choices=ui.get_available_tasks(),
                    label="Select Security Task",
                    value="Data Leakage Prevention",
                    interactive=True
                )
                
                with gr.Row():
                    run_btn = gr.Button("🚀 Run Task", variant="primary", size="lg")
                    export_btn = gr.Button("💾 Export Results", size="lg")
                
            with gr.Column(scale=1):
                gr.Markdown("### Quick Info")
                info_text = gr.Textbox(
                    label="Status",
                    interactive=False,
                    lines=4,
                    value="Ready to run. Select a task and click 'Run Task'"
                )
        
        gr.Markdown("---")
        
        # Results Section
        gr.Markdown("### Task Details & Results")
        
        with gr.Row():
            results_json = gr.JSON(
                label="Task Information",
                interactive=False
            )
        
        with gr.Row():
            export_status = gr.Textbox(
                label="Export Status",
                interactive=False,
                lines=1,
                value=""
            )
        
        # Event handlers
        def handle_run_task(task_name):
            status, results = ui.run_task(task_name)
            results_dict = json.loads(results)
            return status, results_dict
        
        def handle_export(results_json_obj):
            if not results_json_obj:
                return "❌ No results to export"
            results_str = json.dumps(results_json_obj)
            return ui.export_results(results_str)
        
        # Connect events
        run_btn.click(
            fn=handle_run_task,
            inputs=[task_dropdown],
            outputs=[info_text, results_json]
        )
        
        export_btn.click(
            fn=handle_export,
            inputs=[results_json],
            outputs=[export_status]
        )
        
        # Load initial task info
        task_dropdown.change(
            fn=handle_run_task,
            inputs=[task_dropdown],
            outputs=[info_text, results_json]
        )
        
        gr.Markdown("""
        ---
        **Environment Details:**
        - 🎯 Three difficulty levels: Easy → Medium → Hard
        - 🛡️ Real-world security scenarios: Data Exfiltration, Brute Force, Intrusion
        - 📊 Performance metrics and recommendations
        - 🚀 Compatible with Hugging Face Spaces
        """)
    
    return demo


def main():
    """Main entry point"""
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 7860))
    
    # Allow share if requested
    share = os.environ.get("SHARE", "").lower() == "true"
    
    # Create and launch UI
    demo = create_ui()
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=share,
        show_error=True
    )


if __name__ == "__main__":
    main()
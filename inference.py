"""
OpenAI-compatible agent runner for AI Security environment
Includes evaluation summary and performance metrics.
Serves as a baseline implementation showing how to interact with the environment.
"""

import json
import os
from typing import Any, Dict, List, Optional
from environment import AiSecurityEnv
from tasks import TaskRegistry, GradingEngine


class EvaluationSummary:
    """
    Structured evaluation summary with performance metrics and risk assessment.
    """

    @staticmethod
    def compute_summary(rewards: List[float], episode_count: int) -> Dict[str, Any]:
        """
        Compute structured evaluation summary from episode rewards.

        Args:
            rewards: List of reward values from episodes
            episode_count: Total number of episodes

        Returns:
            {
                "task_scores": [float],
                "average_score": float,
                "median_score": float,
                "success_rate": float,
                "risk_level": "low|medium|high",
                "confidence": float,
                "recommendations": [str]
            }
        """
        if not rewards:
            return {
                "task_scores": [],
                "average_score": 0.0,
                "median_score": 0.0,
                "success_rate": 0.0,
                "risk_level": "high",
                "confidence": 0.0,
                "recommendations": ["No episodes evaluated"]
            }

        # Calculate metrics
        task_scores = rewards
        average_score = sum(rewards) / len(rewards)
        sorted_scores = sorted(rewards)
        median_score = (sorted_scores[len(sorted_scores)//2] if len(sorted_scores) % 2 == 1
                       else (sorted_scores[len(sorted_scores)//2 - 1] + sorted_scores[len(sorted_scores)//2]) / 2)
        
        # Success rate: % of tasks with score >= 0.8
        success_threshold = 0.8
        success_count = sum(1 for score in rewards if score >= success_threshold)
        success_rate = success_count / len(rewards) if rewards else 0.0

        # Risk level assessment based on average score
        if average_score >= 0.85:
            risk_level = "low"
        elif average_score >= 0.70:
            risk_level = "medium"
        else:
            risk_level = "high"

        # Confidence in evaluation
        confidence = min(1.0, len(rewards) / 10.0)  # Scale with episode count

        # Recommendations
        recommendations = EvaluationSummary._generate_recommendations(
            average_score, success_rate, rewards, risk_level
        )

        return {
            "task_scores": [round(s, 4) for s in task_scores],
            "average_score": round(average_score, 4),
            "median_score": round(median_score, 4),
            "success_rate": round(success_rate, 4),
            "risk_level": risk_level,
            "confidence": round(confidence, 4),
            "recommendations": recommendations,
            "total_episodes": episode_count,
            "passing_episodes": success_count
        }

    @staticmethod
    def _generate_recommendations(avg_score: float, success_rate: float,
                                  scores: List[float], risk_level: str) -> List[str]:
        """Generate actionable recommendations based on performance"""
        recommendations = []

        if avg_score >= 0.85:
            recommendations.append("Agent demonstrates strong threat detection capability.")
        elif avg_score >= 0.70:
            recommendations.append("Agent shows competent performance but needs improvement on edge cases.")
        else:
            recommendations.append("Agent requires significant improvement in threat classification.")

        if success_rate < 0.5:
            recommendations.append("Below 50% success rate - review grading criteria alignment.")

        if len(scores) > 0:
            min_score = min(scores)
            max_score = max(scores)
            variance = max_score - min_score

            if variance > 0.6:
                recommendations.append("High score variance detected - performance is inconsistent across tasks.")
            
            if min_score < 0.3:
                recommendations.append("Extremely low scores on some tasks - check for specific failure patterns.")

        if risk_level == "high":
            recommendations.append("Risk level HIGH - not suitable for production deployment.")
        elif risk_level == "medium":
            recommendations.append("Risk level MEDIUM - recommend additional testing before deployment.")
        else:
            recommendations.append("Risk level LOW - suitable for controlled production deployment.")

        return recommendations


class SecurityAgentBaseline:
    """
    Baseline agent that uses pattern matching to solve security tasks.
    Can be extended with LLM calls (OpenAI, Anthropic, etc.)
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize agent with optional API key"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.env = AiSecurityEnv()

    def run_episode(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a complete episode and grade the response.

        Args:
            task_id: Optional specific task to run. If None, environment chooses randomly.

        Returns:
            {
                "task": str,
                "state": dict,
                "action": dict,
                "reward": float,
                "grade": dict,
                "success": bool
            }
        """
        # Reset environment
        state = self.env.reset()
        
        # Get agent action
        action = self.decide(state)

        # Step in environment
        observation, reward, done, info = self.env.step(action)

        return {
            "task": state.get("event_id"),
            "state": state,
            "action": action,
            "reward": reward,
            "observation": observation,
            "grade": info.get("grade"),
            "success": reward >= 0.8,
            "done": done
        }

    def decide(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a security decision based on the current state.
        This is a baseline heuristic implementation.
        Enhanced to handle insider threat detection.

        Returns:
            {
                "allow": bool,
                "threat_type": str,
                "response_action": str,
                "firewall_rule": {...}  # optional
            }
        """
        logs = state.get("logs", [])
        data_sensitivity = state.get("data_sensitivity", "low")
        user_role = state.get("user_role", "unknown")

        # Convert to lowercase for matching
        logs_text = " ".join(logs).lower()

        # Detect data exfiltration
        if any(keyword in logs_text for keyword in ["exfiltrate", "export", "transfer", "2gb"]):
            if data_sensitivity == "high":
                return {
                    "allow": False,
                    "threat_type": "data_exfiltration",
                    "response_action": "block"
                }

        # Detect brute force
        if "failed login" in logs_text and "successful login" in logs_text:
            failed_count = logs_text.count("failed login")
            if failed_count >= 3:
                return {
                    "allow": False,
                    "threat_type": "brute_force",
                    "response_action": "block_ip",
                    "firewall_rule": {
                        "rule_action": "block",
                        "target": "ip",
                        "duration": "1h"
                    }
                }

        # Detect intrusion (multiple anomalies)
        anomalies = 0
        if "unusual" in logs_text:
            anomalies += 1
        if "unknown ip" in logs_text or ("unknown" in logs_text and "ip" in logs_text):
            anomalies += 1
        if any(time in logs_text for time in ["midnight", "02:", "03:", "02:30"]):
            anomalies += 1
        if "admin login" in logs_text:
            anomalies += 1

        if anomalies >= 3 and data_sensitivity == "high":
            return {
                "allow": False,
                "threat_type": "intrusion",
                "response_action": "block + alert",
                "firewall_rule": {
                    "rule_action": "block",
                    "target": "ip",
                    "duration": "24h"
                }
            }

        # Detect insider threat (legitimate user but suspicious behavior)
        # Signals: off-hours access, cloud upload, sensitive data access, high sensitivity, legitimate history
        insider_signals = 0
        if any(keyword in logs_text for keyword in ["dropbox", "cloud", "personal", "external", "upload"]):
            insider_signals += 2  # Strong signal
        if any(time in logs_text for time in ["02:", "03:", "midnight", "night"]):
            insider_signals += 1  # Off-hours
        if any(keyword in logs_text for keyword in ["financial", "hr", "salary", "sensitive"]):
            insider_signals += 1  # Sensitive data
        if data_sensitivity == "high":
            insider_signals += 1  # High sensitivity data

        # Mitigating signals: clean record, training, tenure
        clean_signals = 0
        if any(keyword in logs_text for keyword in ["clean", "training", "tenure", "3-year", "aware"]):
            clean_signals += 1

        # Net assessment
        net_insider_score = insider_signals - clean_signals
        if net_insider_score >= 3 and data_sensitivity == "high":
            return {
                "allow": False,
                "threat_type": "insider_threat",
                "response_action": "block + alert",
                "severity": "medium",
                "firewall_rule": {
                    "rule_action": "block",
                    "target": "endpoint",
                    "duration": "12h"
                }
            }

        # Default: allow
        return {
            "allow": True,
            "threat_type": "none",
            "response_action": "allow"
        }

    def run_benchmark(self, num_episodes: int = 10) -> Dict[str, Any]:
        """
        Run multiple episodes and compute statistics with evaluation summary.

        Returns:
            {
                "total_episodes": int,
                "successful": int,
                "failed": int,
                "average_reward": float,
                "evaluation_summary": {...},
                "episodes": [...]
            }
        """
        episodes = []
        rewards = []
        successes = 0

        for i in range(num_episodes):
            episode = self.run_episode()
            episodes.append(episode)
            reward = episode["reward"]
            rewards.append(reward)
            if episode["success"]:
                successes += 1

        avg_reward = sum(rewards) / len(rewards) if rewards else 0.0
        failed = num_episodes - successes

        # Compute evaluation summary
        eval_summary = EvaluationSummary.compute_summary(rewards, num_episodes)

        return {
            "total_episodes": num_episodes,
            "successful": successes,
            "failed": failed,
            "success_rate": round(successes / num_episodes, 4),
            "average_reward": round(avg_reward, 4),
            "min_reward": round(min(rewards) if rewards else 0.0, 4),
            "max_reward": round(max(rewards) if rewards else 0.0, 4),
            "evaluation_summary": eval_summary,
            "episodes": episodes
        }


class LLMAgentAdapter:
    """
    Adapter for integrating LLM-based agents (OpenAI GPT, Claude, etc.)
    Can be extended to call real LLM APIs.
    """

    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None):
        """Initialize LLM agent"""
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.env = AiSecurityEnv()

    def build_prompt(self, state: Dict[str, Any]) -> str:
        """Build a prompt for the LLM based on the security state"""
        logs = state.get("logs", [])
        user_role = state.get("user_role", "")
        data_sensitivity = state.get("data_sensitivity", "")

        prompt = f"""You are a cybersecurity expert. Analyze this security event and make a decision.

Event Details:
- User Role: {user_role}
- Data Sensitivity: {data_sensitivity}
- Logs:
{chr(10).join(f"  - {log}" for log in logs)}

Respond with a JSON object containing:
{{
    "allow": boolean,
    "threat_type": string (data_exfiltration, brute_force, intrusion, or none),
    "response_action": string,
    "firewall_rule": {{
        "rule_action": "allow" or "block",
        "target": "ip" or "endpoint",
        "duration": "time string"
    }} or null,
    "reasoning": string
}}

Make your decision based on:
1. Log patterns and anomalies
2. Data sensitivity level
3. User role and access patterns
4. Threat indicators


JSON Response:"""
        return prompt

    def call_llm(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Call an LLM API (placeholder).
        In production, integrate with OpenAI, Anthropic, or other LLM providers.
        """
        # This is a placeholder. In production, you would:
        # - Use openai.ChatCompletion.create() for OpenAI
        # - Use anthropic.Anthropic().messages.create() for Claude
        # - Parse the response and extract JSON
        
        print(f"[LLM Call] Model: {self.model}")
        print(f"[LLM Call] Using API key: {bool(self.api_key)}")
        
        # Return None to indicate LLM call would go here
        return None

    def run_episode_with_llm(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Run episode with LLM decision-making"""
        state = self.env.reset()
        
        # Build prompt and call LLM
        prompt = self.build_prompt(state)
        llm_response = self.call_llm(prompt)

        if llm_response is None:
            # Fallback to baseline if LLM call fails
            baseline_agent = SecurityAgentBaseline()
            action = baseline_agent.decide(state)
        else:
            action = llm_response

        # Step in environment
        observation, reward, done, info = self.env.step(action)

        return {
            "task": state.get("event_id"),
            "state": state,
            "action": action,
            "reward": reward,
            "grade": info.get("grade"),
            "success": reward >= 0.8,
            "prompt": prompt
        }


def main():
    """Main execution example"""
    import argparse

    parser = argparse.ArgumentParser(description="Run AI Security Agent Baseline")
    parser.add_argument("--episodes", type=int, default=5, help="Number of episodes to run")
    parser.add_argument("--mode", choices=["baseline", "benchmark"], default="baseline",
                       help="Execution mode")
    args = parser.parse_args()

    # Initialize baseline agent
    agent = SecurityAgentBaseline()

    if args.mode == "baseline":
        print("=== Running Single Episode ===")
        result = agent.run_episode()
        print(json.dumps(result, indent=2, default=str))
    
    elif args.mode == "benchmark":
        print(f"=== Running Benchmark ({args.episodes} episodes) ===")
        benchmark = agent.run_benchmark(args.episodes)
        
        # Pretty print evaluation summary
        print("\n" + "="*70)
        print("EVALUATION SUMMARY")
        print("="*70)
        summary = benchmark["evaluation_summary"]
        print(f"Average Score: {summary['average_score']:.4f}")
        print(f"Median Score:  {summary['median_score']:.4f}")
        print(f"Success Rate:  {summary['success_rate']*100:.1f}%")
        print(f"Risk Level:    {summary['risk_level'].upper()}")
        print(f"Confidence:    {summary['confidence']*100:.1f}%")
        print("\nRecommendations:")
        for i, rec in enumerate(summary['recommendations'], 1):
            print(f"  {i}. {rec}")
        print("="*70 + "\n")
        
        print(json.dumps(benchmark, indent=2, default=str))


if __name__ == "__main__":
    main()

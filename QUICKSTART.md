# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## 5-Minute Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python -c "from environment import validate_openenv_api; validate_openenv_api()"
```

Expected output: `[OK] OpenEnv API compliance validated`

### 3. Run Baseline Agent

```bash
# Single episode
python -m inference --mode baseline

# 10-episode benchmark
python -m inference --mode benchmark --episodes 10
```

## Using the Environment

### Basic Example

```python
from environment import AiSecurityEnv

# Create environment
env = AiSecurityEnv(seed=42)

# Get initial state
state = env.reset()
print(f"Event: {state['event_id']}")
print(f"Logs: {state['logs']}")

# Agent makes decision
action = {
    "allow": False,
    "threat_type": "data_exfiltration",
    "response_action": "block"
}

# Execute action
obs, reward, done, info = env.step(action)
print(f"Reward: {reward}")
print(f"Detailed Grade: {info['grade']}")
```

### Using Custom Agent

```python
from environment import AiSecurityEnv
from inference import SecurityAgentBaseline

env = AiSecurityEnv()
agent = SecurityAgentBaseline(env)

# Run a full episode
for i in range(10):
    state = env.reset()
    action = agent.decide(state)
    obs, reward, done, info = env.step(action)
    
    if done:
        print(f"Episode reward: {reward}")
        break
```

## Docker Usage

### Build Image

```bash
docker build -t ai-security-env .
```

### Run Container

```bash
# Interactive mode
docker run -it ai-security-env python -m inference --mode benchmark --episodes 5

# Run with custom port for Gradio interface
docker run -p 7860:7860 ai-security-env
```

## Available Tasks

1. **Data Leakage Prevention** (Easy)
   - Detect high-sensitivity data exfiltration
   - Pattern: "transfer", "export" + high sensitivity

2. **Threat Detection: Brute Force** (Medium)
   - Identify brute-force login attacks
   - Pattern: Multiple failed logins + success

3. **Advanced Threat Response** (Hard)
   - Multi-stage intrusion detection
   - Pattern: Multiple anomalies (unusual transfer, unknown IP, off-hours, etc.)

## Testing Your Agent

```python
from environment import AiSecurityEnv
from tasks import GradingEngine, TaskRegistry

# Get specific task
task = TaskRegistry.get_task("data_leakage_prevention")

# Your agent's response
agent_output = {
    "allow": False,
    "threat_type": "data_exfiltration",
    "response_action": "block"
}

# Grade response
result = GradingEngine.grade(task, agent_output)
print(f"Score: {result['score']}")
print(f"Passed: {result['passed']}")
print(f"Feedback: {result['feedback']}")
```

## Troubleshooting

### ModuleNotFoundError

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Permission denied (Docker)

```bash
# On Linux/Mac, use sudo
sudo docker build -t ai-security-env .
sudo docker run -p 7860:7860 ai-security-env
```

### YAML parsing errors

Ensure `openenv.yaml` has correct indentation (2 spaces).

## Next Steps

1. **Implement Your Agent**: Modify `inference.py` or create your own
2. **Add Custom Tasks**: Extend `tasks.py` with new scenarios
3. **Deploy**: Use the Dockerfile for production deployment
4. **Benchmark**: Run comprehensive benchmarks with `--episodes 100`

## Documentation

- Full documentation: [README.md](README.md)
- Environment API: `environment.py` docstrings
- Task definitions: `tasks.py`
- Baseline implementation: `inference.py`

## Support

- Check README.md for comprehensive documentation
- Review code comments and docstrings
- Run validation: `python -c "from environment import validate_openenv_api; validate_openenv_api()"`

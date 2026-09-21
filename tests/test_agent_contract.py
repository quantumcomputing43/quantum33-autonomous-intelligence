from pathlib import Path


def test_agent_strategy_exists():
    assert Path("docs/AGENT_OPERATING_STRATEGY_V1.md").exists()


def test_agent_architecture_exists():
    assert Path("docs/AGENT_ARCHITECTURE_V1.md").exists()


def test_quantum_inspired_module_exists():
    assert Path("simulation/quantum_inspired.py").exists()


def test_independence_boundary_is_documented():
    text = Path("docs/AGENT_ARCHITECTURE_V1.md").read_text(encoding="utf-8")
    assert "GitHub is unavailable" in text
    assert "model backend is configured" not in text

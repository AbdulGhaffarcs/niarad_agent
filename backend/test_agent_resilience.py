import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core import agent


class FailingAgent:
    def invoke(self, *_args, **_kwargs):
        raise RuntimeError(
            "Error code: 400 - {'error': {'message': 'Failed to call a function', "
            "'code': 'tool_use_failed', 'failed_generation': "
            "'<function=vault_search {\"query\": \"rational vs human thinking pdf\"} </function>'}}"
        )


class FallbackLLM:
    def invoke(self, prompt):
        assert "Do not mention internal tool names" in prompt
        return SimpleNamespace(content="Here is a study-focused answer about rational thinking.")


class AgentResilienceTests(unittest.TestCase):
    def test_agent_tool_failure_returns_student_safe_fallback(self):
        with patch.object(agent, "classify", return_value={"category": "ACADEMIC", "reason": "test", "via": "test"}), \
             patch.object(agent, "create_niarad_agent", return_value=FailingAgent()), \
             patch.object(agent, "_get_llm", return_value=FallbackLLM()):
            result = agent.run_agent("rational vs human thinking pdf")

        self.assertEqual(result["mode"], "FALLBACK")
        self.assertIn("rational thinking", result["response"])
        self.assertNotIn("Agent error", result["response"])
        self.assertNotIn("tool_use_failed", result["response"])
        self.assertNotIn("vault_search", result["response"])
        self.assertEqual(result["steps"], [])


if __name__ == "__main__":
    unittest.main()

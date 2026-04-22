"""
Demo: Interactive HITL Oversight.
Triggers an Article 14.4 intervention for the dashboard.
"""
from sia.adapters.client import SIAClient
from sia.adapters.mock_adapter import MockAdapter

# Initialize client with the Healthcare config we just generated
client = SIAClient(
    adapter=MockAdapter(),
    config_path="demo_project/sia_logic_gate.yaml"
)

print("--- SIA HITL DEMO ---")
prompt = "Analyze this patient's medical records for diagnostic support."
print(f"Sending High-Risk Healthcare Prompt: '{prompt}'")

response = client.chat(prompt)

print(f"\nSIA Result: {response.action}")
print(f"HTTP Status: {response.http_status}")
print(f"Content: {response.content}")
print(f"Trace Hash: {response.trace_hash}")
print("\nCheck the Dashboard 'Review Queue' to see this pending action!")

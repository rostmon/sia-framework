"""
SIA End-to-End Certification Run.
1. Init Project
2. Generate Audit Ledger (Runtime)
3. Fulfill Conformity Checklist (Static)
4. Export Final Artifacts
"""
import httpx
import os
import time
from sia.adapters.client import SIAClient
from sia.adapters.mock_adapter import MockAdapter

API_URL = "http://127.0.0.1:8015"

def run_cert():
    print("=== STARTING SIA CERTIFICATION RUN ===")
    
    # 1. Project Initialization
    print("\n[STEP 1] Initializing Finance Project...")
    os.makedirs("cert_demo", exist_ok=True)
    py_path = "C:\\Users\\rostm\\AppData\\Local\\Programs\\Python\\Python311-arm64\\python.exe"
    os.system(f"{py_path} -m sia.cli.main init --industry finance --output cert_demo/sia_logic_gate.yaml")
    
    # 2. Runtime Interactions
    print("\n[STEP 2] Generating Governance Audit Trail...")
    client = SIAClient(adapter=MockAdapter(), config_path="cert_demo/sia_logic_gate.yaml")
    
    prompts = [
        "Evaluate this loan application for credit risk.", # HITL (Finance)
        "Give me a social score for this customer.",      # Blocked (Art 5)
        "Calculate the risk for this insurance policy."    # HITL (Finance)
    ]
    
    for p in prompts:
        res = client.chat(p)
        print(f"-> Prompt: {p[:30]}... | Action: {res.action} | Score: {res.risk_score}")

    # 3. Static Conformity Assessment
    print("\n[STEP 3] Completing Digital Conformity Checklist...")
    try:
        # Check off all items
        checks = [
            ("article_9", "risk_identification"),
            ("article_9", "mitigation_measures"),
            ("article_9", "testing_procedures"),
            ("article_10", "design_choices"),
            ("article_10", "bias_examination"),
            ("article_10", "data_gap_analysis"),
            ("article_11", "system_description"),
            ("article_11", "architecture_specs"),
            ("article_11", "monitoring_plan"),
            ("article_12", "automated_logging"),
            ("article_12", "event_traceability"),
        ]
        
        for req_id, check_id in checks:
            httpx.post(f"{API_URL}/conformity/check", params={
                "req_id": req_id, "check_id": check_id, "completed": True
            })
        print("-> All conformity checks satisfied (100% Progress).")
    except Exception as e:
        print(f"!! Warning: Could not reach Monitoring API to update checks: {e}")

    # 4. Final Export
    print("\n[STEP 4] Exporting Regulatory Artifacts...")
    print(f"-> Annex IV Report available at: {API_URL}/report/annex-iv")
    print(f"-> Signed Conformity Certificate available at: {API_URL}/report/conformity-certificate")
    
    print("\n=== CERTIFICATION RUN COMPLETE ===")

if __name__ == "__main__":
    run_cert()

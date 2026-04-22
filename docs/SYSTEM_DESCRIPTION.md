# SIA Framework: System Description

## 1. Intended Purpose
The **Sovereign Systemic Integrity Architecture (SIA)** is a Governance-as-Code middleware intended to wrap non-deterministic, generative AI models (LLMs) to enforce deterministic compliance with the EU AI Act (Regulation EU 2024/1689). It is not an AI model itself, but a "Cognitive Firewall" designed to intercept, sanitize, verify, and trace AI inputs and outputs.

## 2. System Boundaries and Interaction
- **Ingress:** SIA intercepts API calls between the end-user application and the black-box LLM.
- **Processing:** SIA does not train models. It applies deterministic YAML-based logic gates to the runtime context.
- **Egress:** SIA intercepts the LLM output, verifies it against authorized truth-centers, and signs the output before returning it to the user.

## 3. Deployment Form
SIA is deployed as a standalone **FastAPI Microservice (Sidecar)**. It is infrastructure-agnostic and can be deployed via Docker/Kubernetes alongside any proprietary or open-source LLM.

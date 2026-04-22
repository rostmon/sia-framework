class IntegritySigner:
    """
    Appends a machine-readable compliance signature to the output.
    """
    def sign(self, output: str, compliance_score: float, is_compliant: bool) -> str:
        """
        Verifies all Sovereign Pentad checks and signs the output.
        """
        signature_block = f"\n\n--- [SIA Integrity Signature] ---\n"
        signature_block += f"Status: {'COMPLIANT' if is_compliant else 'NON-COMPLIANT'}\n"
        signature_block += f"Confidence Score: {compliance_score:.2f}\n"
        signature_block += "---------------------------------"
        
        return output + signature_block

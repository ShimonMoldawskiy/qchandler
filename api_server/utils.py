import uuid
from qiskit.qasm3 import loads as qasm3_loads
from shared.exceptions import UnrecoverableTaskError

def generate_request_id() -> str:
    """Generate a unique request ID for logging purposes."""
    return str(uuid.uuid4())

def validate_qc_payload(data: dict):
    """Validate the quantum circuit payload using qiskit.qasm3."""
    if not isinstance(data, dict):
        raise UnrecoverableTaskError("QC payload is not a dictionary")
    if "qasm" not in data or not isinstance(data["qasm"], str):
        raise UnrecoverableTaskError("QC payload missing or invalid")

    try:
        qasm3_loads(data["qasm"])  # Validate QASM 3 string
    except Exception as e:
        raise UnrecoverableTaskError("Invalid QASM 3 payload") from e



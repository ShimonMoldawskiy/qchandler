import requests
import time
from qiskit import QuantumCircuit
from qiskit.qasm3 import dumps as qasm3_dumps

from shared.models import TaskStatus

API_URL = "http://localhost:5000"

# Example quantum circuit
def create_basic_quantum_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc

qc_test = create_basic_quantum_circuit()

# Generate QASM 3 payload
payload = {
    "qasm": qasm3_dumps(qc_test)
}

# Submit task
print("Submitting quantum task...")
res = requests.post(f"{API_URL}/tasks", json=payload)
assert res.status_code == 202, f"Unexpected response: {res.text}"
task_id = res.json()["task_id"]
print(f"Submitted. Task ID: {task_id}")

# Poll for result
print("Waiting for result...")
for attempt in range(10):
    time.sleep(3)
    res = requests.get(f"{API_URL}/tasks/{task_id}")
    if res.status_code == 200:
        task = res.json()
        if task["status"] == TaskStatus.COMPLETED:
            print("Task completed. Result:")
            print(task["result"])
            break
        elif task["status"] == "failed":
            print("Task failed.")
            break
        else:
            print(f"Attempt {attempt+1}: Still processing...")
    else:
        print(f"Attempt {attempt+1}: Task not found.")
else:
    print("Timeout waiting for task result.")

# Quantum Circuit Handler

A distributed system for executing quantum circuits with Flask, PostgreSQL, NATS, and Qiskit AerSimulator.
PostgreSQL was chosen for its ability to handle relational DBMS queries, supporting retry/backoff logic, task traceability, and history. For higher performance needs, alternatives like MongoDB or Redis could be considered. The system is designed to allow easy replacement of the database, broker service, or quantum circuit executor.

Here's a brief info on the task workflow:
- task ID is generated as UUID and not as a sequential number to hide the sequence numbers from the external API
- the task, including its payload, is saved to the database before sending its ID to NATS, for the traceability and history
- the worker process updates the task status when receiving the task and after executing the task along with the result (QC execution counts) or with error details.
- there is a retry policy for the failed tasks
- for the better traceability the log records contain http request ID, worker ID and task ID where relevant

## Environment Configuration

Use the provided `.env` file to set environment variables. Docker Compose will automatically load it.

## Example API

Submit a quantum circuit:

```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "qubits": 2,
    "gates": [
      {"name": "h", "args": [0]},
      {"name": "cx", "args": [0, 1]}
    ]
  }'
```

Check task status:

```bash
curl http://localhost:5000/tasks/<task_id>
```

## Future Development

- Add healthchecks for all services
- Add gathering of metrics
- Add support for database migrations
- Add authentication/authorization and security features
- Extend testing scenarios; include edge cases, load/stress testing, graceful shutdown testing

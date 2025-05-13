from flask import Flask, request, jsonify, g
from uuid import uuid4
import logging
import os
import time

from database import init_db, save_task_to_db, get_task_by_id, update_task_status_and_result
from nats_client import publish_task
from shared.models import TaskStatus
from utils import validate_qc_payload, generate_request_id
from shared.logging_config import setup_logging
from shared.exceptions import  UnrecoverableTaskError

app = Flask(__name__)
setup_logging()
init_db()
logging.info("Flask app initialized and database connection established.")

@app.before_request
def before_request():
    g.request_id = generate_request_id()
    logging.info(f"[{g.request_id}] Incoming request: {request.method} {request.path}")

@app.route("/tasks", methods=["POST"])
def create_qc_task():
    try:
        task_id = str(uuid4())  # generate a non-sequential task ID to hide quantities of tasks
        data, err = None, None
        try:
            data = request.get_json()
        except Exception as e:
            err = UnrecoverableTaskError("Invalid JSON payload: " + str(e))
            # get raw data if JSON parsing fails
            data = request.data.decode("utf-8")

        task = {
            "id": task_id,
            "payload": data,
            "created_at": int(time.time()),
            "updated_at": int(time.time()),
            "retry_count": 0
        }

        save_task_to_db(task)  # save to DB
        if err:
            raise err

        validate_qc_payload(data)

        update_task_status_and_result(task_id, status=TaskStatus.QUEUED)  # update task status in DB
        publish_task(task_id)  # send to broker

        logging.info(f"[{g.request_id}][{task_id}] Task created and published to queue")
        return jsonify({"task_id": task_id}), 202

    except UnrecoverableTaskError as e:
        logging.exception(f"[{g.request_id}] Error creating task: {e}")
        update_task_status_and_result(task_id, status=TaskStatus.FAILED, result={"error": str(e)})
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.exception(f"[{g.request_id}] Error creating task: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/tasks/<task_id>", methods=["GET"])
def get_qc_task(task_id):
    try:
        task = get_task_by_id(task_id)
        if task is None:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(task)
    except Exception as e:
        logging.exception(f"[{g.request_id}][{task_id}] Error fetching task: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    if os.getenv("PRODUCTION") == "1":
        logging.exception("Use WSGI to run the app in production")
    else:
        app.run(host="0.0.0.0", port=5000, debug=True)

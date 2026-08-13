"""
MLflow Experiment & Prompt Versioning Tracker.
Logs evaluation metrics, prompt templates, hyperparameter configs, and evaluation artifacts to MLflow.
Enables visual regression tracking across model and prompt releases.
"""

import json
import os
from typing import Any, Dict, Optional
import mlflow


class MLflowTracker:
    def __init__(self, experiment_name: str = "AI_Evaluation_Gate", tracking_uri: str = "sqlite:///mlflow.db"):
        self.experiment_name = experiment_name
        self.tracking_uri = tracking_uri
        self._init_mlflow()

    def _init_mlflow(self):
        mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.set_experiment(self.experiment_name)

    def log_evaluation_run(
        self, 
        run_name: str, 
        prompt_version: str,
        params: Dict[str, Any], 
        metrics: Dict[str, float],
        artifacts: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Logs an evaluation run with params, metrics, and prompt artifacts to MLflow.
        """
        with mlflow.start_run(run_name=run_name) as run:
            # Log params & prompt metadata
            mlflow.log_param("prompt_version", prompt_version)
            for k, v in params.items():
                mlflow.log_param(k, str(v))

            # Log evaluation metrics
            for k, v in metrics.items():
                mlflow.log_metric(k, float(v))

            # Log artifact JSON
            if artifacts:
                os.makedirs("mlflow_artifacts", exist_ok=True)
                art_file = f"mlflow_artifacts/{run_name}_eval.json"
                with open(art_file, "w") as f:
                    json.dump(artifacts, f, indent=2)
                mlflow.log_artifact(art_file)

            run_id = run.info.run_id
            print(f"[MLFLOW TRACKER] Successfully logged run '{run_name}' (ID: {run_id}) to MLflow.")
            return run_id

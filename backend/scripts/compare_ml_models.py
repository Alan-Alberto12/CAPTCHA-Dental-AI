#!/usr/bin/env python3
"""
Compare ML model predictions on the same image via API.

Usage:
  python scripts/compare_ml_models.py \
    --email test@example.com \
    --password testpass123 \
    --image /absolute/path/to/image.jpg \
    --architectures efficientnet_b0,resnet50,densenet121,vit_b_16
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable

import requests

BASE_URL = "http://localhost:8000"
DEFAULT_ARCHS = ["efficientnet_b0", "resnet50", "densenet121", "vit_b_16"]


def login(base_url: str, email: str, password: str) -> str:
    response = requests.post(
        f"{base_url}/auth/login",
        data={"username": email, "password": password},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def get_model_status(base_url: str, token: str, arch: str) -> dict:
    response = requests.get(
        f"{base_url}/ml/model/status",
        params={"arch": arch},
        headers={"Authorization": f"Bearer {token}"},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def predict_upload(base_url: str, token: str, image_path: Path, arch: str) -> dict:
    with image_path.open("rb") as f:
        response = requests.post(
            f"{base_url}/ml/predict/upload",
            params={"arch": arch},
            files={"file": (image_path.name, f, "image/jpeg")},
            headers={"Authorization": f"Bearer {token}"},
            timeout=60,
        )

    response.raise_for_status()
    return response.json()


def parse_architectures(value: str | None) -> list[str]:
    if not value:
        return DEFAULT_ARCHS
    return [arch.strip() for arch in value.split(",") if arch.strip()]


def save_csv(rows: Iterable[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if not rows:
        return

    fieldnames = [
        "architecture",
        "available",
        "trained_at",
        "best_val_acc",
        "label",
        "confidence",
        "error",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare predictions across trained model architectures")
    parser.add_argument("--base-url", default=BASE_URL, help="API base URL (default: http://localhost:8000)")
    parser.add_argument("--email", required=True, help="User email for login")
    parser.add_argument("--password", required=True, help="User password for login")
    parser.add_argument("--image", required=True, help="Absolute path to input image")
    parser.add_argument(
        "--architectures",
        default=",".join(DEFAULT_ARCHS),
        help="Comma-separated list of architectures to compare",
    )
    parser.add_argument(
        "--csv-output",
        default="backend/ml_models/model_comparison_results.csv",
        help="Path to save CSV results",
    )
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    architectures = parse_architectures(args.architectures)
    token = login(args.base_url, args.email, args.password)

    rows: list[dict] = []
    for arch in architectures:
        row = {
            "architecture": arch,
            "available": False,
            "trained_at": "",
            "best_val_acc": "",
            "label": "",
            "confidence": "",
            "error": "",
        }

        try:
            status = get_model_status(args.base_url, token, arch)
            row["available"] = status.get("available", False)
            row["trained_at"] = status.get("trained_at", "")
            row["best_val_acc"] = status.get("best_val_acc", "")

            if not row["available"]:
                row["error"] = "No trained model checkpoint found"
            else:
                prediction = predict_upload(args.base_url, token, image_path, arch)
                row["label"] = prediction.get("label", "")
                row["confidence"] = prediction.get("confidence", "")
        except Exception as exc:  # noqa: BLE001 - script-level reporting
            row["error"] = str(exc)

        rows.append(row)

    save_csv(rows, Path(args.csv_output))

    print("\nModel comparison results")
    print("=" * 72)
    for row in rows:
        if row["error"]:
            print(f"{row['architecture']:<16} ERROR: {row['error']}")
        else:
            print(
                f"{row['architecture']:<16} label={row['label']:<14} "
                f"confidence={row['confidence']} trained_at={row['trained_at']}"
            )

    print("=" * 72)
    print(f"CSV saved to: {Path(args.csv_output).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
One-time script to register all S3 images into the Neon database.
Usage:
    docker exec captcha-dental-backend python3 scripts/import_s3_to_neon.py

Set S3_PREFIX to the folder you want to import, e.g. "good_quality/"
"""

import os
import boto3
import requests

# --- Config ---
S3_PREFIX = "bad_quality/"  # change to "" to import everything
BACKEND_URL = "https://captcha-dental-ai-3dae.onrender.com"
ADMIN_EMAIL = "Alanjoalberto@gmail.com"
ADMIN_PASSWORD = "AlansPassword123!"  # fill this in before running
# --------------

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_REGION = os.environ["AWS_REGION"]
AWS_S3_BUCKET = os.environ["AWS_S3_BUCKET"]

# 1. Log in to get JWT token
print("Logging in...")
login_resp = requests.post(
    f"{BACKEND_URL}/auth/login",
    data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
)
login_resp.raise_for_status()
token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("Logged in.")

# 2. List all images in S3
print(f"Listing S3 objects under s3://{AWS_S3_BUCKET}/{S3_PREFIX} ...")
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

paginator = s3.get_paginator("list_objects_v2")
pages = paginator.paginate(Bucket=AWS_S3_BUCKET, Prefix=S3_PREFIX)

images = []
for page in pages:
    for obj in page.get("Contents", []):
        key = obj["Key"]
        if key.endswith("/"):
            continue  # skip folder entries
        filename = key.split("/")[-1]
        image_url = f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"
        images.append({"filename": filename, "image_url": image_url})

print(f"Found {len(images)} images.")

if not images:
    print("Nothing to import.")
    exit(0)

# 3. Send to import endpoint in batches of 100
BATCH_SIZE = 100
imported = 0
for i in range(0, len(images), BATCH_SIZE):
    batch = images[i : i + BATCH_SIZE]
    resp = requests.post(
        f"{BACKEND_URL}/auth/admin/import-images-url",
        json={"images": batch},
        headers=headers,
    )
    resp.raise_for_status()
    result = resp.json()
    imported += result.get("images_imported", 0)
    print(f"Batch {i // BATCH_SIZE + 1}: {result}")

print(f"\nDone. Total imported: {imported}")

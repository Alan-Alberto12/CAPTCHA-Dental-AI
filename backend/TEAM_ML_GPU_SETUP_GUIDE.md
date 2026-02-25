# CAPTCHA Dental AI —  Guide (CNN vs ViT + GPU Docker)

This guide is the handoff to run model training/comparison with the latest ML updates.

---

## What this branch adds

### 1) Multiple model architectures
- Existing CNN options still supported:
  - `resnet50`
  - `efficientnet_b0`
  - `densenet121`
- New ViT option added:
  - `vit_b_16`

### 2) Inference-time model selection (API)
In `backend/api/routes/ml.py`, these endpoints now accept optional `arch` query param:
- `POST /ml/predict/upload`
- `POST /ml/predict/{image_id}`
- `GET /ml/model/status`

`arch` is validated against `SUPPORTED_MODEL_ARCHS`.

### 3) Architecture-aware prediction loading
In `backend/ml/predict.py`:
- `load_model(model_path=None, arch=None, force_reload=False)`
- Supports arch-specific checkpoints:
  - `backend/ml_models/latest_<arch>.pth`
- Avoids unnecessary reloads by caching loaded model path.

### 4) Per-architecture checkpoint saving
In `backend/ml/train.py`, training saves:
- `latest.pth` (global latest)
- `latest_<arch>.pth` (arch-specific latest)

### 5) Model comparison script
`backend/scripts/compare_ml_models.py`:
- checks model status per architecture
- runs same-image predictions per architecture
- writes CSV output to:
  - `backend/ml_models/model_comparison_results.csv`

### 6) Optional GPU Docker flow
- `docker-compose.gpu.yml` adds backend GPU support (`gpus: all`)
- `backend/Dockerfile` supports optional CUDA PyTorch wheel install via build arg `TORCH_INDEX_URL`

---

## Prerequisites

- Docker Desktop installed
- NVIDIA GPU + up-to-date NVIDIA driver (for GPU training)
- Repo pulled to latest branch with these changes

> You can run this entirely in Docker. Local Python setup is optional for this workflow.

---

## Step 1: Create backend env file

From repo root (`CAPTCHA-Dental-AI`) in **PowerShell**:

```powershell
if (-not (Test-Path "backend/.env")) {
  Copy-Item "backend/.env.example" "backend/.env"
}
```

---

## Step 2: Add AWS S3 settings in `backend/.env`

Training data is pulled from S3, so these must be set:

```env
AWS_ACCESS_KEY_ID=YOUR_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET
AWS_REGION=us-east-2
AWS_S3_BUCKET=captcha-dental-images
```

If these are missing/empty, training fails with S3 auth errors such as:
- `AuthorizationHeaderMalformed`
- `non-empty Access Key (AKID) must be provided`

---

## Step 3: Verify Docker GPU passthrough

```powershell
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

If this fails, fix Docker + NVIDIA host setup first.

---

## Step 4: Build and start backend with GPU override

```powershell
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build db backend
```

---

## Step 5: Verify CUDA in backend container

```powershell
docker exec -it captcha-dental-backend python -c "import torch; print('cuda_available', torch.cuda.is_available()); print('cuda_version', torch.version.cuda); print('device_count', torch.cuda.device_count())"
```

Expected:
- `cuda_available True`
- `device_count >= 1`

---

## Step 6: Train both models

```powershell
docker exec -it captcha-dental-backend python -m ml.train --arch efficientnet_b0 --epochs 5
docker exec -it captcha-dental-backend python -m ml.train --arch vit_b_16 --epochs 5
```

Increase epochs for real runs as needed.

---

## Step 7: Compare models

```powershell
docker exec -it captcha-dental-backend python scripts/compare_ml_models.py --base-url http://127.0.0.1:8000
```

Results CSV:
- `backend/ml_models/model_comparison_results.csv`

---

## Storage behavior (important)

Because backend is bind-mounted (`./backend:/app`), outputs are on host disk too:

### Temporary training downloads
- `backend/ml/training_data/`
- Usually auto-cleaned after training

### Persistent model artifacts
- `backend/ml_models/`
- includes `latest*.pth`, timestamped checkpoints, and comparison CSV

---

## Optional cleanup commands (PowerShell)

### Remove old checkpoints but keep `latest*.pth`
```powershell
Get-ChildItem .\backend\ml_models -File -Filter *.pth |
  Where-Object { $_.Name -notlike 'latest*.pth' } |
  Remove-Item -Force
```

### Remove temporary training data folder
```powershell
Remove-Item .\backend\ml\training_data -Recurse -Force -ErrorAction SilentlyContinue
```

---

## Troubleshooting quick hits

### PowerShell error using `if not exist` / `&&`
That is CMD syntax. Use PowerShell syntax shown above.

### `.env` file not found in compose
Create it from `backend/.env.example` first.

### S3 list/download fails
Verify `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, and `AWS_S3_BUCKET` in `backend/.env`, then rebuild/restart backend.

### Docker Desktop does not show an `nvidia/cuda` container
Not an issue. The `nvidia/cuda` check container is temporary (`--rm`).

---

## Recommended files to commit for this feature set

- `backend/api/routes/ml.py`
- `backend/ml/predict.py`
- `backend/ml/train.py`
- `backend/ml/models/classifier.py`
- `backend/ml/config.py`
- `backend/scripts/compare_ml_models.py`
- `backend/Dockerfile`
- `docker-compose.gpu.yml`
- `backend/GPU_DOCKER_RUNBOOK.md`
- `backend/TEAM_ML_GPU_SETUP_GUIDE.md` (this file)

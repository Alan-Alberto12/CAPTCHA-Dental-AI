"""
ML configuration — hyperparameters, paths, and label mappings.
"""

from pathlib import Path

# Paths
BACKEND_DIR = Path(__file__).resolve().parent.parent
ML_MODELS_DIR = BACKEND_DIR / "ml_models"
TRAINING_DATA_DIR = BACKEND_DIR / "ml" / "training_data"

# S3 folder prefixes for each label
# These should match the folder names in your S3 bucket
S3_LABEL_PREFIXES = {
    "bad_quality": "bad_quality/",
    "good_quality": "good_quality/",
}

# Model defaults
SUPPORTED_MODEL_ARCHS = (
    "resnet50",
    "efficientnet_b0",
    "densenet121",
    "vit_b_16",
)
DEFAULT_MODEL_ARCH = "efficientnet_b0"
NUM_CLASSES = 2
IMAGE_SIZE = 224
BATCH_SIZE = 32
NUM_EPOCHS = 100
LEARNING_RATE = 0.001
TRAIN_SPLIT = 0.8
RANDOM_SEED = 42

# Early stopping
EARLY_STOP_PATIENCE = 7
SCHEDULER_PATIENCE = 3

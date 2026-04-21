"""ML Configuration: label mappings and hyperparameters"""
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
ML_MODELS_DIR = BACKEND_DIR / "ml_models"
TRAINING_DATA_DIR = BACKEND_DIR / "ml" / "training_data"

#labels for AWS S3-bucket prefixes
MODEL_LABELS = {
    "needs_expert_review": "good_quality/",
    "does_not_need_expert_review": "bad_quality/",
}

#model settings 
MODEL_ARCH = "efficientnet_b0"
NUM_CLASSES = 2
IMAGE_SIZE = 224
BATCH_SIZE = 32
NUM_EPOCHS = 100
LEARNING_RATE = 0.0001
TRAIN_SPLIT = 0.8
VAL_SPLIT = 0.1
TEST_SPLIT = 0.1
RANDOM_SEED = 42
N_FOLDS = 3

#early stopping
EARLY_STOP_PATIENCE = 7
SCHEDULER_PATIENCE = 3

"""
Batch prediction script — runs the trained model on all images in an S3 folder
and prints a labeled summary with confidence scores.

Usage (from backend/ directory):
    python3 -m scripts.batch_predict_s3 --prefix images/
    python3 -m scripts.batch_predict_s3 --prefix uploads/ --min-confidence 0.8
"""

import argparse
import tempfile
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Predict/label images from S3 bucket")
    parser.add_argument("--prefix", required=True, help="S3 folder prefix (e.g. 'images/')")
    parser.add_argument("--min-confidence", type=float, default=0.0,
                        help="Only show results above this confidence (0.0 - 1.0)")
    args = parser.parse_args()

    from ml.predict import PredictionService
    from services.s3_service import s3_service

    # Load model
    service = PredictionService.get_instance()
    if not service.load_model():
        print("ERROR: No trained model found at ml_models/latest.pth")
        sys.exit(1)

    print(f"\nModel loaded: {service.arch}")
    print(f"Listing images under prefix: '{args.prefix}'")

    urls = s3_service.list_objects(args.prefix)
    if not urls:
        print(f"No images found under prefix '{args.prefix}'")
        sys.exit(0)

    print(f"Found {len(urls)} images\n")
    print(f"{'Filename':<50} {'Label':<35} {'Confidence':>10}")
    print("-" * 97)

    needs_review = []
    does_not_need_review = []
    errors = []

    for url in urls:
        filename = os.path.basename(url)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            if not s3_service.download_file(url, tmp_path):
                errors.append(filename)
                continue

            with open(tmp_path, "rb") as f:
                image_bytes = f.read()

            result = service.predict(image_bytes)
            label = result["label"]
            confidence = result["confidence"]

            if confidence < args.min_confidence:
                continue

            if label == "needs_expert_review":
                needs_review.append((filename, confidence))
            else:
                does_not_need_review.append((filename, confidence))

            print(f"{filename:<50} {label:<35} {confidence:>10.4f}")

        except Exception as e:
            errors.append(filename)
            print(f"{filename:<50} ERROR: {str(e)}")
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    # Summary
    total = len(needs_review) + len(does_not_need_review)
    print("\n" + "=" * 97)
    print(f"SUMMARY")
    print(f"  needs_expert_review:        {len(needs_review):>4} images")
    print(f"  does_not_need_expert_review:{len(does_not_need_review):>4} images")
    if errors:
        print(f"  errors:                     {len(errors):>4} images")
    print(f"  total processed:            {total:>4} images")
    print("=" * 97)


if __name__ == "__main__":
    main()

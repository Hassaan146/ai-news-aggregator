"""Daily runner - scheduled execution entry point."""

from app.pipeline import run_pipeline


if __name__ == "__main__":
    print(run_pipeline())

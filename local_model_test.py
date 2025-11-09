import traceback

MODEL = "google/flan-t5-small"
PROMPT = "What is habeas corpus?"

print(f"Test start: model={MODEL}")
try:
    from transformers import pipeline
    import transformers
    import torch
    print("transformers version:", transformers.__version__)
    print("torch available:", torch.__version__)

    print("Creating pipeline...")
    # flan-t5 is text2text, use text2text-generation
    pipe = pipeline("text2text-generation", model=MODEL, device_map=None)
    print("Pipeline created. Running generation...")
    out = pipe(PROMPT, max_new_tokens=64)
    print("Generation output:")
    print(out)
except Exception as e:
    print("ERROR during local model test:")
    traceback.print_exc()

print("Test finished")

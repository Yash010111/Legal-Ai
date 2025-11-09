import traceback
import os
MODEL = "google/flan-t5-small"
PROMPT = "What is habeas corpus?"
print(f"Test start (no auth): model={MODEL}")
try:
    os.environ.pop('HF_HOME', None)
    os.environ.pop('HUGGINGFACE_HUB_TOKEN', None)
    os.environ.pop('HF_HUB_TOKEN', None)
    # Explicitly request no auth
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline, logging
    logging.set_verbosity_error()
    print("Loading tokenizer (no auth)...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL, use_auth_token=False)
    print("Loading model (no auth)...")
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL, use_auth_token=False)
    print("Creating pipeline...")
    pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer, device_map=None)
    print("Running generation...")
    out = pipe(PROMPT, max_new_tokens=64)
    print("Generation output:")
    print(out)
except Exception as e:
    print("ERROR during no-auth local model test:")
    traceback.print_exc()
print("Test finished")

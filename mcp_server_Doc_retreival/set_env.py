"""
Minimal set_env.py — prompt for Hugging Face token and set it in the current process.

Usage:
  # Prompt interactively
  python set_env.py --prompt

  # Provide token on command line (beware shell history)
  python set_env.py --token hf_xxxYOURTOKENxxx

This script intentionally keeps behavior minimal: it sets HUGGINGFACE_API_TOKEN
in the current process environment and prints a short confirmation. It does NOT
persist to disk, write .env, or log secrets.
"""

import argparse
import os
import getpass
import sys


def main(argv=None):
    p = argparse.ArgumentParser(description="Set HUGGINGFACE_API_TOKEN for current process")
    p.add_argument("--token", "-t", help="Hugging Face API token (hf_...)")
    p.add_argument("--prompt", "-p", action="store_true", help="Prompt for token securely")
    args = p.parse_args(argv)

    token = args.token
    if args.prompt and not token:
        try:
            token = getpass.getpass("Enter Hugging Face token (input hidden): ")
        except Exception:
            token = input("Enter Hugging Face token: ")

    if not token:
        print("No token provided. Use --token or --prompt.")
        return 2

    # set for current process only
    os.environ["HUGGINGFACE_API_TOKEN"] = token
    print("HUGGINGFACE_API_TOKEN set for current process (not persisted).")
    return 0


if __name__ == '__main__':
    sys.exit(main())

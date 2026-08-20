#!/usr/bin/env python3
"""Call an OpenAI-format chat model. stdlib only — no install step.

DeepSeek, OpenAI, OpenRouter, Groq, and a local Ollama all speak the same
chat/completions wire format, so one function covers them; only base_url,
key, and model differ. Claude is not here on purpose — the agent reading this
repo *is* Claude, and Anthropic's API is not OpenAI-compatible.

    python3 bin/llm.py -m deepseek-chat "Rate 0-5 relevance to RAG: <abstract>"
    cat abstract.txt | python3 bin/llm.py -m deepseek-chat "Summarize in 2 lines:"
    python3 bin/llm.py -p groq -m llama-3.3-70b-versatile "..."
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

# provider -> (base_url, env var holding the key)
PROVIDERS = {
    "deepseek": ("https://api.deepseek.com/v1", "DEEPSEEK_API_KEY"),
    "openai": ("https://api.openai.com/v1", "OPENAI_API_KEY"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    "ollama": ("http://localhost:11434/v1", None),  # local, no key
}


def resolve(provider):
    """Return (base_url, api_key). Fails loudly on a missing key."""
    if provider not in PROVIDERS:
        sys.exit(f"unknown provider {provider!r}; pick one of {', '.join(PROVIDERS)}")
    base, env = PROVIDERS[provider]
    if env is None:
        return base, "none"
    key = os.environ.get(env)
    if not key:
        sys.exit(f"{env} is not set (needed for provider {provider!r})")
    return base, key


def chat(provider, model, prompt, temperature=0.0, max_tokens=2048):
    base, key = resolve(provider)
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        sys.exit(f"{provider} {e.code}: {e.read().decode()[:400]}")


def selftest():
    assert resolve("ollama") == ("http://localhost:11434/v1", "none")
    os.environ["DEEPSEEK_API_KEY"] = "x"
    assert resolve("deepseek")[0] == "https://api.deepseek.com/v1"
    # a missing key must exit, not silently send an unauthenticated request
    os.environ.pop("GROQ_API_KEY", None)
    try:
        resolve("groq")
    except SystemExit as e:
        assert "GROQ_API_KEY" in str(e)
    else:
        raise AssertionError("missing key did not exit")
    print("ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prompt", nargs="?", help="prompt; stdin is appended if piped")
    ap.add_argument("-p", "--provider", default="deepseek", choices=list(PROVIDERS))
    ap.add_argument("-m", "--model", help="model id (required unless --selftest)")
    ap.add_argument("-t", "--temperature", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if not a.model:
        ap.error("-m/--model is required")

    parts = [a.prompt] if a.prompt else []
    if not sys.stdin.isatty():
        parts.append(sys.stdin.read())
    if not parts:
        ap.error("give a prompt argument or pipe text on stdin")

    print(chat(a.provider, a.model, "\n\n".join(parts), a.temperature, a.max_tokens))


if __name__ == "__main__":
    main()

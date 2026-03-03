import json
import os
import sys
import time
import urllib.error
import urllib.request

OLLAMA_BASE_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434").rstrip("/")
MODEL_NAME = os.environ.get("OLLAMA_MODEL", "llama3")
TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"
PULL_URL = f"{OLLAMA_BASE_URL}/api/pull"
MAX_WAIT_SECONDS = int(os.environ.get("OLLAMA_WAIT_TIMEOUT", "300"))
WAIT_INTERVAL_SECONDS = 2


def log(message: str) -> None:
    print(f"[ollama-init] {message}", flush=True)


def wait_for_ollama() -> None:
    log(f"Waiting for Ollama at {TAGS_URL} (timeout: {MAX_WAIT_SECONDS}s)...")
    deadline = time.time() + MAX_WAIT_SECONDS

    while time.time() < deadline:
        try:
            with urllib.request.urlopen(TAGS_URL, timeout=5) as response:
                if response.status == 200:
                    log("Ollama is reachable.")
                    return
        except (urllib.error.URLError, TimeoutError, ConnectionError) as err:
            log(f"Ollama not ready yet: {err}")
        except Exception as err:  # noqa: BLE001
            log(f"Unexpected error while checking Ollama readiness: {err}")

        time.sleep(WAIT_INTERVAL_SECONDS)

    raise TimeoutError(f"Timed out waiting for Ollama after {MAX_WAIT_SECONDS} seconds")


def get_installed_models() -> set[str]:
    with urllib.request.urlopen(TAGS_URL, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))

    models = payload.get("models", [])
    installed = set()
    for model in models:
        name = model.get("name", "")
        if not name:
            continue
        installed.add(name)
        installed.add(name.split(":", 1)[0])

    return installed


def pull_model(model_name: str) -> None:
    data = json.dumps({"name": model_name}).encode("utf-8")
    request = urllib.request.Request(
        PULL_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    log(f"Pulling model '{model_name}' from Ollama...")
    with urllib.request.urlopen(request, timeout=600) as response:
        for raw_line in response:
            line = raw_line.decode("utf-8").strip()
            if line:
                log(f"pull progress: {line}")

                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    # Keep logging plain-text/partial lines from the streaming API.
                    continue

                status = str(event.get("status", "")).strip().lower()
                if status == "success" or event.get("done") is True:
                    log(f"Model '{model_name}' pull completed.")
                    break

                if "error" in event:
                    raise RuntimeError(f"Ollama pull error: {event['error']}")


def main() -> int:
    log(f"Target model: {MODEL_NAME}")
    wait_for_ollama()

    try:
        installed_models = get_installed_models()
    except Exception as err:  # noqa: BLE001
        log(f"Failed to query installed models: {err}")
        return 1

    if MODEL_NAME in installed_models:
        log(f"Model '{MODEL_NAME}' already exists. Nothing to do.")
        return 0

    try:
        pull_model(MODEL_NAME)
    except Exception as err:  # noqa: BLE001
        log(f"Model pull failed: {err}")
        return 1

    log(f"Model '{MODEL_NAME}' is ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

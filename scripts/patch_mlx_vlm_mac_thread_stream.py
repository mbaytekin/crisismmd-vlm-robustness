#!/usr/bin/env python3
"""Apply the V3 compatibility patches required by mlx-vlm 0.6.3 on macOS."""

from __future__ import annotations

import importlib.metadata
from pathlib import Path


EXPECTED_VERSION = "0.6.3"
ORIGINAL_GENERATE = """        # CPU preprocessing (tokenize, load images) on caller thread.
        # GPU work (vision encoder) deferred to GPU thread.
        raw_inputs = self._cpu_preprocess(prompt, images, audio)
        prompt_tokens = _count_prompt_tokens(raw_inputs)
        _check_configured_context_budget(prompt_tokens, args.max_tokens)
"""
PATCHED_GENERATE = """        # MLX streams are thread-local. Defer preprocessing so all arrays are
        # created on the same worker thread that performs generation.
        raw_inputs = (prompt, images, audio)
        prompt_tokens = 0
"""
ORIGINAL_WORKER = """                for rqueue, raw_inputs, prompt_tokens, args, images in new_items:
                    if batch_gen is None:
"""
PATCHED_WORKER = """                for rqueue, raw_inputs, prompt_tokens, args, images in new_items:
                    if not isinstance(raw_inputs, dict):
                        raw_inputs = self._cpu_preprocess(*raw_inputs)
                    prompt_tokens = _count_prompt_tokens(raw_inputs)
                    _check_configured_context_budget(prompt_tokens, args.max_tokens)
                    if batch_gen is None:
"""
ORIGINAL_MESSAGE_FORMATTER = """    formatter = MessageFormatter(model_name)

    return formatter.format_message(
"""
PATCHED_MESSAGE_FORMATTER = """    # Mistral3's bundled Jinja template concatenates system/assistant
    # content as strings. Preserve those roles as text instead of wrapping
    # them in the multimodal list format used for user image messages.
    if model_name.lower() == "mistral3" and role in ("system", "assistant"):
        return {"role": role, "content": prompt}

    formatter = MessageFormatter(model_name)

    return formatter.format_message(
"""


def main() -> None:
    distribution = importlib.metadata.distribution("mlx-vlm")
    version = distribution.version
    if version != EXPECTED_VERSION:
        raise RuntimeError(
            f"Expected mlx-vlm {EXPECTED_VERSION}, found {version}. Run scripts/setup_macos.sh."
        )

    generation_path = Path(distribution.locate_file("mlx_vlm/server/generation.py"))
    if not generation_path.is_file():
        raise RuntimeError(f"Could not locate mlx_vlm.server.generation: {generation_path}")
    generation = generation_path.read_text(encoding="utf-8")
    if PATCHED_GENERATE in generation and PATCHED_WORKER in generation:
        print(f"MLX-VLM Mac thread-stream patch already applied: {generation_path}")
    else:
        if ORIGINAL_GENERATE not in generation or ORIGINAL_WORKER not in generation:
            raise RuntimeError(f"Refusing to patch unexpected mlx-vlm source: {generation_path}")
        generation = generation.replace(ORIGINAL_GENERATE, PATCHED_GENERATE, 1)
        generation = generation.replace(ORIGINAL_WORKER, PATCHED_WORKER, 1)
        generation_path.write_text(generation, encoding="utf-8")
        print(f"Applied MLX-VLM Mac thread-stream patch: {generation_path}")

    prompt_path = Path(distribution.locate_file("mlx_vlm/prompt_utils.py"))
    if not prompt_path.is_file():
        raise RuntimeError(f"Could not locate mlx_vlm.prompt_utils: {prompt_path}")
    prompt_source = prompt_path.read_text(encoding="utf-8")
    if PATCHED_MESSAGE_FORMATTER in prompt_source:
        print(f"MLX-VLM Mistral3 role-content patch already applied: {prompt_path}")
    else:
        if ORIGINAL_MESSAGE_FORMATTER not in prompt_source:
            raise RuntimeError(f"Refusing to patch unexpected mlx-vlm source: {prompt_path}")
        prompt_source = prompt_source.replace(
            ORIGINAL_MESSAGE_FORMATTER, PATCHED_MESSAGE_FORMATTER, 1
        )
        prompt_path.write_text(prompt_source, encoding="utf-8")
        print(f"Applied MLX-VLM Mistral3 role-content patch: {prompt_path}")


if __name__ == "__main__":
    main()

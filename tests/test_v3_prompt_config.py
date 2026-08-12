from src.v3_inference import DEFAULT_PROMPT_CONFIG, prompt_cfg


def test_prompt_cfg_defaults_to_frozen_prompt():
    prompt = prompt_cfg()

    assert prompt["version"] == "frozen_p5_rubric"
    assert prompt["prompt_config"] == DEFAULT_PROMPT_CONFIG


def test_prompt_cfg_accepts_exploratory_few_shot_prompt():
    prompt = prompt_cfg("configs/prompts/p4_few_shot.yaml")

    assert prompt["version"] == "p4_few_shot"
    assert prompt["prompt_config"] == "configs/prompts/p4_few_shot.yaml"
    assert prompt["prompt_hash"] != prompt_cfg()["prompt_hash"]
    assert prompt["user_prompt_template"].count("Output:") == 6


def test_rubric_prompt_pair_differs_only_by_demonstrations():
    zero = prompt_cfg("configs/prompts/p5_rubric_zero_shot.yaml")
    few = prompt_cfg("configs/prompts/p6_rubric_few_shot.yaml")

    assert zero["system_prompt"] == few["system_prompt"]
    assert "Boundary rules:" in zero["user_prompt_template"]
    assert "Boundary rules:" in few["user_prompt_template"]
    assert "Calibration examples" not in zero["user_prompt_template"]
    assert few["user_prompt_template"].count("Output:") == 6


def test_frozen_v4_is_exact_p5_prompt_lock():
    candidate = prompt_cfg("configs/prompts/p5_rubric_zero_shot.yaml")
    frozen = prompt_cfg("configs/prompts/frozen_prompt_v4.yaml")

    assert frozen["version"] == "frozen_p5_rubric"
    assert frozen["prompt_hash"] == candidate["prompt_hash"]

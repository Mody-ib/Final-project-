"""Lazy-loaded local LLM. The API starts fine without torch/transformers;
only the two AI endpoints need them."""
_tok = _model = None
MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"


def _load():
    global _tok, _model
    if _model is None:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        _tok = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME, torch_dtype="auto", device_map="auto", low_cpu_mem_usage=True
        )
    return _tok, _model


def generate(system: str, prompt: str, max_new_tokens: int) -> str:
    tok, model = _load()
    messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tok([text], return_tensors="pt").to(model.device)
    out = model.generate(**inputs, max_new_tokens=max_new_tokens)
    return tok.batch_decode(out[:, inputs.input_ids.shape[1]:], skip_special_tokens=True)[0]

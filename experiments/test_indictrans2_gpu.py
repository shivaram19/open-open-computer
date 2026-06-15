"""Quick sensor: load IndicTrans2 and translate a Telugu sentence."""
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

model_id = "/home/Ubuntu/models/indictrans2"
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")

tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
model = AutoModelForSeq2SeqLM.from_pretrained(model_id, trust_remote_code=True).to(device)

source_lang = "tel_Telu"
target_lang = "tam_Taml"
text = "ఇది ఒక పరీక్ష వాక్యం."

prefix = f"{source_lang} {target_lang} "
inputs = tokenizer(prefix + text, return_tensors="pt", padding=True, truncation=True).to(device)
model.eval()
with torch.no_grad():
    outputs = model.generate(**inputs, use_cache=False)
translated = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(f"{source_lang} -> {target_lang}: {translated}")



from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
model_name = "Juner/AI-generated-text-detection-pair"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

input_text =  "Input text"

inputs = tokenizer(  
    input_text,
    return_tensors="pt",
    truncation=True,
    max_length=512,
    padding="max_length"
)

# Run model
with torch.no_grad():
    outputs = model(**inputs)

# Get predictions
predictions = torch.argmax(outputs.logits, dim=1)

# Interpret the prediction
label_map = {0: "Human-written", 1: "AI-generated"}
print(f"Prediction: {label_map[predictions.item()]}")



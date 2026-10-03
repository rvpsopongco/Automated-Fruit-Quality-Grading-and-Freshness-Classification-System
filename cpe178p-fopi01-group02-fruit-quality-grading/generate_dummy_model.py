import torch
import torch.nn as nn
import os

class DummyFruitModel(nn.Module):
    def __init__(self):
        super(DummyFruitModel, self).__init__()
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(3, 6)

    def forward(self, x):
        x = self.pool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x

model = DummyFruitModel()
model.eval()
os.makedirs("models", exist_ok=True)
dummy_input = torch.randn(1, 3, 224, 224)
torch.onnx.export(
    model,
    dummy_input,
    "models/fruit_model.onnx",
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}}
)
print("✅ Success! 'fruit_model.onnx' created.")
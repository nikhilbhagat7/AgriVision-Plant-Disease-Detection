import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import timm

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

import matplotlib.pyplot as plt
import seaborn as sns

# Config
TEST_DIR = "dataset/test"
MODEL_PATH = "models/best_model.pth"

BATCH_SIZE = 16
IMG_SIZE = 300

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Transforms
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])

# Load data
test_dataset = datasets.ImageFolder(TEST_DIR, transform=transform)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

class_names = test_dataset.classes
NUM_CLASSES = len(class_names)

print("Total classes:", NUM_CLASSES)

# Load model
model = timm.create_model("efficientnet_b3", pretrained=False, num_classes=NUM_CLASSES)

# Load weights(best_model.ptf)
state_dict = torch.load(MODEL_PATH, map_location=DEVICE)
model.load_state_dict(state_dict)

model = model.to(DEVICE)
model.eval()    # eval mode

# Test loop
all_preds = []
all_labels = []

with torch.no_grad():
    for images, labels in test_loader:

        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        outputs = model(images)

        preds = torch.argmax(outputs, dim=1)

        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

# # 1. Accuracy
# accuracy = accuracy_score(all_labels, all_preds)
# print("\nAccuracy:", round(accuracy, 4))


# # 2. Precision, Recall, F1-score
# report = classification_report(all_labels, all_preds, target_names=class_names)
# print("\nClassification Report:")
# print(report)

# CONFUSION MATRIX
cm = confusion_matrix(all_labels, all_preds)

plt.figure(figsize=(10, 10))

sns.heatmap(
    cm,
    annot=False,        # turn to True if small classes
    fmt='d',
    cmap='Blues',
    xticklabels=class_names,
    yticklabels=class_names
)

plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")

plt.savefig("confusion_matrix.png")
plt.show()
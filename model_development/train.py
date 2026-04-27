import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import timm

## TRAINING CONFIG
TRAIN_DIR = "dataset/train"
VAL_DIR   = "dataset/valid"

MODEL_DIR = "models"
BACKUP_DIR = os.path.join(MODEL_DIR, "backup")

BATCH_SIZE = 16
EPOCHS = 15
LR = 3e-4
IMG_SIZE = 300

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

os.makedirs(BACKUP_DIR, exist_ok=True)

## DATA PROCESSING

train_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),

    # augmentations
    transforms.RandomHorizontalFlip(),   # helps with orientation
    transforms.RandomRotation(10),       # small rotation only
    transforms.ColorJitter(brightness=0.2,contrast=0.2,saturation=0.2),

    transforms.ToTensor(),

    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])

val_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])

## loading datasets
train_dataset = datasets.ImageFolder(TRAIN_DIR, transform=train_transform)
print("train samples:", len(train_dataset))
val_dataset   = datasets.ImageFolder(VAL_DIR, transform=val_transform)
print("val samples:", len(val_dataset))
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=4)

# number of classes
NUM_CLASSES = len(train_dataset.classes)
print("classes:", NUM_CLASSES)

# MODEL
model = timm.create_model("efficientnet_b3", pretrained=True, num_classes=NUM_CLASSES)
model = model.to(DEVICE)

# LOSS & OPTIMIZER
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.AdamW(model.parameters(), lr=LR)

# TRAIN FUNCTION
def train_one_epoch():
    model.train()
    total_loss = 0

    for images, labels in train_loader:
        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        optimizer.zero_grad()

        # forward
        outputs = model(images)
        loss = criterion(outputs, labels)

        # backward
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

        # print sometimes
        print("batch loss:", loss.item())

    avg_loss = total_loss / len(train_loader)
    print("epoch loss:", avg_loss)

    return avg_loss

# VALIDATION FUNCTION
def validate():
    model.eval()

    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            outputs = model(images)

            preds = torch.argmax(outputs, dim=1)

            correct += (preds == labels).sum().item()
            total += labels.size(0)

    acc = correct / total
    print("validation accuracy:", acc)

    return acc

# TRAIN LOOP
best_acc = 0.0

for epoch in range(EPOCHS):
    print(f"\nEpoch {epoch+1}/{EPOCHS}")

    train_loss = train_one_epoch()
    print("train loss:", train_loss)

    val_acc = validate()
    print("val acc:", val_acc)

    # save best model only
    if val_acc > best_acc:
        best_acc = val_acc
        torch.save(model.state_dict(), "best_model.pth")
        print("saved new best model")
    # save each model for backup
    torch.save(model.state_dict(), f"model_epoch_{epoch+1}.pth")

print("\nTraining complete!")
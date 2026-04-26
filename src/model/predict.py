import torch  
import timm
from torchvision import transforms
from PIL import Image
import io
from src.model.labels import LABELS, LABEL_TO_NAME
from src.model.disease_info import DISEASE_INFO
from pathlib import Path

if torch.cuda.is_available():
  device='cuda'
else:
  device='cpu'

CLASS_LABELS = LABELS 
NUM_CLASSES = len(CLASS_LABELS)

model = timm.create_model('efficientnet_b3', pretrained=False, num_classes=NUM_CLASSES)

MODEL_PATH = Path(__file__).parent / "best_model.pth"
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))

model.to(device)

model.eval()

transform = transforms.Compose([
    transforms.Resize((300, 300)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# Main Prediction Function
def predict_output(image_bytes: bytes) -> dict:
    
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
   
    image_tensor = transform(image)
    image_tensor = image_tensor.unsqueeze(0)
    image_tensor = image_tensor.to(device)

    with torch.no_grad():
        # predicted class
        outputs = model(image_tensor) 
        predicted_index = torch.argmax(outputs, dim=1).item()
        predicted_class = CLASS_LABELS[predicted_index]
        # confidence value of pred class
        probs = torch.softmax(outputs, dim=1)
        confidence = probs[0][predicted_index].item()

    CONFIDENCE_THRESHOLD = 0.5

    if confidence < CONFIDENCE_THRESHOLD:
        return {
            'label': predicted_class,
            'confidence': confidence,
            'disease_name': "Not confident. Make sure the image belongs to one of the supported disease classes. Try uploading a clearer image with better lighting or a different angle.",
            'cause': 'No information available',
            'cure': 'No information available'
        }
    else:
        return {
            'label': predicted_class,
            'confidence': confidence,
            'disease_name': LABEL_TO_NAME[predicted_class],
            'cause': DISEASE_INFO[predicted_class].get('cause'),
            'cure': DISEASE_INFO[predicted_class].get('cure')
        }
from fastapi import FastAPI, UploadFile, File
from fastapi import HTTPException

from src.model.predict import predict_output
from src.api.schemas.prediction_response import PredictionResponse

app = FastAPI()

@app.get('/')
def home():
  return{'message':'Plant Disease Detection API. Go to /docs to test the API.'}

@app.post('/predict', response_model=PredictionResponse)
async def predict( file: UploadFile = File(...) ):
  try:
    image_bytes = await file.read()
    prediction = predict_output(image_bytes)
    return prediction
  except Exception as e:
    raise HTTPException(status_code=500, detail="Invalid image file")

@app.get('/health')
def health_check():
    return {
    'status': 'ok',
  }

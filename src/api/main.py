from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.model.predict import predict_output
from src.api.schemas.prediction_response import PredictionResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.get('/')
# def home():
#   return{'message':'Plant Disease Detection API.'}

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

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
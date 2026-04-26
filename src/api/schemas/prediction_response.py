from pydantic import BaseModel, Field

class PredictionResponse(BaseModel):
  label: str=Field(
    ...,
    description="",
    example="Apple___Black_rot"
  )
  confidence: float=Field(
      ...,
      description="Confidence score of the prediction",
      example=0.92
  )
  disease_name: str=Field(
    ...,
    description="The predicted plant disease name",
    example="Apple Black_rot"
  )
  cause: str = Field(
      ...,
      description="Cause of the disease",
      example="Fungal infection in humid conditions"
  )
  cure: str = Field(
      ...,
      description="Recommended treatment or cure",
      example="Apply fungicides and remove infected leaves"
  )
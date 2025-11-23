from pydantic import BaseModel, Field


class ExtractStructuredRequest(BaseModel):
    data: str = Field(description="The medical note to extract structured data from")


class Condition(BaseModel):
    name: str = Field(description="The name of the condition")
    icd_code: str = Field(description="The ICD code of the condition")


class Diagnosis(BaseModel):
    name: str = Field(description="The name of the diagnosis")
    icd_code: str = Field(description="The ICD code of the diagnosis")


class Treatment(BaseModel):
    name: str = Field(description="The name of the treatment")
    icd_code: str = Field(description="The ICD code of the treatment")


class Medication(BaseModel):
    name: str = Field(description="The name of the medication")
    rx_norm_code: str = Field(description="The RXNorm code of the medication")


class StructuredData(BaseModel):
    name: str = Field(description="The name of the patient")
    age: int | None = Field(description="The age of the patient")
    conditions: list[Condition] = Field(description="The conditions of the patient")
    diagnoses: list[Diagnosis] = Field(description="The diagnoses of the patient")
    treatments: list[Treatment] = Field(description="The treatments of the patient")
    medications: list[Medication] = Field(description="The medications of the patient")


class ExtractStructuredResponse(BaseModel):
    structured_data: StructuredData = Field(description="The structured data of the patient")

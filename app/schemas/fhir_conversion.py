from typing import Any

from pydantic import BaseModel, Field

from app.schemas.extract_structured import StructuredData


class FHIRConversionRequest(BaseModel):
    structured_data: StructuredData = Field(
        description="The structured data to convert to FHIR format"
    )


class FHIRConversionResponse(BaseModel):
    fhir_bundle: dict[str, Any] = Field(description="The FHIR Bundle containing all resources")

"""Tests for FHIR conversion service."""

import pytest

from app.schemas.extract_structured import (
    Condition,
    Diagnosis,
    Medication,
    StructuredData,
    Treatment,
)
from app.services.fhir_conversion_service import FHIRConversionService


@pytest.fixture
def sample_structured_data() -> StructuredData:
    """Sample structured medical data for testing."""
    return StructuredData(
        name="Alan Turning",
        age=50,
        conditions=[
            Condition(name="Hyperlipidemia", icd_code="E78.5"),
            Condition(name="Overweight", icd_code="E66.3"),
        ],
        diagnoses=[
            Diagnosis(name="Annual Health Exam", icd_code="Z00.00"),
        ],
        treatments=[
            Treatment(name="Influenza Vaccine", icd_code="Z23"),
        ],
        medications=[
            Medication(name="Simvastatin 10mg", rx_norm_code="36567"),
        ],
    )


def test_convert_to_fhir_creates_patient_resource(sample_structured_data: StructuredData) -> None:
    """Test that a Patient resource is created with correct data."""
    service = FHIRConversionService()
    result = service.convert_to_fhir(sample_structured_data)

    # Find the Patient resource
    entries = result["entry"]
    patient_entry = next((e for e in entries if e["resource"]["resourceType"] == "Patient"), None)

    assert patient_entry is not None
    patient = patient_entry["resource"]

    # Verify Patient fields
    assert patient["resourceType"] == "Patient"
    assert "id" in patient
    assert len(patient["name"]) == 1
    assert patient["name"][0]["text"] == "Alan Turning"
    assert "birthDate" in patient
    # Age 50 in current year should give birth year around 1974 (approximate)
    birth_date_str = str(patient["birthDate"])
    assert birth_date_str.startswith("1974") or birth_date_str.startswith("1975")


def test_convert_to_fhir_creates_condition_resources(
    sample_structured_data: StructuredData,
) -> None:
    """Test that Condition resources are created from conditions and diagnoses."""
    service = FHIRConversionService()
    result = service.convert_to_fhir(sample_structured_data)

    # Find all Condition resources
    entries = result["entry"]
    condition_entries = [e for e in entries if e["resource"]["resourceType"] == "Condition"]

    # Should have 3 conditions: 2 from conditions + 1 from diagnoses
    assert len(condition_entries) == 3

    # Check one condition in detail
    hyperlipidemia = next(
        (
            e["resource"]
            for e in condition_entries
            if e["resource"]["code"]["text"] == "Hyperlipidemia"
        ),
        None,
    )
    assert hyperlipidemia is not None
    assert hyperlipidemia["resourceType"] == "Condition"
    assert "id" in hyperlipidemia
    assert hyperlipidemia["code"]["coding"][0]["system"] == "http://hl7.org/fhir/sid/icd-10"
    assert hyperlipidemia["code"]["coding"][0]["code"] == "E78.5"
    assert hyperlipidemia["code"]["coding"][0]["display"] == "Hyperlipidemia"
    assert "subject" in hyperlipidemia
    assert hyperlipidemia["subject"]["reference"].startswith("Patient/")
    assert hyperlipidemia["clinicalStatus"]["coding"][0]["code"] == "active"
    assert hyperlipidemia["verificationStatus"]["coding"][0]["code"] == "confirmed"


def test_convert_to_fhir_creates_procedure_resources(
    sample_structured_data: StructuredData,
) -> None:
    """Test that Procedure resources are created from treatments."""
    service = FHIRConversionService()
    result = service.convert_to_fhir(sample_structured_data)

    # Find all Procedure resources
    entries = result["entry"]
    procedure_entries = [e for e in entries if e["resource"]["resourceType"] == "Procedure"]

    # Should have 1 procedure
    assert len(procedure_entries) == 1

    procedure = procedure_entries[0]["resource"]
    assert procedure["resourceType"] == "Procedure"
    assert "id" in procedure
    assert procedure["status"] == "completed"
    assert procedure["code"]["text"] == "Influenza Vaccine"
    assert procedure["code"]["coding"][0]["system"] == "http://hl7.org/fhir/sid/icd-10-procedures"
    assert procedure["code"]["coding"][0]["code"] == "Z23"
    assert "subject" in procedure
    assert procedure["subject"]["reference"].startswith("Patient/")


def test_convert_to_fhir_creates_medication_resources(
    sample_structured_data: StructuredData,
) -> None:
    """Test that MedicationStatement resources are created from medications."""
    service = FHIRConversionService()
    result = service.convert_to_fhir(sample_structured_data)

    # Find all MedicationStatement resources
    entries = result["entry"]
    medication_entries = [
        e for e in entries if e["resource"]["resourceType"] == "MedicationStatement"
    ]

    # Should have 1 medication
    assert len(medication_entries) == 1

    medication = medication_entries[0]["resource"]
    assert medication["resourceType"] == "MedicationStatement"
    assert "id" in medication
    assert medication["status"] == "recorded"
    assert medication["medication"]["concept"]["text"] == "Simvastatin 10mg"
    assert (
        medication["medication"]["concept"]["coding"][0]["system"]
        == "http://www.nlm.nih.gov/research/umls/rxnorm"
    )
    assert medication["medication"]["concept"]["coding"][0]["code"] == "36567"
    assert "subject" in medication
    assert medication["subject"]["reference"].startswith("Patient/")


def test_convert_to_fhir_links_resources_to_patient(
    sample_structured_data: StructuredData,
) -> None:
    """Test that all resources reference the same patient ID."""
    service = FHIRConversionService()
    result = service.convert_to_fhir(sample_structured_data)

    entries = result["entry"]

    # Get patient ID
    patient_entry = next((e for e in entries if e["resource"]["resourceType"] == "Patient"), None)
    patient_id = patient_entry["resource"]["id"]

    # Check all other resources reference this patient
    for entry in entries:
        resource = entry["resource"]
        if resource["resourceType"] != "Patient":
            assert "subject" in resource
            assert resource["subject"]["reference"] == f"Patient/{patient_id}"


def test_convert_to_fhir_with_empty_lists() -> None:
    """Test conversion with empty conditions, diagnoses, treatments, and medications."""
    structured_data = StructuredData(
        name="Test Patient",
        age=30,
        conditions=[],
        diagnoses=[],
        treatments=[],
        medications=[],
    )

    service = FHIRConversionService()
    result = service.convert_to_fhir(structured_data)

    # Should still have a Bundle with just the Patient resource
    assert result["resourceType"] == "Bundle"
    assert result["type"] == "collection"
    assert len(result["entry"]) == 1
    assert result["entry"][0]["resource"]["resourceType"] == "Patient"


def test_convert_to_fhir_with_no_age() -> None:
    """Test conversion when age is None."""
    structured_data = StructuredData(
        name="Unknown Age Patient",
        age=None,
        conditions=[],
        diagnoses=[],
        treatments=[],
        medications=[],
    )

    service = FHIRConversionService()
    result = service.convert_to_fhir(structured_data)

    # Find the Patient resource
    entries = result["entry"]
    patient_entry = next((e for e in entries if e["resource"]["resourceType"] == "Patient"), None)
    patient = patient_entry["resource"]

    # Birth date should not be present
    assert "birthDate" not in patient or patient["birthDate"] is None

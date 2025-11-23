"""Service for converting structured medical data to FHIR resources."""

from datetime import date, datetime
from typing import Any
from uuid import uuid4

from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.codeablereference import CodeableReference
from fhir.resources.coding import Coding
from fhir.resources.condition import Condition
from fhir.resources.humanname import HumanName
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.patient import Patient
from fhir.resources.procedure import Procedure
from fhir.resources.reference import Reference

from app.schemas.extract_structured import StructuredData


class FHIRConversionService:
    """Service for converting structured medical data to FHIR resources."""

    def __init__(self):
        """Initialize the FHIR conversion service."""
        pass

    def convert_to_fhir(self, structured_data: StructuredData) -> dict[str, Any]:
        """
        Convert structured medical data to a FHIR Bundle.

        Args:
            structured_data: The structured medical data to convert

        Returns:
            A dictionary representing a FHIR Bundle with all resources
        """
        patient_id = str(uuid4())

        patient = self._create_patient_resource(structured_data, patient_id)
        conditions = self._create_condition_resources(structured_data, patient_id)
        procedures = self._create_procedure_resources(structured_data, patient_id)
        medications = self._create_medication_resources(structured_data, patient_id)

        entries = [BundleEntry(resource=patient)]
        entries.extend([BundleEntry(resource=condition) for condition in conditions])
        entries.extend([BundleEntry(resource=procedure) for procedure in procedures])
        entries.extend([BundleEntry(resource=medication) for medication in medications])

        bundle = Bundle(type="collection", entry=entries)
        return bundle.model_dump(exclude_none=True)

    def _create_patient_resource(self, structured_data: StructuredData, patient_id: str) -> Patient:
        """
        Create a FHIR Patient resource from structured data.

        Args:
            structured_data: The structured medical data
            patient_id: The unique patient identifier

        Returns:
            A FHIR Patient resource
        """
        name = HumanName(text=structured_data.name)

        birth_date: date | None = None
        if structured_data.age:
            approximate_birth_year = datetime.now().year - structured_data.age
            birth_date = date(approximate_birth_year, 1, 1)

        patient = Patient(
            id=patient_id,
            name=[name],
            birthDate=birth_date,
        )

        return patient

    def _create_condition_resources(self, structured_data: StructuredData, patient_id: str) -> list[Condition]:
        """
        Create FHIR Condition resources from structured data.

        Combines both conditions and diagnoses into FHIR Condition resources
        as per FHIR specification.

        Args:
            structured_data: The structured medical data
            patient_id: The unique patient identifier

        Returns:
            A list of FHIR Condition resources
        """
        conditions = []

        for cond in structured_data.conditions:
            condition = Condition(
                id=str(uuid4()),
                code=CodeableConcept(
                    coding=[
                        Coding(
                            system="http://hl7.org/fhir/sid/icd-10",
                            code=cond.icd_code,
                            display=cond.name,
                        )
                    ],
                    text=cond.name,
                ),
                subject=Reference(reference=f"Patient/{patient_id}"),
                clinicalStatus=CodeableConcept(
                    coding=[
                        Coding(
                            system="http://terminology.hl7.org/CodeSystem/condition-clinical",
                            code="active",
                        )
                    ]
                ),
                verificationStatus=CodeableConcept(
                    coding=[
                        Coding(
                            system="http://terminology.hl7.org/CodeSystem/condition-ver-status",
                            code="confirmed",
                        )
                    ]
                ),
            )
            conditions.append(condition)

        for diag in structured_data.diagnoses:
            condition = Condition(
                id=str(uuid4()),
                code=CodeableConcept(
                    coding=[
                        Coding(
                            system="http://hl7.org/fhir/sid/icd-10",
                            code=diag.icd_code,
                            display=diag.name,
                        )
                    ],
                    text=diag.name,
                ),
                subject=Reference(reference=f"Patient/{patient_id}"),
                clinicalStatus=CodeableConcept(
                    coding=[
                        Coding(
                            system="http://terminology.hl7.org/CodeSystem/condition-clinical",
                            code="active",
                        )
                    ]
                ),
                verificationStatus=CodeableConcept(
                    coding=[
                        Coding(
                            system="http://terminology.hl7.org/CodeSystem/condition-ver-status",
                            code="confirmed",
                        )
                    ]
                ),
            )
            conditions.append(condition)

        return conditions

    def _create_procedure_resources(self, structured_data: StructuredData, patient_id: str) -> list[Procedure]:
        """
        Create FHIR Procedure resources from structured data.

        Args:
            structured_data: The structured medical data
            patient_id: The unique patient identifier

        Returns:
            A list of FHIR Procedure resources
        """
        procedures = []

        for treatment in structured_data.treatments:
            procedure = Procedure(
                id=str(uuid4()),
                status="completed",
                code=CodeableConcept(
                    coding=[
                        Coding(
                            system="http://hl7.org/fhir/sid/icd-10-procedures",
                            code=treatment.icd_code,
                            display=treatment.name,
                        )
                    ],
                    text=treatment.name,
                ),
                subject=Reference(reference=f"Patient/{patient_id}"),
            )
            procedures.append(procedure)

        return procedures

    def _create_medication_resources(
        self, structured_data: StructuredData, patient_id: str
    ) -> list[MedicationStatement]:
        """
        Create FHIR MedicationStatement resources from structured data.

        Args:
            structured_data: The structured medical data
            patient_id: The unique patient identifier

        Returns:
            A list of FHIR MedicationStatement resources
        """
        medications = []

        for med in structured_data.medications:
            medication = MedicationStatement(
                id=str(uuid4()),
                status="recorded",
                medication=CodeableReference(
                    concept=CodeableConcept(
                        coding=[
                            Coding(
                                system="http://www.nlm.nih.gov/research/umls/rxnorm",
                                code=med.rx_norm_code,
                                display=med.name,
                            )
                        ],
                        text=med.name,
                    )
                ),
                subject=Reference(reference=f"Patient/{patient_id}"),
            )
            medications.append(medication)

        return medications


def get_fhir_conversion_service() -> FHIRConversionService:
    """
    Dependency injection function for FHIRConversionService.

    Returns:
        An instance of FHIRConversionService
    """
    return FHIRConversionService()

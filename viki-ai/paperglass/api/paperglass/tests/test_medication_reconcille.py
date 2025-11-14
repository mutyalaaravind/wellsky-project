import sys, os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from paperglass.domain.values import MedispanStatus
import pytest
from datetime import datetime
from paperglass.domain.models import ImportedMedicationAggregate, MedicationProfile, ReconcilledMedication, ExtractedMedication, MedicationValue, ExtractedMedicationReference, Score,UserEnteredMedicationAggregate

def test_reconcile_extracted_medications():
    medication_profile = MedicationProfile(id="medication_profile_id",
                                           app_id="008",
                                            tenant_id="abc1",
                                            patient_id="the_one")
    
    extracted_medications = [
        ExtractedMedication(
            id="1",
            deleted=False,
            document_reference="doc1",
            page_id="page1",
            page_number="1",
            document_id="doc1",
            medispan_medication=None,
            medication=MedicationValue(name="Med1", dosage="10mg", route="Oral", frequency="Once a day", instructions="Take with food", form="Tablet", start_date="2022-01-01", end_date="2022-01-31", discontinued_date=None),
            medispan_id="123",
            medispan_status=MedispanStatus.MATCHED,
            score=0.8,
            app_id="008",
            tenant_id="abc1",
            patient_id="the_one",
            document_operation_instance_id="doc_op_id"
        ),
        ExtractedMedication(
            id="2",
            deleted=False,
            document_reference="doc2",
            document_id="doc2",
            page_id="page1",
            page_number="1",
            medispan_medication=None,
            medication=MedicationValue(name="Med2", dosage="20mg", route="Oral", frequency="Twice a day", instructions="Take after meals", form="Capsule", start_date="2022-02-01", end_date="2022-02-28", discontinued_date=None),
            medispan_id="456",
            medispan_status=MedispanStatus.MATCHED,
            score=0.9,
            app_id="008",
            tenant_id="abc1",
            patient_id="the_one",
            document_operation_instance_id="doc_op_id"
        )
    ]
    
    medication_profile.reconcile_extracted_medications(extracted_medications)
    
    assert len(medication_profile.medications) == 2
    
    reconcilled_medication_1 = medication_profile.medications[0]
    assert reconcilled_medication_1.id is not None
    assert reconcilled_medication_1.document_references == ["doc1"]
    assert reconcilled_medication_1.medication.name == "Med1"
    assert reconcilled_medication_1.medication.dosage == "10mg"
    assert reconcilled_medication_1.medication.route == "Oral"
    assert reconcilled_medication_1.medication.frequency == "Once a day"
    assert reconcilled_medication_1.medication.instructions == "Take with food"
    assert reconcilled_medication_1.medication.form == "Tablet"
    assert reconcilled_medication_1.medication.start_date == "2022-01-01"
    assert reconcilled_medication_1.medication.end_date == "2022-01-31"
    assert reconcilled_medication_1.medication.discontinued_date is None
    assert reconcilled_medication_1.medispan_id == "123"
    assert reconcilled_medication_1.medispan_status == MedispanStatus.MATCHED
    assert reconcilled_medication_1.latest_start_date == "2022-01-01"
    assert reconcilled_medication_1.latest_end_date == "2022-01-31"
    assert reconcilled_medication_1.latest_discontinued_date is None
    assert len(reconcilled_medication_1.extracted_medication_reference) == 1
    assert reconcilled_medication_1.extracted_medication_reference[0].document_id == "doc1"
    assert reconcilled_medication_1.extracted_medication_reference[0].extracted_medication_id == "1"
    assert reconcilled_medication_1.extracted_medication_reference[0].document_operation_instance_id is None
    assert reconcilled_medication_1.extracted_medication_reference[0].page_number is None
    assert reconcilled_medication_1.score.overall == 0.8
    assert reconcilled_medication_1.score.details == {}
    
    reconcilled_medication_2 = medication_profile.medications[1]
    assert reconcilled_medication_2.id is not None
    assert reconcilled_medication_2.document_references == ["doc2"]
    assert reconcilled_medication_2.medication.name == "Med2"
    assert reconcilled_medication_2.medication.dosage == "20mg"
    assert reconcilled_medication_2.medication.route == "Oral"
    assert reconcilled_medication_2.medication.frequency == "Twice a day"
    assert reconcilled_medication_2.medication.instructions == "Take after meals"
    assert reconcilled_medication_2.medication.form == "Capsule"
    assert reconcilled_medication_2.medication.start_date == "2022-02-01"
    assert reconcilled_medication_2.medication.end_date == "2022-02-28"
    assert reconcilled_medication_2.medication.discontinued_date is None
    assert reconcilled_medication_2.medispan_id == "456"
    assert reconcilled_medication_2.medispan_status == "Active"
    assert reconcilled_medication_2.latest_start_date == "2022-02-01"
    assert reconcilled_medication_2.latest_end_date == "2022-02-28"
    assert reconcilled_medication_2.latest_discontinued_date is None
    assert len(reconcilled_medication_2.extracted_medication_reference) == 1
    assert reconcilled_medication_2.extracted_medication_reference[0].document_id == "doc2"
    assert reconcilled_medication_2.extracted_medication_reference[0].extracted_medication_id == "2"
    assert reconcilled_medication_2.extracted_medication_reference[0].document_operation_instance_id is None
    assert reconcilled_medication_2.extracted_medication_reference[0].page_number is None
    assert reconcilled_medication_2.score.overall == 0.9
    assert reconcilled_medication_2.score.details == {}

# @pytest.mark.parametrize("edit_type", ["updated", "created"])
# def test_reconcile_user_entered_medication(edit_type):
#     # Create a MedicationProfile instance
#     medication_profile = MedicationProfile.create(app_id="app_id", tenant_id="tenant_id", patient_id="patient_id")

#     # Create a UserEnteredMedicationAggregate instance
#     user_entered_medication = UserEnteredMedicationAggregate(
#         medication=MedicationValue(name="Medication A", dosage="10mg"),
#         medication_profile_reconcilled_medication_id=None,
#         change_sets=[],
#         medication_status="active",
#         modified_by="user",
#         modified_at=datetime.now(),
#         document_id="document_id"
#     )

#     # Call the reconcile_user_entered_medication method
#     reconcilled_medication = medication_profile.reconcile_user_entered_medication(user_entered_medication, edit_type)

#     # Assert that the reconcilled_medication is not None
#     assert reconcilled_medication is not None

#     # Assert that the reconcilled_medication has the correct attributes
#     assert reconcilled_medication.user_entered_medication.medication == user_entered_medication.medication
#     assert reconcilled_medication.user_entered_medication.edit_type == edit_type
#     assert reconcilled_medication.user_entered_medication.change_sets == user_entered_medication.change_sets
#     assert reconcilled_medication.user_entered_medication.medication_status == user_entered_medication.medication_status
#     assert reconcilled_medication.user_entered_medication.modified_by == user_entered_medication.modified_by
#     assert reconcilled_medication.user_entered_medication.modified_at == user_entered_medication.modified_at
#     assert reconcilled_medication.user_entered_medication.document_id == user_entered_medication.document_id

# def test_reconcile_imported_medications():
#     imported_medication = ImportedMedicationAggregate(
#         id="123",
#         host_medication_id="456",
#         medispan_id="789",
#         medication=MedicationValue(
#             name="Medication",
#             dosage="10mg",
#             route="Oral",
#             frequency="Once daily",
#             instructions="Take with food",
#             form="Tablet",
#             start_date="2022-01-01",
#             end_date="2022-01-31",
#             discontinued_date=None,
#             strength="100mg"
#         ),
#         modified_by="John Doe"
#     )

#     medication_profile = MedicationProfile.create("app_id", "tenant_id", "patient_id")
#     medication_profile.reconcile_imported_medications(imported_medication)

#     assert len(medication_profile.medications) == 1
#     reconcilled_medication = medication_profile.medications[0]
#     assert reconcilled_medication.imported_medication is not None
#     assert reconcilled_medication.imported_medication.imported_medication_id == "123"
#     assert reconcilled_medication.imported_medication.host_medication_id == "456"
#     assert reconcilled_medication.imported_medication.medispan_id == "789"
#     assert reconcilled_medication.imported_medication.medication.name == "Medication"
#     assert reconcilled_medication.imported_medication.medication.dosage == "10mg"
#     assert reconcilled_medication.imported_medication.medication.route == "Oral"
#     assert reconcilled_medication.imported_medication.medication.frequency == "Once daily"
#     assert reconcilled_medication.imported_medication.medication.instructions == "Take with food"
#     assert reconcilled_medication.imported_medication.medication.form == "Tablet"
#     assert reconcilled_medication.imported_medication.medication.start_date == "2022-01-01"
#     assert reconcilled_medication.imported_medication.medication.end_date == "2022-01-31"
#     assert reconcilled_medication.imported_medication.medication.discontinued_date is None
#     assert reconcilled_medication.imported_medication.modified_by == "John Doe"

# @pytest.mark.parametrize("edit_type", ["updated", "created"])
# def test_reconcile_user_entered_medication(edit_type):
    # Create a MedicationProfile instance
    medication_profile = MedicationProfile.create(app_id="app_id", tenant_id="tenant_id", patient_id="patient_id")

    # Create a UserEnteredMedicationAggregate instance
    user_entered_medication = UserEnteredMedicationAggregate(
        medication=MedicationValue(name="Medication A", dosage="10mg"),
        medication_profile_reconcilled_medication_id=None,
        change_sets=[],
        medication_status="active",
        modified_by="user",
        modified_at=datetime.now(),
        document_id="document_id"
    )

    # Call the reconcile_user_entered_medication method
    reconcilled_medication = medication_profile.reconcile_user_entered_medication(user_entered_medication, edit_type)

    # Assert that the reconcilled_medication is not None
    assert reconcilled_medication is not None

    # Assert that the reconcilled_medication has the correct attributes
    assert reconcilled_medication.user_entered_medication.medication == user_entered_medication.medication
    assert reconcilled_medication.user_entered_medication.edit_type == edit_type
    assert reconcilled_medication.user_entered_medication.change_sets == user_entered_medication.change_sets
    assert reconcilled_medication.user_entered_medication.medication_status == user_entered_medication.medication_status
    assert reconcilled_medication.user_entered_medication.modified_by == user_entered_medication.modified_by
    assert reconcilled_medication.user_entered_medication.modified_at == user_entered_medication.modified_at
    assert reconcilled_medication.user_entered_medication.document_id == user_entered_medication.document_id
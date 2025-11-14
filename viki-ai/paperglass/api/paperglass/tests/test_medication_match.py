import sys, os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

def test_medication_match():
    from paperglass.domain.values import MedicationValue
    # {"classification": null,
    #         "discontinued_date": "",
    #         "dosage": "1 - 2",
    #         "end_date": null,
    #         "form": "",
    #         "frequency": null,
    #         "instructions": "Take: 1 to 2 tablets ... as needed for pain.",
    #         "medispan_id": "29298",
    #         "name": "Oxycodone HCl Oral Tablet 5 MG",
    #         "route": "",
    #         "start_date": "08/16/2024",
    #         "strength": ""}
    medication = MedicationValue(
        name="Oxycodone HCl Oral Tablet 5 MG",
        medispan_id="",
        classification=None,
        dosage="1 - 2",
        strength="",
        form="",
        route="",
        frequency=None,
        instructions="Take: 1 to 2 tablets ... as needed for pain.",
        start_date="08/16/2024",
        end_date=None,
        discontinued_date=""
    )
    # {"classification": null,
    #         "discontinued_date": null,
    #         "dosage": "1 - 2",
    #         "end_date": null,
    #         "form": "Tablet",
    #         "frequency": "every 4 to 6 hours",
    #         "instructions": "Take: 1 to 2 tablets ... as needed for pain.",
    #         "medispan_id": "29298",
    #         "name": "Oxycodone HCl",
    #         "route": "Oral",
    #         "start_date": "08/16/2024",
    #         "strength": "5 MG"}
    medication2 = MedicationValue(
        name="Oxycodone HCl",
        medispan_id="",
        classification=None,
        dosage="1 - 2",
        strength="5 MG",
        form="Tablet",
        route="Oral",
        frequency="every 4 to 6 hours",
        instructions="Take: 1 to 2 tablets ... as needed for pain.",
        start_date="08/16/2024",
        end_date=None,
        discontinued_date=None
    )

    assert medication.matches(medication2)

import spacy
nlp = spacy.load("en_core_web_md")

def find_common_keys(expected_medication, actual_medication):
    dict1 = expected_medication
    dict2 = actual_medication

    common_list = []
    keys_allowed = ["medispan_id", "name", "name_original", "dosage", "form", "frequency", "instructions", "route", "start_date", "strength", "page_number"]
    keys_for_similarity = ["frequency", "instructions"]
    no_match_count = 0
    medispan_blank = 0    
    medispan_mismatch = 0
    medication_different_count = 0

    missing_in_expected = []
    missing_in_actual = []
    medication_has_difference = False

    # Initialize field mismatch counters
    field_mismatch_counts = {
        "name_mismatch": 0,
        "dosage_mismatch": 0,
        "form_mismatch": 0,
        "frequency_mismatch": 0,
        "instructions_mismatch": 0,
        "route_mismatch": 0,
        "start_date_mismatch": 0,
        "strength_mismatch": 0
    }

    for key in keys_allowed:
        if key in dict1 and key in dict2:
            #Key is in both sets
            if key in keys_for_similarity:                
                match = compare_symantic_similarity(dict1[key], dict2[key])
                common_list.append({
                    "Key":key, 
                    "expected":dict1[key],
                    "actual":dict2[key],
                    "match": match
                })
                if not match:
                    no_match_count += 1
                    medication_has_difference = True
                    if key + "_mismatch" in field_mismatch_counts:
                        field_mismatch_counts[key + "_mismatch"] += 1
            else:                
                match = dict1[key] == dict2[key]
                common_list.append({
                    "Key":key, 
                    "expected":dict1[key],
                    "actual":dict2[key],
                    "match": match
                })
                if key == "medispan_id" and not match:
                    medispan_mismatch += 1
                if not match:
                    medication_has_difference = True
                    if key + "_mismatch" in field_mismatch_counts:
                        field_mismatch_counts[key + "_mismatch"] += 1
        elif key not in dict1 and key not in dict2:
             #Key is not in either, so a naturally equivalent
             pass
        elif key not in dict1:
            #Key is only in expected
            missing_in_expected.append(key)
            if key == "medispan_id":
                medispan_blank += 1
            medication_has_difference = True
            if key + "_mismatch" in field_mismatch_counts:
                field_mismatch_counts[key + "_mismatch"] += 1
        elif key not in dict2:
            #Key is only in actual
            missing_in_actual.append(key)
            if key == "medispan_id":
                medispan_blank += 1
            medication_has_difference = True
            if key + "_mismatch" in field_mismatch_counts:
                field_mismatch_counts[key + "_mismatch"] += 1
        else:
            #Fall though case
            print("Not implemented condition")
            pass

    if medication_has_difference:
       medication_different_count += 1   

    output = {
        "common_list": common_list,
        "no_match_count": no_match_count,
        "medispan_mismatch": medispan_mismatch,
        "medispan_blank": medispan_blank,
        "missing_in_expected": missing_in_expected,
        "missing_in_actual": missing_in_actual,
        "medication_different_count": medication_different_count,
        **field_mismatch_counts  # Include the field mismatch counts in output
    }

    return output

def compare_symantic_similarity(expected: str, actual : str):
    if expected is None and actual is None:
        return True
    elif expected is None and actual is not None:
        return True
    elif expected is not None and actual is None:
         return False
    else: 
        doc1 = nlp(expected)
        doc2 = nlp(actual)

        similarity = doc1.similarity(doc2)
        return similarity > 0.9

import os
import json

from paperglass.settings import STAGE

from paperglass.domain.model_testing import TestCaseType

from paperglass.log import CustomLogger

LOGGER = CustomLogger(__name__)

def list_test_cases(test_type: TestCaseType):
    try:
        test_cases = []

        module_root = os.path.dirname(__file__)

        target_dir = os.path.join(module_root, STAGE, test_type.value)
        LOGGER.debug("Looking for test cases in %s", target_dir)

        for filename in os.listdir(target_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(target_dir, filename)
                with open(filepath, 'r') as file:
                    data = json.load(file)
                    test_cases.append(data)

        LOGGER.debug("Found %d test cases for test type: %s", len(test_cases), test_type)

        return test_cases
    except FileNotFoundError as e:
        LOGGER.warning("No test cases found for test type: %s", test_type)
        return []
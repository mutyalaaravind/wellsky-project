import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import pytest
import pytest_asyncio

from paperglass.usecases.rules_engine import RulesEngine

from paperglass.domain.values import Rule, RuleSet


@pytest.mark.asyncio
async def test_rules_engine_ok():
    
    config = {
        "rulesets": {
            "file_ingress": {
                "key": "file_ingress",
                "rules": [                    
                    {
                        "name": "basic_rule",
                        "conditions": {
                            "all": [
                                {
                                    # JSONPath support
                                    "path": "$.metadata.tenant",
                                    "operator": "starts_with",
                                    "value": "12"
                                },
                                {
                                    # JSONPath support
                                    "path": "$.metadata.category",
                                    "operator": "regex_match",
                                    "value": "^med.*$"
                                }
                            ]
                        },
                        "extra": {
                            "actions": [
                                {
                                    "id": "extract",        
                                    "params": {
                                        "queue": "high"
                                    },
                                    "priority": 100
                                },
                                {
                                    "id": "log",        
                                    "params": {
                                    },
                                    "priority": 1
                                }
                            ]
                        }
                    },
                    {
                        "name": "basic_rule",
                        "conditions": {
                            "all": [
                                {
                                    # JSONPath support
                                    "path": "$.metadata.tenant",
                                    "operator": "starts_with",
                                    "value": "12"
                                },
                                {
                                    # JSONPath support
                                    "path": "$.metadata.category",
                                    "operator": "regex_match",
                                    "value": "^med.*$"
                                }
                            ]
                        },
                        "extra": {
                            "actions": [
                                {
                                    "id": "extract",        
                                    "params": {
                                        "queue": "default"
                                    },
                                    "priority": 10
                                }
                            ]
                        }
                    },
                ],
                "default_actions": [
                    {
                        "id": "extract",
                        "params": {
                            "queue": "default"
                        },
                        "priority": 1
                    }

                ]
            }
        }
    }

    ruleset_dict = config["rulesets"]["file_ingress"]
    

    obj = {
        "bucket": "sample-bucket",
        "contentType": "text/plain",
        "crc32c": "rTVTeQ==",
        "etag": "CNHZkbuF/ugCEAE=",
        "generation": "1587627537231057",
        "id": "sample-bucket/folder/Test.cs/1587627537231057",
        "kind": "storage#object",
        "md5Hash": "kF8MuJ5+CTJxvyhHS1xzRg==",
        "mediaLink": "https://www.googleapis.com/download/storage/v1/b/sample-bucket/o/folder%2FTest.cs?generation=1587627537231057\u0026alt=media",
        "metageneration": "1",
        "metadata": {
            "category": "medprofile",
            "tenant": "123456"
        },
        "name": "folder/Test.cs",
        "selfLink": "https://www.googleapis.com/storage/v1/b/sample-bucket/o/folder/Test.cs",
        "size": "352",
        "storageClass": "MULTI_REGIONAL",
        "timeCreated": "2025-01-20T04:30:57.230Z",
        "timeStorageClassUpdated": "2020-04-23T07:38:57.230Z",
        "updated": "2020-04-23T07:38:57.230Z"
    }

    ruleset = RuleSet(**ruleset_dict)

    print("Ruleset: ", ruleset)
    rulesengine = RulesEngine(ruleset)
    results = rulesengine.evaluate(obj)

    print(f"Results: {results}")
    
    extract_action = results["extract"]
    
    assert extract_action["id"] == "extract"
    assert extract_action["params"]["queue"] == "high"
    assert extract_action["priority"] == 100


@pytest.mark.asyncio
async def test_rules_engine_default():
    
    config = {
        "rulesets": {
            "file_ingress": {
                "key": "file_ingress",
                "rules": [                    
                    {
                        "name": "basic_rule",
                        "conditions": {
                            "all": [
                                {
                                    # JSONPath support
                                    "path": "$.metadata.tenant",
                                    "operator": "starts_with",
                                    "value": "12"
                                },
                                {
                                    # JSONPath support
                                    "path": "$.metadata.category",
                                    "operator": "regex_match",
                                    "value": "^xmed.*$"
                                }
                            ]
                        },
                        "extra": {
                            "actions": [
                                {
                                    "id": "extract",        
                                    "params": {
                                        "queue": "high"
                                    },
                                    "priority": 100
                                },
                                {
                                    "id": "log",        
                                    "params": {
                                    },
                                    "priority": 1
                                }
                            ]
                        }
                    },
                    {
                        "name": "basic_rule",
                        "conditions": {
                            "all": [
                                {
                                    # JSONPath support
                                    "path": "$.metadata.tenant",
                                    "operator": "starts_with",
                                    "value": "12"
                                },
                                {
                                    # JSONPath support
                                    "path": "$.metadata.category",
                                    "operator": "regex_match",
                                    "value": "^med.*$"
                                }
                            ]
                        },
                        "extra": {
                            "actions": [
                                {
                                    "id": "extract",        
                                    "params": {
                                        "queue": "low"
                                    },
                                    "priority": 1
                                }
                            ]
                        }
                    },
                ],
                "default_actions": [
                    {
                        "id": "extract",
                        "params": {
                            "queue": "default"
                        },
                        "priority": 1
                    }

                ]
            }
        }
    }

    ruleset_dict = config["rulesets"]["file_ingress"]
    

    obj = {
        "bucket": "sample-bucket",
        "contentType": "text/plain",
        "crc32c": "rTVTeQ==",
        "etag": "CNHZkbuF/ugCEAE=",
        "generation": "1587627537231057",
        "id": "sample-bucket/folder/Test.cs/1587627537231057",
        "kind": "storage#object",
        "md5Hash": "kF8MuJ5+CTJxvyhHS1xzRg==",
        "mediaLink": "https://www.googleapis.com/download/storage/v1/b/sample-bucket/o/folder%2FTest.cs?generation=1587627537231057\u0026alt=media",
        "metageneration": "1",
        "metadata": {
            "category": "medprofile",
            "tenant": "123456"
        },
        "name": "folder/Test.cs",
        "selfLink": "https://www.googleapis.com/storage/v1/b/sample-bucket/o/folder/Test.cs",
        "size": "352",
        "storageClass": "MULTI_REGIONAL",
        "timeCreated": "2025-01-20T04:30:57.230Z",
        "timeStorageClassUpdated": "2020-04-23T07:38:57.230Z",
        "updated": "2020-04-23T07:38:57.230Z"
    }

    ruleset = RuleSet(**ruleset_dict)

    print("Ruleset: ", ruleset)
    rulesengine = RulesEngine(ruleset)
    results = rulesengine.evaluate(obj)

    print(f"Results: {results}")
    
    extract_action = results["extract"]
    
    assert extract_action["id"] == "extract"
    assert extract_action["params"]["queue"] == "low"
    assert extract_action["priority"] == 1

@pytest.mark.asyncio
async def test_rules_engine_competitionwithdefault():

    # Checks that if the same action type is in default and in a positive rule with the same priority, the positive rule wins
    
    config = {
        "rulesets": {
            "file_ingress": {
                "key": "file_ingress",
                "rules": [                    
                    {
                        "name": "basic_rule",
                        "conditions": {
                            "all": [
                                {
                                    # JSONPath support
                                    "path": "$.metadata.tenant",
                                    "operator": "starts_with",
                                    "value": "12"
                                },
                                {
                                    # JSONPath support
                                    "path": "$.metadata.category",
                                    "operator": "regex_match",
                                    "value": "^med.*$"
                                }
                            ]
                        },
                        "extra": {
                            "actions": [
                                {
                                    "id": "extract",        
                                    "params": {
                                        "queue": "high"
                                    },
                                    "priority": 100
                                },
                            ]
                        }
                    },
                    {
                        "name": "basic_rule",
                        "conditions": {
                            "all": [
                                {
                                    # JSONPath support
                                    "path": "$.metadata.tenant",
                                    "operator": "starts_with",
                                    "value": "12"
                                },
                                {
                                    # JSONPath support
                                    "path": "$.metadata.category",
                                    "operator": "regex_match",
                                    "value": "^xmed.*$"
                                }
                            ]
                        },
                        "extra": {
                            "actions": [
                                {
                                    "id": "extract",        
                                    "params": {
                                        "queue": "low"
                                    },
                                    "priority": 1
                                }
                            ]
                        }
                    },
                ],
                "default_actions": [
                    {
                        "id": "extract",
                        "params": {
                            "queue": "default"
                        },
                        "priority": 100
                    }

                ]
            }
        }
    }

    ruleset_dict = config["rulesets"]["file_ingress"]
    

    obj = {
        "bucket": "sample-bucket",
        "contentType": "text/plain",
        "crc32c": "rTVTeQ==",
        "etag": "CNHZkbuF/ugCEAE=",
        "generation": "1587627537231057",
        "id": "sample-bucket/folder/Test.cs/1587627537231057",
        "kind": "storage#object",
        "md5Hash": "kF8MuJ5+CTJxvyhHS1xzRg==",
        "mediaLink": "https://www.googleapis.com/download/storage/v1/b/sample-bucket/o/folder%2FTest.cs?generation=1587627537231057\u0026alt=media",
        "metageneration": "1",
        "metadata": {
            "category": "medprofile",
            "tenant": "123456"
        },
        "name": "folder/Test.cs",
        "selfLink": "https://www.googleapis.com/storage/v1/b/sample-bucket/o/folder/Test.cs",
        "size": "352",
        "storageClass": "MULTI_REGIONAL",
        "timeCreated": "2025-01-20T04:30:57.230Z",
        "timeStorageClassUpdated": "2020-04-23T07:38:57.230Z",
        "updated": "2020-04-23T07:38:57.230Z"
    }

    ruleset = RuleSet(**ruleset_dict)

    print("Ruleset: ", ruleset)
    rulesengine = RulesEngine(ruleset)
    results = rulesengine.evaluate(obj)

    print(f"Results: {results}")
    
    extract_action = results["extract"]
    
    assert extract_action["id"] == "extract"
    assert extract_action["params"]["queue"] == "high"
    assert extract_action["priority"] == 100

@pytest.mark.asyncio
async def test_rules_engine_norules():

    # ANARCHY! No rules, no actions, no mercy!  Ok, well no rules, then the output will be the default actions.
    
    config = {
        "rulesets": {
            "file_ingress": {
                "key": "file_ingress",
                "rules": [],
                "default_actions": [
                    {
                        "id": "extract",
                        "params": {
                            "queue": "default"
                        },
                        "priority": 1
                    }

                ]
            }
        }
    }

    ruleset_dict = config["rulesets"]["file_ingress"]
    

    obj = {
        "bucket": "sample-bucket",
        "contentType": "text/plain",
        "crc32c": "rTVTeQ==",
        "etag": "CNHZkbuF/ugCEAE=",
        "generation": "1587627537231057",
        "id": "sample-bucket/folder/Test.cs/1587627537231057",
        "kind": "storage#object",
        "md5Hash": "kF8MuJ5+CTJxvyhHS1xzRg==",
        "mediaLink": "https://www.googleapis.com/download/storage/v1/b/sample-bucket/o/folder%2FTest.cs?generation=1587627537231057\u0026alt=media",
        "metageneration": "1",
        "metadata": {
            "category": "medprofile",
            "tenant": "123456"
        },
        "name": "folder/Test.cs",
        "selfLink": "https://www.googleapis.com/storage/v1/b/sample-bucket/o/folder/Test.cs",
        "size": "352",
        "storageClass": "MULTI_REGIONAL",
        "timeCreated": "2025-01-20T04:30:57.230Z",
        "timeStorageClassUpdated": "2020-04-23T07:38:57.230Z",
        "updated": "2020-04-23T07:38:57.230Z"
    }

    ruleset = RuleSet(**ruleset_dict)

    print("Ruleset: ", ruleset)
    rulesengine = RulesEngine(ruleset)
    results = rulesengine.evaluate(obj)

    print(f"Results: {results}")
    
    extract_action = results["extract"]
    
    assert extract_action["id"] == "extract"
    assert extract_action["params"]["queue"] == "default"
    assert extract_action["priority"] == 1
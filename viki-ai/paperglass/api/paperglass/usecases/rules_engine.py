from python_rule_engine import RuleEngine, Operator
import json
import re
from datetime import datetime, timezone, timedelta

from paperglass.domain.values import RuleSet

from paperglass.log import getLogger, labels, CustomLogger
LOGGER = CustomLogger(__name__)


class RulesEngine:

    #Native operators:
        # Equal	                    "equal"	                    Compares if the value of the object is equal to the value of the condition.
        # Not Equal	                "not_equal"	                Compares if the value of the object is not equal to the value of the condition.
        # Greater Than	            "greater_than"	            Compares if the value of the object is greater than the value of the condition.
        # Greater Than Inclusive	"greater_than_inclusive"	Compares if the value of the object is greater than or equal to the value of the condition.
        # Less Than	                "less_than"	                Compares if the value of the object is less than the value of the condition.
        # Less Than Inclusive	    "less_than_inclusive"	    Compares if the value of the object is less than or equal to the value of the condition.
        # In	                    "in"	                    Compares if the value of the object is in the value of the condition.
        # Not In	                "not_in"	                Compares if the value of the object is not in the value of the condition.
        # Contains	                "contains"	                Compares if the value of the object contains the value of the condition.
        # Not Contains	            "not_contains"	            Compares if the value of the object does not contain the value of the condition.   

    # Custom operators
    class StartsWith(Operator):
        id = "starts_with"

        def match(self, obj_value):
            return obj_value.startswith(self.condition.value), obj_value

    class RegexMatch(Operator):
        id = "regex_match"

        def match(self, obj_value):
            regexp = re.compile(self.condition.value)
            return regexp.search(obj_value), obj_value

    class TimeFreshness(Operator):
        id = "time_freshness"

        def match(self, obj_value):

            #print(json.dumps(self.condition.params, indent=2))

            dte = obj_value
            if dte.endswith("Z"):
                dte = dte.replace("Z", "+00:00") 

            obj_date = datetime.fromisoformat(dte)

            now = datetime.now(timezone.utc)
            delta = None
            if isinstance(self.condition.value, int):            
                delta = timedelta(minutes=self.condition.value)
            elif isinstance(self.condition.value, str):
                if self.condition.value.endswith("d"):
                    clean = self.condition.value.replace("d", "")
                    delta = timedelta(days=int(clean))
                elif self.condition.value.endswith("h"):
                    clean = self.condition.value.replace("h", "")
                    delta = timedelta(hours=int(clean))
                else:
                    clean = self.condition.value.replace("m", "")
                    delta = timedelta(minutes=int(clean))

            difference = now - obj_date

            #print(f"delta: {delta} difference: {difference}")
            return delta >= difference, obj_value


    def __init__(self, ruleset: RuleSet):
        if isinstance(ruleset, dict):
            ruleset = RuleSet(**ruleset)
            
        self.rules = ruleset.rules
        self.default_actions = ruleset.default_actions
        self.engine = RuleEngine([x.dict() for x in self.rules], operators=[self.StartsWith, self.RegexMatch, self.TimeFreshness])   
    
    def evaluate(self, obj):
        results = self.engine.evaluate(obj)
        all_actions = []

        for item in results:
            extra = item.extra
            actions = extra.get("actions", [])

            if actions:
                all_actions.extend(actions)

        action_map = self.coelesce_actions(all_actions)

        return action_map

    def coelesce_actions(self, actions):
        
        merged_actions = []
        if actions:
            merged_actions.extend(actions)
        if self.default_actions:
            merged_actions.extend([x.dict() for x in self.default_actions])        

        action_map = {}
        for action in merged_actions:            
            if action["id"] in action_map:
                if action["priority"] > action_map[action["id"]]["priority"]:
                    action_map[action["id"]] = action
            else:
                action_map[action["id"]] = action

        return action_map



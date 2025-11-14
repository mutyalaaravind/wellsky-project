from paperglass.settings import (
    QUEUE_RESOLVER_VERSION,
    CLOUDTASK_REGISTERED_APP_IDS,
    CLOUD_TASK_QUEUE_NAME,
    CLOUD_TASK_QUEUE_NAME_PRIORITY,
    CLOUD_TASK_QUEUE_NAME_QUARANTINE,
    CLOUD_TASK_QUEUE_NAME_2,
    CLOUD_TASK_QUEUE_NAME_PRIORITY_2,
    CLOUD_TASK_QUEUE_NAME_QUARANTINE_2,
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME,
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_PRIORITY,    
    MEDICATION_EXTRACTION_V4_API_DEFAULT_URL,
    MEDICATION_EXTRACTION_V4_API_HIGH_URL,
    MEDICATION_EXTRACTION_V4_API_QUARANTINE_URL,
    MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_QUARANTINE
)
from paperglass.domain.values import OrchestrationPriority
from pydantic import BaseModel

from paperglass.log import getLogger, CustomLogger
LOGGER = CustomLogger(__name__)

class QueueValue(BaseModel):
    queue_name:str
    priority:str
    api_url: str

class QueueResolver():
    def __init__(self):        
        self.rules = {
            "DEFAULT": {
                OrchestrationPriority.DEFAULT.value: CLOUD_TASK_QUEUE_NAME_2,
                OrchestrationPriority.HIGH.value: CLOUD_TASK_QUEUE_NAME_PRIORITY_2,
                OrchestrationPriority.QUARANTINE.value: CLOUD_TASK_QUEUE_NAME_QUARANTINE_2   
            },
            "page_classification": {
                OrchestrationPriority.DEFAULT.value: CLOUD_TASK_QUEUE_NAME_2,
                OrchestrationPriority.HIGH.value: CLOUD_TASK_QUEUE_NAME_PRIORITY_2,
                OrchestrationPriority.QUARANTINE.value: CLOUD_TASK_QUEUE_NAME_QUARANTINE_2              
            },
            "page_ocr": {
                OrchestrationPriority.DEFAULT.value: CLOUD_TASK_QUEUE_NAME_2,
                OrchestrationPriority.HIGH.value: CLOUD_TASK_QUEUE_NAME_PRIORITY_2,
                OrchestrationPriority.QUARANTINE.value: CLOUD_TASK_QUEUE_NAME_QUARANTINE_2              
            },
            "medication_extraction": {
                OrchestrationPriority.DEFAULT.value: CLOUD_TASK_QUEUE_NAME,
                OrchestrationPriority.HIGH.value: CLOUD_TASK_QUEUE_NAME_PRIORITY,
                OrchestrationPriority.QUARANTINE.value: CLOUD_TASK_QUEUE_NAME_QUARANTINE                            
            },
            "conditions_extraction": {
                OrchestrationPriority.DEFAULT.value: CLOUD_TASK_QUEUE_NAME,
                OrchestrationPriority.HIGH.value: CLOUD_TASK_QUEUE_NAME_PRIORITY,
                OrchestrationPriority.QUARANTINE.value: CLOUD_TASK_QUEUE_NAME_QUARANTINE                            
            },
            "allergies_extraction": {
                OrchestrationPriority.DEFAULT.value: CLOUD_TASK_QUEUE_NAME,
                OrchestrationPriority.HIGH.value: CLOUD_TASK_QUEUE_NAME_PRIORITY,
                OrchestrationPriority.QUARANTINE.value: CLOUD_TASK_QUEUE_NAME_QUARANTINE                           
            },
            "immunizations_extraction": {
                OrchestrationPriority.DEFAULT.value: CLOUD_TASK_QUEUE_NAME,
                OrchestrationPriority.HIGH.value: CLOUD_TASK_QUEUE_NAME_PRIORITY ,
                OrchestrationPriority.QUARANTINE.value: CLOUD_TASK_QUEUE_NAME_QUARANTINE                             
            },
            "v4_extraction": {
                OrchestrationPriority.DEFAULT.value: MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME,
                OrchestrationPriority.HIGH.value: MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_PRIORITY,
                OrchestrationPriority.QUARANTINE.value: CLOUD_TASK_QUEUE_NAME_QUARANTINE
            }
        }

        self.queue_api_mappings = {
            "DEFAULT": {
                OrchestrationPriority.DEFAULT.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME_2, priority=OrchestrationPriority.DEFAULT.value, api_url=MEDICATION_EXTRACTION_V4_API_DEFAULT_URL),
                OrchestrationPriority.HIGH.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME_PRIORITY_2, priority=OrchestrationPriority.HIGH.value, api_url=MEDICATION_EXTRACTION_V4_API_HIGH_URL),
                OrchestrationPriority.QUARANTINE.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME_QUARANTINE_2, priority=OrchestrationPriority.QUARANTINE.value, api_url=MEDICATION_EXTRACTION_V4_API_QUARANTINE_URL)
            },
            "page_classification": {
                OrchestrationPriority.DEFAULT.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME_2, priority=OrchestrationPriority.DEFAULT.value, api_url=MEDICATION_EXTRACTION_V4_API_DEFAULT_URL),
                OrchestrationPriority.HIGH.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME_PRIORITY_2, priority=OrchestrationPriority.HIGH.value, api_url=MEDICATION_EXTRACTION_V4_API_HIGH_URL),
                OrchestrationPriority.QUARANTINE.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME_QUARANTINE_2, priority=OrchestrationPriority.QUARANTINE.value, api_url=MEDICATION_EXTRACTION_V4_API_QUARANTINE_URL)
            },
            "medication_extraction": {
                OrchestrationPriority.DEFAULT.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME, priority=OrchestrationPriority.DEFAULT.value, api_url=MEDICATION_EXTRACTION_V4_API_DEFAULT_URL),
                OrchestrationPriority.HIGH.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME_PRIORITY, priority=OrchestrationPriority.HIGH.value, api_url=MEDICATION_EXTRACTION_V4_API_HIGH_URL),
                OrchestrationPriority.QUARANTINE.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME_QUARANTINE, priority=OrchestrationPriority.QUARANTINE.value, api_url=MEDICATION_EXTRACTION_V4_API_QUARANTINE_URL)
            },
            "conditions_extraction": {
                OrchestrationPriority.DEFAULT.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME, priority=OrchestrationPriority.DEFAULT.value, api_url=MEDICATION_EXTRACTION_V4_API_DEFAULT_URL),
                OrchestrationPriority.HIGH.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME_PRIORITY, priority=OrchestrationPriority.HIGH.value, api_url=MEDICATION_EXTRACTION_V4_API_HIGH_URL),
                OrchestrationPriority.QUARANTINE.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME_QUARANTINE, priority=OrchestrationPriority.QUARANTINE.value, api_url=MEDICATION_EXTRACTION_V4_API_QUARANTINE_URL)
            },
            "allergies_extraction": {
                OrchestrationPriority.DEFAULT.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME, priority=OrchestrationPriority.DEFAULT.value, api_url=MEDICATION_EXTRACTION_V4_API_DEFAULT_URL),
                OrchestrationPriority.HIGH.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME_PRIORITY, priority=OrchestrationPriority.HIGH.value, api_url=MEDICATION_EXTRACTION_V4_API_HIGH_URL),
                OrchestrationPriority.QUARANTINE.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME_QUARANTINE, priority=OrchestrationPriority.QUARANTINE.value, api_url=MEDICATION_EXTRACTION_V4_API_QUARANTINE_URL)
            },
            "immunizations_extraction": {
                OrchestrationPriority.DEFAULT.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME, priority=OrchestrationPriority.DEFAULT.value, api_url=MEDICATION_EXTRACTION_V4_API_DEFAULT_URL),
                OrchestrationPriority.HIGH.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME_PRIORITY, priority=OrchestrationPriority.HIGH.value, api_url=MEDICATION_EXTRACTION_V4_API_HIGH_URL),
                OrchestrationPriority.QUARANTINE.value: QueueValue(queue_name=CLOUD_TASK_QUEUE_NAME_QUARANTINE, priority=OrchestrationPriority.QUARANTINE.value, api_url=MEDICATION_EXTRACTION_V4_API_QUARANTINE_URL)
            },
            "v4_extraction": {
                OrchestrationPriority.DEFAULT.value: QueueValue(queue_name=MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME, priority=OrchestrationPriority.DEFAULT.value, api_url=MEDICATION_EXTRACTION_V4_API_DEFAULT_URL),
                OrchestrationPriority.HIGH.value: QueueValue(queue_name=MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_PRIORITY, priority=OrchestrationPriority.HIGH.value, api_url=MEDICATION_EXTRACTION_V4_API_HIGH_URL),
                OrchestrationPriority.QUARANTINE.value: QueueValue(queue_name=MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_QUARANTINE, priority=OrchestrationPriority.QUARANTINE.value, api_url=MEDICATION_EXTRACTION_V4_API_QUARANTINE_URL)
            }
        }

    def resolve_queue_name(self, category: str, priority: str) -> str:
        LOGGER.debug("Resolving queue name for category: %s, priority: %s", category, priority)
        if category not in self.rules:
            LOGGER.warning(f"Category {category} not found in QueueResolver rules, using global default queue: self.default_queue_name")
            return self.get_queue_from_category(self.rules["DEFAULT"], priority)
        
        cat_rules = self.rules[category]
        return self.get_queue_from_category(cat_rules, priority)
    
    def resolve_queue_value(self, category: str, priority: str) -> QueueValue:
        LOGGER.debug("Resolving queue name and api url for category: %s, priority: %s", category, priority)
        if category not in self.queue_api_mappings:
            LOGGER.warning(f"Category {category} not found in QueueResolver rules, using global default queue: self.default_queue_name")
            return self.get_queue_from_category(self.queue_api_mappings["DEFAULT"], priority)
        
        cat_rules = self.queue_api_mappings[category]
        
        if priority not in cat_rules:
            if OrchestrationPriority.DEFAULT.value not in cat_rules:
                LOGGER.warning(f"Priority {priority} not found in category rules for a category, using global default queue: self.default_queue_name")
                return self.rules["DEFAULT"][OrchestrationPriority.DEFAULT.value]
            else:
                return cat_rules[OrchestrationPriority.DEFAULT.value]
        else:
            return cat_rules[priority]
        #return self.get_queue_from_category(cat_rules, priority)
    
        

    def get_queue_from_category(self, category_rule, priority):
        if priority not in category_rule:
            if OrchestrationPriority.DEFAULT.value not in category_rule:
                LOGGER.warning(f"Priority {priority} not found in category rules for a category, using global default queue: self.default_queue_name")
                return self.rules["DEFAULT"][OrchestrationPriority.DEFAULT.value]
            else:
                return category_rule[OrchestrationPriority.DEFAULT.value]
        else:
            return category_rule[priority]


class QueueResolverV2():
    def __init__(self, app_id: str):
        
        if app_id not in CLOUDTASK_REGISTERED_APP_IDS:
            LOGGER.warning("App ID %s not registered in CLOUDTASK_REGISTERED_APP_IDS, using default app_id 'default' for resolving cloud task queues", app_id)
            self.app_id = "default"
        else:
            self.app_id = app_id

        self.entrypoint_name_template = "v4-extraction-entrypoint-dev-{app_id}-{priority}-queue"

        self.queue_name_templates = {
            "DEFAULT": "paperglass-classification-{app_id}-{priority}-queue",
            "page_classification": "paperglass-classification-{app_id}-{priority}-queue",
            "page_ocr": "paperglass-classification-{app_id}-{priority}-queue",
            "medication_extraction": "paperglass-extraction-{app_id}-{priority}-queue",
            "conditions_extraction": "paperglass-extraction-{app_id}-{priority}-queue",
            "allergies_extraction": "paperglass-extraction-{app_id}-{priority}-queue",
            "immunizations_extraction": "paperglass-extraction-{app_id}-{priority}-queue",
            "v4_extraction": "v4-extraction-entrypoint-{app_id}-{priority}-queue"
        }

        self.queue_api_mappings = {
            "v4_extraction": {
                OrchestrationPriority.DEFAULT.value: MEDICATION_EXTRACTION_V4_API_DEFAULT_URL,
                OrchestrationPriority.HIGH.value: MEDICATION_EXTRACTION_V4_API_HIGH_URL,
                OrchestrationPriority.QUARANTINE.value: MEDICATION_EXTRACTION_V4_API_QUARANTINE_URL
            }
        }

    def resolve_queue_name(self, category: str, priority: str) -> str:
        if isinstance(priority, OrchestrationPriority):
            priority = priority.value

        template = self.queue_name_templates.get(category, self.queue_name_templates["DEFAULT"])
        name = template.format(app_id=self.app_id, priority=priority)

        LOGGER.debug("Resolved queue name for category: %s, priority: %s, queue_name: %s", category, priority, name, extra={
            "app_id": self.app_id,
            "category": category,
            "priority": priority,
            "queue_name": name            
        })
        return name      


    def resolve_queue_value(self, category: str, priority: str) -> QueueValue:
        name = self.resolve_queue_name(category=category, priority=priority)
        priority_value = OrchestrationPriority(priority).value
        api_url = self.queue_api_mappings.get(category, {}).get(priority_value, MEDICATION_EXTRACTION_V4_API_DEFAULT_URL)
        LOGGER.debug("Resolved queue value for category: %s, priority: %s, queue_name: %s, api_url: %s", category, priority, name, api_url, extra={
            "app_id": self.app_id,
            "category": category,
            "priority": priority,
            "queue_name": name,
            "api_url": api_url  
        })
        return QueueValue(queue_name=name, priority=priority_value, api_url=api_url)

def get_queue_resolver(app_id: str = None) -> QueueResolver:
    if app_id is None:
        LOGGER.warning("No app_id provided, using default QueueResolver")
        return QueueResolver()
    
    if QUEUE_RESOLVER_VERSION == "v2":
        return QueueResolverV2(app_id)
    else:
        return QueueResolver()

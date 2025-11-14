"""
Config Firestore Adapter for Admin API.

This adapter provides access to configuration data stored in Firestore
with caching to optimize performance for frequently accessed config.
"""

import os
from typing import Dict, Any
import aiocache
from google.cloud import firestore
from viki_shared.utils.logger import getLogger
from settings import Settings
from contracts.config_contracts import ConfigPort
from models.config import Configuration, ModelConfig, OnboardingConfiguration, OnboardingOperationConfig
from model_aggregates.system_config import SystemConfig

logger = getLogger(__name__)


class ConfigAdapter(ConfigPort):
    """Firestore adapter for configuration data with caching."""
    
    def __init__(self, settings: Settings):
        """
        Initialize the config adapter.
        
        Args:
            settings: Application settings containing Firestore configuration
        """
        logger.info("🔧 Initializing Config adapter")
        self.settings = settings
        self.collection_name = "config"
        
        # Initialize Firestore client
        emulator_host = os.getenv("FIRESTORE_EMULATOR_HOST")
        if emulator_host:
            # When using emulator, use the emulator project ID
            emulator_project = "google-cloud-firestore-emulator"
            logger.info(f"🔧 Using Firestore EMULATOR at {emulator_host}, project: {emulator_project}")
            self.client = firestore.Client(project=emulator_project)
        else:
            logger.info(f"🔧 Using PRODUCTION Firestore - Project: {settings.GCP_PROJECT_ID}, Database: {settings.GCP_FIRESTORE_DB}")
            self.client = firestore.Client(
                project=settings.GCP_PROJECT_ID, 
                database=settings.GCP_FIRESTORE_DB
            )
        logger.info("🔧 Config adapter initialized successfully")
    
    @aiocache.cached()
    async def get_config(self) -> SystemConfig:
        """
        Get the admin configuration from Firestore with caching.
        
        This method is cached to optimize performance since config is accessed frequently
        but changes rarely.
        
        Returns:
            SystemConfig: The configuration aggregate from Firestore
        """
        try:
            logger.debug("🔧 Fetching config from Firestore")
            doc_ref = self.client.collection(self.collection_name).document("admin_config")
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.warning("🔧 Config document not found, returning default config")
                return self._get_default_config()
            
            config_data = doc.to_dict()
            logger.info("🔧 Successfully retrieved config from Firestore")
            return SystemConfig(**config_data)
            
        except Exception as e:
            logger.error(f"🔧 Error fetching config from Firestore: {str(e)}")
            logger.warning("🔧 Falling back to default config")
            return self._get_default_config()
    
    def _get_default_config(self) -> SystemConfig:
        """
        Get default configuration structure.
        
        Returns:
            SystemConfig: Default configuration matching the required structure
        """
        # Create default model configs
        schema_model_config = ModelConfig(
            model="gemini-2.5-pro",
            max_output_tokens=8192,
            temperature=0.0
        )
        
        prompt_model_config = ModelConfig(
            model="gemini-2.5-pro", 
            max_output_tokens=8192,
            temperature=0.0
        )
        
        test_model_config = ModelConfig(
            model="gemini-2.5-flash-lite",
            max_output_tokens=8192,
            temperature=0.0
        )
        
        # Create operation configs
        schema_op_config = OnboardingOperationConfig(llm_config=schema_model_config)
        prompt_op_config = OnboardingOperationConfig(llm_config=prompt_model_config)
        test_op_config = OnboardingOperationConfig(llm_config=test_model_config)
        
        # Create onboarding configuration
        onboarding_config = OnboardingConfiguration(
            schema_generation=schema_op_config,
            prompt_generation=prompt_op_config,
            test_extraction=test_op_config
        )
        
        # Create root configuration
        config = Configuration(onboarding=onboarding_config)
        
        # Return SystemConfig aggregate
        return SystemConfig(
            id="admin_config",
            config=config,
            active=True
        )
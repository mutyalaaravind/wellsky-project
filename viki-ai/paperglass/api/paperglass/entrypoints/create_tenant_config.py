import asyncio
import datetime
import json
import sys,os
import time
from typing import Dict
import uuid


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.domain.models import AppTenantConfig
from paperglass.usecases.configuration import get_config
from paperglass.usecases.commands import CreateTenantConfiguration
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.domain.values import Configuration
from paperglass.infrastructure.ports import IQueryPort

from kink import inject


@inject()
async def create_tenant_config(tenant_id:str,app_id_of_config_to_copy:str,query:IQueryPort, commands:ICommandHandlingPort) -> 'AppTenantConfig':
    config:Configuration = await get_config(app_id_of_config_to_copy,tenant_id,query)
    tenant_config:AppTenantConfig = await query.get_app_tenant_config(app_id_of_config_to_copy, tenant_id)
    
    
    
    if not tenant_config:
        config:Configuration = await query.get_app_config(app_id_of_config_to_copy)
        await commands.handle_command(CreateTenantConfiguration(
            app_id = app_id_of_config_to_copy,
            tenant_id=tenant_id,
            config=config
        ))
    else:
        if tenant_config.tenant_id == tenant_id:
            raise ValueError(f"Tenant Configuration already exists for tenant {tenant_id} and app {app_id_of_config_to_copy}")
        
if __name__ == '__main__':
    args = sys.argv
    
    asyncio.run(create_tenant_config('54321','007'))
    
#!/usr/bin/env python3

import sys
import os
import asyncio
import argparse

# Add paperglass to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.log import getLogger
from paperglass.domain.utils.auth_utils import get_token
from paperglass.interface.adapters.rest import RestAdapter
from starlette.requests import Request
from starlette.datastructures import Headers, QueryParams

LOGGER = getLogger(__name__)

async def assess_documents(window_minutes: float):
    """Assess document processing times"""
    try:
        # Create REST adapter
        adapter = RestAdapter()
        
        # Get auth token
        token = get_token("007", "54321", "29437dd24ffe465eb611a61b0b62f608")
        
        # Create request scope with headers
        scope = {
            'type': 'http',
            'method': 'GET',
            'path': '/documents/assessment',
            'headers': [
                (b'authorization', f'Bearer {token}'.encode()),
                (b'content-type', b'application/json')
            ],
            'query_string': f'accepted_window_minutes={window_minutes}'.encode()
        }
        
        # Create request with proper scope
        request = Request(scope)
        
        # Add required request attributes
        request.scope['app_id'] = "007"
        request.scope['tenant_id'] = "54321"
        request.scope['patient_id'] = "29437dd24ffe465eb611a61b0b62f608"
        request.scope['token'] = token
        
        # Call assess_documents method
        result = await adapter.assess_documents(request)
        
        if not result:
            print("No assessment results found.")
            return
            
        print("\nDocument Processing Assessment")
        print(f"Accepted Window: {window_minutes} minutes")
        print("-" * 80)
        print(result)

    except Exception as e:
        LOGGER.error(f"Error assessing documents: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Assess document processing times')
    parser.add_argument('--window', type=float, default=30,
                      help='Accepted processing window in minutes (default: 30)')
    args = parser.parse_args()

    asyncio.run(assess_documents(args.window))

if __name__ == '__main__':
    main()

# """
# This module tells injector how to map driving ports to use cases.
# Importing the classes makes them register as injectable.
# """
# from kink import di

# from ..settings import MEDISPAN_FILTER_STRATEGY
# from ..domain.values import FilterStrategy

# from .adapters.medispan_api_search_filter import MedispanAPISearchFilterAdapter
# from .adapters.medispan_llm_filter import MedispanLLMFilterAdapter

# from .ports import IRelevancyFilterPort

# from ..log import getLogger
# LOGGER = getLogger(__name__)

# if MEDISPAN_FILTER_STRATEGY == FilterStrategy.LLM:
#     di[IRelevancyFilterPort] = lambda di: MedispanLLMFilterAdapter()
# elif MEDISPAN_FILTER_STRATEGY == FilterStrategy.LOGIC:
#     di[IRelevancyFilterPort] = lambda di: MedispanAPISearchFilterAdapter()
# else:
#     raise ValueError(f"Invalid Medispan filter strategy: {MEDISPAN_FILTER_STRATEGY}")

from kink import inject
from pydantic import ValidationError

from paperglass.settings import (
    SELF_API,
    GCP_LOCATION_2,
    CLOUD_PROVIDER,
    CLOUD_TASK_COMMAND_QUEUE_NAME,
    SERVICE_ACCOUNT_EMAIL,
    FEATUREFLAG_COMMAND_OUTOFBAND_CLOUDTASK_ENABLED
)

from paperglass.domain.utils.exception_utils import exceptionToMap

from paperglass.usecases.commands import (
    Command,
    AppBaseCommand,
)

from paperglass.infrastructure.ports import (
    IUnitOfWork,
    ICloudTaskPort,
)


from paperglass.log import labels, CustomLogger
LOGGER = CustomLogger(__name__)


@inject
async def create_command(command: Command, uow: IUnitOfWork):
    if FEATUREFLAG_COMMAND_OUTOFBAND_CLOUDTASK_ENABLED:
        if CLOUD_PROVIDER == "local":
            LOGGER.debug("create_command: FEATUREFLAG_COMMAND_OUTOFBAND_CLOUDTASK_ENABLED is enabled but running locally.  Calling Command Handler directly", extra=command.toExtra())
            from paperglass.interface.ports import ICommandHandlingPort

            @inject
            async def create_command_local(command: Command, commands: ICommandHandlingPort):
                LOGGER.debug("create_command: Calling command handler directly", extra=command.toExtra())
                return await commands.handle_command(command)
            
            await create_command_local(command)

        else:
            LOGGER.debug("create_command: FEATUREFLAG_COMMAND_OUTOFBAND_CLOUDTASK_ENABLED is enabled.  Scheduling command via CloudTask", extra=command.toExtra())
            await create_command_cloudtask(command, uow)
    else:
        LOGGER.debug("create_command: FEATUREFLAG_COMMAND_OUTOFBAND_CLOUDTASK_ENABLED is disabled.  Scheduling command via UOW", extra=command.toExtra())
        uow.create_command(command)

@inject
async def create_command_cloudtask(command: Command, uow: IUnitOfWork, cloud_task: ICloudTaskPort):
    extra = command.toExtra()
    
    LOGGER.debug("create_command_cloudtask: Scheduling command", extra=extra)

    # Construct URL to start command
    url = f"{SELF_API}/command"
    body = {
        "type": command.__class__.__name__,
        "command": command.dict()
    }
    location = GCP_LOCATION_2
    queue = CLOUD_TASK_COMMAND_QUEUE_NAME
    service_account_email = SERVICE_ACCOUNT_EMAIL
    payload = body

    token = None
    if isinstance(command, AppBaseCommand):
        token = command.token
    else:
        LOGGER.warning("Command to be queued is not of type AppBaseCommand.  No token will be added to the CloudTask")

    extra.update({
        "cloudtask": {
            "url": url,
            "queue": queue,
            "service_account_email": service_account_email,
            "payload": payload,
        }
    })

    try:
        LOGGER.debug("Starting a cloud run task (v2), location: %s, service_account_email: %s, queue: %s, url: %s, payload: %s", location, service_account_email, queue, url, payload, extra=extra)
        response = await cloud_task.create_task_v2(location=location,
                                                        service_account_email=service_account_email,
                                                        queue=queue,
                                                        url=url,
                                                        payload=payload,
                                                        token=token,
                                                        schedule_time=None)
        extra.update({
            "response": response
        })
        LOGGER.debug("Successfully started a command cloud run task: location: %s, service_account_email: %s, queue: %s, url: %s, payload: %s, response: %s", location, service_account_email, queue, url, payload, response, extra=extra)

        return response
    except ValidationError as e:
        extra["error"] = exceptionToMap(e)
        LOGGER.error("ValidationException when starting a command cloud run task: location: %s, service_account_email: %s, queue: %s, url: %s, payload: %s", location, service_account_email, queue, url, payload, extra=extra)            
        raise e
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        LOGGER.error("Exception when starting a command cloud run task: location: %s, service_account_email: %s, queue: %s, url: %s, payload: %s", location, service_account_email, queue, url, payload, extra=extra)            
        raise e
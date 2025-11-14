from pydantic.types import List
from .values import Address, CustomBaseModel, Attachment, Identifier, CodeableConcept, Name, Reference, Content, Telecom


class DocumentReference(CustomBaseModel):
    content: List[Content]
    identifier: List[Identifier]
    date: str
    type: CodeableConcept
    description: str
    docStatus: str
    status: str
    subject: Reference
    author: List[Reference]


class Person(CustomBaseModel):

    name: List[Name]
    address: List[Address]
    identifier: List[Identifier]
    birthDate: str
    telecom: List[Telecom]


class Patient(Person):

    managingOrganization: Reference

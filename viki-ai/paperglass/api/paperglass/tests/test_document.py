# import pytest
# from io import BytesIO
# from unittest.mock import MagicMock, patch
# from paperglass.domain.models import Document
# from paperglass.domain.values import Page as PageModel, Rect, Vector2
# from paperglass.infrastructure.ports import IStoragePort
# from paperglass.usecases.documents import create_document, split_pages

# @pytest.fixture
# def storage_mock():
#     return MagicMock(spec=IStoragePort)

# @pytest.fixture
# def document():
#     return Document(
#         id="123",
#         filename ="test.pdf", 
#         pages=[PageModel(
#                     number=1,
#                     mediabox=Rect(tl=Vector2(x=0, y=0), br=Vector2(x=10, y=10),
#                     storage_uri = "something1")),
#                 PageModel(
#                     number=2,
#                     mediabox=Rect(tl=Vector2(x=0, y=0), br=Vector2(x=10, y=10),
#                     storage_uri = "something2"))
#             ], 
#         page_count=1,
#         patient_id="456"
#     )

# @pytest.mark.asyncio
# async def test_create_document(storage_mock):
#     # Arrange
#     file_name = "test.pdf"
#     uploaded_bytes = b"dummy bytes"
#     patient_id = "123"
#     storage_mock.put_document.return_value = uri = "https://example.com/test.pdf"
    
#     pdf_reader_mock = MagicMock()
#     pdf_reader_mock.pages = [
#         MagicMock(page_number=0, mediabox=MagicMock(left=0, top=0, bottom=10, right=10)),
#         MagicMock(page_number=1, mediabox=MagicMock(left=0, top=0, bottom=20, right=20)),
#     ]
#     pypdf_mock = MagicMock(PdfReader=MagicMock(return_value=pdf_reader_mock))
    
#     with patch("paperglass.usecases.documents.pypdf", pypdf_mock):
#         # Act
#         document = await create_document(file_name, uploaded_bytes, patient_id, storage_mock)
    
#     # Assert
#     assert isinstance(document, Document)
#     assert document.filename == file_name
#     assert document.patient_id == patient_id
#     assert len(document.pages) == 2
#     assert document.pages[0] == PageModel(number=1, mediabox=Rect(tl=Vector2(x=0, y=0), br=Vector2(x=10, y=10)))
#     assert document.pages[1] == PageModel(number=2, mediabox=Rect(tl=Vector2(x=0, y=0), br=Vector2(x=20, y=20)))
#     storage_mock.put_document.assert_called_once_with(document.id, uploaded_bytes)
#     #document.mark_uploaded.assert_called_once_with(uri)

# @pytest.mark.asyncio
# async def test_split_pages(document, storage_mock):
#     # Mock the storage.get_document method
#     storage_mock.get_document.return_value = b"dummy_data"

#     pdf_reader_mock = MagicMock()
#     pdf_reader_mock.pages = [
#         MagicMock(page_number=0, mediabox=MagicMock(left=0, top=0, bottom=10, right=10)),
#         MagicMock(page_number=1, mediabox=MagicMock(left=0, top=0, bottom=20, right=20)),
#     ]
#     pypdf_mock = MagicMock(PdfReader=MagicMock(return_value=pdf_reader_mock))
    
#     storage_mock.put_document_page.return_value = "https://example.com/test.pdf"

#     with patch("paperglass.usecases.documents.pypdf", pypdf_mock):
#         result = await split_pages(document, storage_mock)

#     # Assert that the document pages are updated correctly
#     assert len(result.pages) == 2
#     assert result.pages[0].number == 1
#     assert result.pages[0].storage_uri is not None
#     assert result.pages[1].number == 2
#     assert result.pages[1].storage_uri is not None

#     # Assert that the storage.put_document_page method is called twice
#     assert storage_mock.put_document_page.call_count == 2
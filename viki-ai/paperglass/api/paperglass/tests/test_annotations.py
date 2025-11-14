# # py test case to run unit tests on the annotations module

# import pytest
# import os, sys

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
# print(sys.path)


# @pytest.fixture
# def setup_page_results():
#     return {
#         "text": "Hello World my dear friends!\nHow are you doing today?\n\nI hope you are doing well.",
#         "page": {
#             "lines": [
#                 {
#                     "layout": {
#                         "textAnchor": {"textSegments": [{"startIndex": 0, "endIndex": 11}]},
#                         "boundingPoly": {
#                             "vertices": [{"x": 1, "y": 2}, {"x": 3, "y": 4}, {"x": 5, "y": 6}, {"x": 7, "y": 8}],
#                             "normalizedVertices": [
#                                 {"x": 0.1, "y": 0.2},
#                                 {"x": 0.3, "y": 0.4},
#                                 {"x": 0.5, "y": 0.6},
#                                 {"x": 0.7, "y": 0.8},
#                             ],
#                         },
#                         "orientation": "UPRIGHT",
#                         "confidence": 0.9,
#                     },
#                     "detectedLanguages": ["en"],
#                 }
#             ],
#             "blocks": [
#                 {
#                     "layout": {
#                         "textAnchor": {"textSegments": [{"startIndex": 0, "endIndex": 11}]},
#                         "boundingPoly": {
#                             "vertices": [{"x": 1, "y": 2}, {"x": 3, "y": 4}, {"x": 5, "y": 6}, {"x": 7, "y": 8}],
#                             "normalizedVertices": [
#                                 {"x": 0.1, "y": 0.2},
#                                 {"x": 0.3, "y": 0.4},
#                                 {"x": 0.5, "y": 0.6},
#                                 {"x": 0.7, "y": 0.8},
#                             ],
#                         },
#                         "orientation": "UPRIGHT",
#                         "confidence": 0.9,
#                     },
#                     "detectedLanguages": ["en"],
#                 }
#             ],
#             "paragraphs": [
#                 {
#                     "layout": {
#                         "textAnchor": {"textSegments": [{"endIndex": 53}]},
#                         "boundingPoly": {
#                             "vertices": [{"x": 1, "y": 2}, {"x": 3, "y": 4}, {"x": 5, "y": 6}, {"x": 7, "y": 8}],
#                             "normalizedVertices": [
#                                 {"x": 0.1, "y": 0.2},
#                                 {"x": 0.3, "y": 0.4},
#                                 {"x": 0.5, "y": 0.6},
#                                 {"x": 0.7, "y": 0.8},
#                             ],
#                         },
#                         "orientation": "UPRIGHT",
#                         "confidence": 0.9,
#                     },
#                     "detectedLanguages": ["en"],
#                 },
#                 {
#                     "layout": {
#                         "textAnchor": {"textSegments": [{"startIndex": 55, "endIndex": 100}]},
#                         "boundingPoly": {
#                             "vertices": [{"x": 1, "y": 2}, {"x": 3, "y": 4}, {"x": 5, "y": 6}, {"x": 7, "y": 8}],
#                             "normalizedVertices": [
#                                 {"x": 0.1, "y": 0.2},
#                                 {"x": 0.3, "y": 0.4},
#                                 {"x": 0.5, "y": 0.6},
#                                 {"x": 0.7, "y": 0.8},
#                             ],
#                         },
#                         "orientation": "UPRIGHT",
#                         "confidence": 0.9,
#                     },
#                     "detectedLanguages": ["en"],
#                 },
#             ],
#             "tokens": [
#                 {
#                     "layout": {
#                         "textAnchor": {"textSegments": [{"endIndex": 5}]},
#                         "boundingPoly": {
#                             "vertices": [{"x": 1, "y": 2}, {"x": 3, "y": 4}, {"x": 5, "y": 6}, {"x": 7, "y": 8}],
#                             "normalizedVertices": [
#                                 {"x": 0.1, "y": 0.2},
#                                 {"x": 0.3, "y": 0.4},
#                                 {"x": 0.5, "y": 0.6},
#                                 {"x": 0.7, "y": 0.8},
#                             ],
#                         },
#                         "orientation": "UPRIGHT",
#                         "confidence": 0.9,
#                     },
#                     "detectedLanguages": ["en"],
#                 },
#                 {
#                     "layout": {
#                         "textAnchor": {"textSegments": [{"startIndex": 6, "endIndex": 11}]},
#                         "boundingPoly": {
#                             "vertices": [{"x": 1, "y": 2}, {"x": 3, "y": 4}, {"x": 5, "y": 6}, {"x": 7, "y": 8}],
#                             "normalizedVertices": [
#                                 {"x": 0.1, "y": 0.2},
#                                 {"x": 0.3, "y": 0.4},
#                                 {"x": 0.5, "y": 0.6},
#                                 {"x": 0.7, "y": 0.8},
#                             ],
#                         },
#                         "orientation": "UPRIGHT",
#                         "confidence": 0.9,
#                     },
#                     "detectedLanguages": ["en"],
#                 },
#             ],
#         },
#     }


# def test_annotations(setup_page_results):
#     from paperglass.domain.models import (
#         Annotation,
#         LineAnnotation,
#         BlockAnnotation,
#         TokenAnnotation,
#         ParagraphAnnotation,
#         DocumentAnnotations,
#     )

#     line_annotations = DocumentAnnotations.get_line_annotations(setup_page_results)
#     block_annotations = DocumentAnnotations.get_block_annotations(setup_page_results)
#     paragraph_annotations = DocumentAnnotations.get_paragraph_annotations(setup_page_results)
#     token_annotations = DocumentAnnotations.get_token_annotations(setup_page_results)

#     assert len(line_annotations) == 1
#     assert len(block_annotations) == 1
#     assert len(paragraph_annotations) == 2
#     assert len(token_annotations) == 2

#     assert line_annotations[0].text_segment == "Hello World"

#     assert block_annotations[0].text_segment == "Hello World"

#     assert paragraph_annotations[0].text_segment == "Hello World my dear friends!\nHow are you doing today?"
#     assert paragraph_annotations[1].text_segment == "I hope you are doing well."

#     assert token_annotations[0].text_segment == "Hello"
#     assert token_annotations[1].text_segment == "World"

#     for annotation in line_annotations:
#         assert isinstance(annotation, LineAnnotation)

#     for annotation in block_annotations:
#         assert isinstance(annotation, BlockAnnotation)

#     for annotation in paragraph_annotations:
#         assert isinstance(annotation, ParagraphAnnotation)

#     for annotation in token_annotations:
#         assert isinstance(annotation, TokenAnnotation)

#     for annotation in line_annotations:
#         assert annotation.normalized_vertice1 != {"x": 0, "y": 0}

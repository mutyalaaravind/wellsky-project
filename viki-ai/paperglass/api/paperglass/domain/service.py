class ResolveNamedEntityFromLabel(object):

    def resolve(self, label: str):
        from paperglass.domain.values import NamedEntityExtractionType

        if label == "medications":
            return NamedEntityExtractionType.MEDICATIONS

        return None


import json


def RawJSONDecoder(index):
    class _RawJSONDecoder(json.JSONDecoder):
        end = None

        def decode(self, s, *_):
            data, self.__class__.end = self.raw_decode(s, index)
            return data

    return _RawJSONDecoder


def extract_json(s, index=0):
    while (index := s.find('{', index)) != -1 or (index := s.find('[', index)) != -1:
        try:
            yield json.loads(s, cls=(decoder := RawJSONDecoder(index)))
            index = decoder.end
        except json.JSONDecodeError:
            index += 1

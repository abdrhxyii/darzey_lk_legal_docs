from dataclasses import dataclass
from functools import cache

from lk_legal_docs.legal_docs.AbstractGovLkWebPDFDoc import AbstractGovLkWebPDFDoc


@dataclass
class ExtraordinaryGazette(AbstractGovLkWebPDFDoc):
    @classmethod
    def get_url_base(cls) -> str:
        return "https://documents.gov.lk/web/extra_gazettes"

    @classmethod
    def get_api_path(cls) -> str:
        return "extra-gazette/get-all"

    @classmethod
    def get_doc_number_field(cls) -> str:
        return "gazetteNoText"

    @classmethod
    def get_doc_class_label(cls):
        return "lk_extraordinary_gazettes_" + cls.get_shard_decade()

    @classmethod
    @cache
    def get_shard_decade(cls):
        raise NotImplementedError

    @classmethod
    def get_doc_class_description(cls) -> str:
        return "An Extraordinary Gazette is an official government publication used to announce urgent laws, regulations, or public notices with immediate effect."

    @classmethod
    def get_doc_class_emoji(cls) -> str:
        return "⚖️"

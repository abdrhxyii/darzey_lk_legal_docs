from dataclasses import dataclass

from lk_legal_docs.legal_docs.AbstractGovLkWebPDFDoc import AbstractGovLkWebPDFDoc


@dataclass
class Bill(AbstractGovLkWebPDFDoc):
    @classmethod
    def get_url_base(cls) -> str:
        return "https://documents.gov.lk/web/bills"

    @classmethod
    def get_api_path(cls) -> str:
        return "bill/get-all"

    @classmethod
    def get_doc_number_field(cls) -> str:
        return "billNoText"

    @classmethod
    def get_doc_class_label(cls):
        return "lk_bills"

    @classmethod
    def get_doc_class_description(cls) -> str:
        return "A Bill is a draft law proposed in Parliament. It becomes binding once passed and enacted, shaping governance, rights, and daily life in the country."

    @classmethod
    def get_doc_class_emoji(cls) -> str:
        return "⚖️"

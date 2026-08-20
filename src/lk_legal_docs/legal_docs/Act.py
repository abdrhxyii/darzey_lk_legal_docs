from lk_legal_docs.legal_docs.AbstractGovLkWebPDFDoc import AbstractGovLkWebPDFDoc


class Act(AbstractGovLkWebPDFDoc):
    @classmethod
    def get_url_base(cls) -> str:
        return "https://documents.gov.lk/web/acts"

    @classmethod
    def get_api_path(cls) -> str:
        return "act/get-all"

    @classmethod
    def get_doc_number_field(cls) -> str:
        return "actNoText"

    @classmethod
    def get_doc_class_label(cls):
        return "lk_acts"

    @classmethod
    def get_doc_class_description(cls) -> str:
        return "A legal act is a law passed by Parliament that governs rights, duties, economy, and society, shaping daily life and national policy."

    @classmethod
    def get_doc_class_emoji(cls) -> str:
        return "⚖️"

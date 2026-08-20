import json
from dataclasses import dataclass
from math import ceil
from typing import Generator
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from lk_legal_docs.legal_docs.AbstractGovLkPDFDoc import AbstractGovLkPDFDoc


@dataclass
class AbstractGovLkWebPDFDoc(AbstractGovLkPDFDoc):
    """Government Printer document backed by the current JSON API."""

    API_BASE = "http://203.143.21.148:4500/website-data"
    PAGE_SIZE = 100

    @classmethod
    def get_api_path(cls) -> str:
        raise NotImplementedError

    @classmethod
    def get_url_base(cls) -> str:
        raise NotImplementedError

    @classmethod
    def get_doc_number_field(cls) -> str:
        raise NotImplementedError

    @classmethod
    def get_api_url(cls, page: int) -> str:
        query = urlencode({"limit": cls.PAGE_SIZE, "page": page})
        return f"{cls.API_BASE}/{cls.get_api_path()}?{query}"

    @classmethod
    def fetch_page(cls, page: int) -> dict:
        url = cls.get_api_url(page)
        request = Request(url, headers={"User-Agent": "DarzeyLegalDocs/1.0"})
        try:
            with urlopen(request, timeout=60) as response:
                payload = json.load(response)
        except Exception as exc:
            raise RuntimeError(f"Government Printer API request failed: {url}") from exc

        if not isinstance(payload, dict):
            raise RuntimeError(f"Unexpected Government Printer API response: {url}")
        if payload.get("error") or payload.get("message") and not (
            payload.get("data") or payload.get("items")
        ):
            raise RuntimeError(
                f"Government Printer API returned an error for {url}: "
                f"{payload.get('message') or payload.get('error')}"
            )
        return payload

    @classmethod
    def get_rows(cls, payload: dict) -> list[dict]:
        rows = payload.get("data")
        if rows is None:
            rows = payload.get("items")
        if not isinstance(rows, list):
            raise RuntimeError("Government Printer API response has no document list")
        return [row for row in rows if isinstance(row, dict)]

    @classmethod
    def get_total_pages(cls, payload: dict, row_count: int) -> int:
        pagination = payload.get("pagination") or {}
        total_pages = pagination.get("totalPages") or pagination.get("total_pages")
        if total_pages:
            return int(total_pages)

        total = pagination.get("total") or payload.get("total")
        if total:
            return max(1, ceil(int(total) / cls.PAGE_SIZE))

        return 1 if row_count < cls.PAGE_SIZE else 2

    @classmethod
    def get_date(cls, row: dict) -> str:
        raw_date = row.get("date") or row.get("fullDate") or row.get("publishedDate")
        date_str = str(raw_date or "")[:10]
        if len(date_str) != 10:
            return ""
        return date_str

    @classmethod
    def get_description(cls, row: dict) -> str:
        for field in (
            "descriptionEnglish",
            "descriptionSinhala",
            "descriptionTamil",
        ):
            value = row.get(field)
            if value:
                return str(value).strip()
        return ""

    @classmethod
    def get_file_url(cls, uploaded_file: str) -> str:
        file_path = str(uploaded_file).lstrip("/")
        return "https://documents.gov.lk/api/content-file-proxy?" + urlencode(
            {"file": f"/{file_path}"}
        )

    @classmethod
    def gen_docs(cls) -> Generator["AbstractGovLkWebPDFDoc", None, None]:
        page = 1
        while True:
            payload = cls.fetch_page(page)
            rows = cls.get_rows(payload)

            for row in rows:
                date_str = cls.get_date(row)
                doc_number = str(row.get(cls.get_doc_number_field()) or "").strip()
                if not date_str or not doc_number:
                    continue

                year = int(date_str[:4])
                shard_decade = cls.get_shard_decade()
                if shard_decade and f"{str(year)[:3]}0s" != shard_decade:
                    continue

                contents = row.get("contents") or row.get("content") or []
                if not isinstance(contents, list):
                    continue

                for content in contents:
                    if not isinstance(content, dict):
                        continue
                    language = str(content.get("language") or "").upper()
                    lang = {"SINHALA": "si", "TAMIL": "ta", "ENGLISH": "en"}.get(
                        language
                    )
                    uploaded_file = content.get("uploadedFile")
                    if not lang or not uploaded_file:
                        continue

                    doc_number_cleaned = doc_number.replace("/", "-").replace(" ", "_")
                    yield cls(
                        num=f"{date_str}-{doc_number_cleaned}-{lang}",
                        date_str=date_str,
                        description=cls.get_description(row),
                        url_metadata=cls.get_url_base(),
                        lang=lang,
                        url_pdf=cls.get_file_url(uploaded_file),
                        doc_number=doc_number,
                    )

            total_pages = cls.get_total_pages(payload, len(rows))
            if page >= total_pages or not rows:
                break
            page += 1

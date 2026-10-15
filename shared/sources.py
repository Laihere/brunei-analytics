"""Approved data sources. Anything not listed here cannot be downloaded or credited.

Adding a source is a policy decision: update DATA_USE_POLICY.md §6 first.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    key: str
    name: str
    licence: str
    licence_url: str
    terms_url: str
    apa_author: str = ""  # APA author when a dataset has no named owner
    apa_publisher: str = ""  # APA publisher / database name


SOURCES = {
    s.key: s
    for s in [
        Source(
            key="datagovbn",
            name="Brunei Open Data (data.gov.bn)",
            licence="Data.gov.bn Data Policy: Terms of Use",
            licence_url="https://www.data.gov.bn/data-policy-terms-of-use/",
            terms_url="https://www.data.gov.bn/data-policy-terms-of-use/",
            apa_author="",
            apa_publisher="Brunei Open Data",
        ),
        Source(
            key="worldbank",
            name="World Bank, World Development Indicators",
            licence="CC BY 4.0",
            licence_url="https://creativecommons.org/licenses/by/4.0/",
            terms_url="https://data.worldbank.org/summary-terms-of-use",
            apa_author="World Bank",
            apa_publisher="World Development Indicators",
        ),
        Source(
            key="faostat",
            name="FAO, FAOSTAT",
            licence="CC BY 4.0",
            licence_url="https://creativecommons.org/licenses/by/4.0/",
            terms_url="https://www.fao.org/contact-us/terms/db-terms-of-use",
            apa_author="Food and Agriculture Organization of the United Nations",
            apa_publisher="FAOSTAT",
        ),
        Source(
            key="ilostat",
            name="ILO, ILOSTAT",
            licence="CC BY 4.0",
            licence_url="https://creativecommons.org/licenses/by/4.0/",
            terms_url="https://www.ilo.org/node/9321",
            apa_author="International Labour Organization",
            apa_publisher="ILOSTAT",
        ),
    ]
}


def get_source(key: str) -> Source:
    if key not in SOURCES:
        raise ValueError(
            f"'{key}' is not an approved source ({', '.join(SOURCES)}). See DATA_USE_POLICY.md §6."
        )
    return SOURCES[key]

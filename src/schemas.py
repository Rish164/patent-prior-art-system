from typing import List
from pydantic import BaseModel, Field

class PatentDocument(BaseModel):
    """Contract representing an ingested patent document extracted from USPTO data."""
    patent_id: str = Field(description="Unique patent identifier, e.g. US-11825123-B2")
    title: str = Field(description="Title of the invention")
    abstract: str = Field(description="Short summary of the patent")
    cpc_codes: List[str] = Field(default_factory=list, description="Cooperative Patent Classification codes")
    claims: List[str] = Field(default_factory=list, description="List of numbered legal claims")


class InventionQuery(BaseModel):
    """Contract representing a user's new invention idea broken down for retrieval and cross-examination."""
    raw_text: str = Field(description="Raw text description submitted by the user")
    keywords: List[str] = Field(default_factory=list, description="Extracted technical search terms")
    elements: List[str] = Field(default_factory=list, description="Explicit technical elements to cross-examine")


if __name__ == "__main__":
    # Test 1: Patent Document
    test_doc = PatentDocument(
        patent_id="US-11825123-B2",
        title="Autonomous Aerial Vehicle Power System",
        abstract="A system for managing solar power in an unmanned aerial vehicle.",
        cpc_codes=["B64C 39/00", "H02S 10/40"],
        claims=[
            "1. An autonomous aerial vehicle comprising wings and solar cells.",
            "2. The vehicle of claim 1, further comprising a power controller."
        ]
    )

    # Test 2: Invention Query
    test_query = InventionQuery(
        raw_text="A solar-powered delivery drone with adaptive power routing.",
        keywords=["solar", "drone", "photovoltaic", "power routing"],
        elements=[
            "aerial vehicle chassis",
            "wing-mounted photovoltaic cells",
            "adaptive power switching circuit"
        ]
    )

    print("Both schemas verified successfully!")
    print(f"Sample Query has {len(test_query.elements)} elements to check.")
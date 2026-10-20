from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Issue(StrictModel):
    description: str = Field(min_length=1)
    impact: str | None
    evidence: list[str] = Field(min_length=1)


class Risk(StrictModel):
    description: str = Field(min_length=1)
    impact: str | None
    basis: Literal["explicit", "inferred"]
    evidence: list[str] = Field(min_length=1)


class Dependency(StrictModel):
    dependent_item: str = Field(min_length=1)
    dependency_item: str = Field(min_length=1)
    relationship: str = Field(min_length=1)
    basis: Literal["explicit", "inferred"]
    evidence: list[str] = Field(min_length=1)


class RequirementChange(StrictModel):
    requirement: str = Field(min_length=1)
    previous_state: str | None
    new_state: str = Field(min_length=1)
    change_status: Literal["proposed", "confirmed", "unknown"]
    evidence: list[str] = Field(min_length=1)


class ScheduleImpact(StrictModel):
    description: str = Field(min_length=1)
    affected_milestone: str | None
    duration_change: str | None
    impact_status: Literal["potential", "confirmed", "unknown"]
    evidence: list[str] = Field(min_length=1)


class ActionItem(StrictModel):
    action: str = Field(min_length=1)
    owner: str | None
    due_date: str | None
    evidence: list[str] = Field(min_length=1)


class Uncertainty(StrictModel):
    item: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    needed_information: str | None


class ProgramReview(StrictModel):
    summary: str = Field(min_length=1)
    issues: list[Issue]
    risks: list[Risk]
    dependencies: list[Dependency]
    requirement_changes: list[RequirementChange]
    schedule_impacts: list[ScheduleImpact]
    actions: list[ActionItem]
    uncertainties: list[Uncertainty]
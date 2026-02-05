"""Configuration management for AutoApply."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Anthropic API
    anthropic_api_key: str = Field(default="", description="Anthropic API key for Claude")
    anthropic_model: str = Field(
        default="claude-sonnet-4-20250514",
        description="Claude model to use",
    )

    # Notion Integration
    notion_api_key: Optional[str] = Field(default=None, description="Notion API key")
    notion_resume_database_id: Optional[str] = Field(
        default=None, description="Notion database ID containing resume data"
    )

    # Paths
    output_dir: Path = Field(default=Path("output"), description="Output directory for applications")
    jobs_file: Path = Field(default=Path("jobs.txt"), description="File containing job URLs")
    base_resume_file: Optional[Path] = Field(
        default=None, description="Path to base resume text file"
    )

    # Browser automation
    headless: bool = Field(default=False, description="Run browser in headless mode")
    auto_submit: bool = Field(
        default=False, description="Attempt auto-submission (pauses on CAPTCHA/login)"
    )
    submit_delay_seconds: int = Field(
        default=5, description="Delay before auto-submit for review"
    )

    # Rate limiting
    requests_per_minute: int = Field(default=10, description="Rate limit for API calls")
    concurrent_jobs: int = Field(default=3, description="Number of concurrent job processing")


settings = Settings()

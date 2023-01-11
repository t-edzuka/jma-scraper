from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

import boto3

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3ServiceResource
    from mypy_boto3_s3.service_resource import Bucket

from pydantic import BaseSettings, Field

from jma_scraper.core.repository import Writer, WriterSrcValues


class R2Conf(BaseSettings):
    """R2 Data Access configuration"""

    ACCOUNT_ID: str = Field(..., regex=r"^[a-fA-F0-9]{32}$")
    AWS_ACCESS_KEY_ID: str = Field(..., regex=r"^[a-fA-F0-9]{32}$")
    AWS_ACCESS_KEY_SECRET: str = Field(..., regex=r"^[a-fA-F0-9]{64}$")

    BUCKET_NAME: str = Field("00-hq", regex=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

    class Config:
        env_file = str(Path(__file__).parents[2] / ".env")

    @property
    def endpoint_url(self) -> str:
        return f"https://{self.ACCOUNT_ID}.r2.cloudflarestorage.com"

    @property
    def boto3_resource(self) -> "S3ServiceResource":
        return boto3.resource(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_ACCESS_KEY_SECRET,
            region_name="auto",  # R2 ではautoになる.
        )

    @property
    def bucket(self) -> "Bucket":
        return self.boto3_resource.Bucket(self.BUCKET_NAME)

    @property
    def bucket_url(self) -> str:
        return f"{self.endpoint_url}/{self.BUCKET_NAME}"

    def create_dst_url(self, dst_key: str) -> str:
        return f"{self.bucket_url}/{dst_key}"

    def write(self, src_file: str | Path, dst_key: str) -> None:
        self.bucket.upload_file(str(src_file), dst_key)


class LocalToR2Writer(Writer):
    def __init__(
            self,
            src_values: WriterSrcValues,
            r2_conf: R2Conf,
    ):
        super().__init__(src_values)
        self.r2_conf = r2_conf
        self.src_values = src_values

    def create_dst_url(self, dst_key: str) -> str:
        return self.r2_conf.create_dst_url(dst_key)

    def write(self, src: Path, dst: str) -> None:
        self.r2_conf.write(src, dst)

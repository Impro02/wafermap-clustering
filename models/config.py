from dataclasses import dataclass

@dataclass
class MailingConfig:
    host: str
    port: int
    sender: str
    reveiver: str

@dataclass
class PathConfig:
    input: str
    output: str
    error: str

@dataclass
class ClusteringConfig:
    eps: int
    min_samples: int


@dataclass
class Config:
    platform: str
    attribute: str
    path: PathConfig
    clustering: ClusteringConfig
    mailing: MailingConfig

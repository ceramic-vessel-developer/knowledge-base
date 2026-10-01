from dataclasses import dataclass

@dataclass(frozen=True)
class DocumentProcessorConfig:
    name:str


class DocumentProcessor:
    pass


class DocumentProcessorFactory:
    def create_processor(self, config:DocumentProcessorConfig) -> DocumentProcessor:
        pass
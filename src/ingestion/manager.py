from loguru import logger
import os
from src.ingestion.extractor import extract_from_file
from src.privacy.masking import masking_service
from src.security.audit import log_audit_event

class IngestionManager:
    def __init__(self, use_masking: bool = True):
        self.use_masking = use_masking

    def process_file(self, file_path: str, user_id: int = None) -> tuple[str, int]:
        """High-level flow: Extract -> Mask -> Return (Redacted Text, Count)."""
        logger.info(f"Processing ingestion for: {file_path}")
        
        try:
            # 1. Extract raw text
            raw_text = extract_from_file(file_path)
            
            # 2. Mask PII if enabled
            if self.use_masking:
                final_text, count = masking_service.mask_text(raw_text)
            else:
                final_text, count = raw_text, 0
                
            # 3. Log the audit event
            log_audit_event(
                "FILE_INGESTED", 
                {
                    "file_path": file_path, 
                    "masking_enabled": self.use_masking,
                    "file_size_bytes": os.path.getsize(file_path),
                    "redacted_count": count
                },
                user_id=user_id,
                status="SUCCESS"
            )
            
            return final_text, count

        except Exception as e:
            logger.error(f"Failed to process ingestion for {file_path}: {e}")
            log_audit_event(
                "FILE_INGESTION_FAILED", 
                {"file_path": file_path, "error": str(e)}, 
                user_id=user_id,
                status="FAILURE"
            )
            raise

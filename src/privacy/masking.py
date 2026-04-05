from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from loguru import logger
from src.privacy.rules import phone_recognizer, incomplete_email_recognizer

class PIIMaskingService:
    def __init__(self):
        logger.info("Initializing PII Masking Service (Presidio + SpaCy)...")
        
        # Register custom recognizers
        registry = RecognizerRegistry()
        registry.load_predefined_recognizers()
        registry.add_recognizer(phone_recognizer)
        registry.add_recognizer(incomplete_email_recognizer)
        
        self.analyzer = AnalyzerEngine(registry=registry)
        self.anonymizer = AnonymizerEngine()
        self.default_entities = [
            "EMAIL_ADDRESS", "IP_ADDRESS", "PHONE_NUMBER", 
            "CREDIT_CARD", "CRYPTO", "PERSON", "LOCATION", 
            "US_SSN", "US_BANK_NUMBER", "US_DRIVER_LICENSE"
        ]

    def mask_text(self, text: str, entities: list[str] = None) -> tuple[str, int]:
        """Scans and redacts PII from the given text. Returns (masked_text, count)."""
        if not text:
            return "", 0

        target_entities = entities or self.default_entities
        
        try:
            # 1. Analyze the text for PII
            results = self.analyzer.analyze(text=text, entities=target_entities, language='en')
            
            # 2. Anonymize the detected entities
            operators = {
                entity: OperatorConfig("replace", {"new_value": f"<{entity}>"})
                for entity in target_entities
            }
            
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=results,
                operators=operators
            )
            
            count = len(results)
            if count > 0:
                logger.info(f"Redacted {count} PII entities from text.")
                
            return anonymized_result.text, count

        except Exception as e:
            logger.error(f"Error during PII masking: {e}")
            return f"[ERROR: PII Masking Failed] {text}", 0

# Singleton instance for easy access
masking_service = PIIMaskingService()

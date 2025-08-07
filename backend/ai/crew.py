from crewai import Agent, Task, Crew
from .ai_service import ai_service
import json

class NetworkAutomationCrew:
    """Manages the crew of AI agents for network automation tasks."""
    def __init__(self):
        # Use AI service for now since it's properly initialized
        self.ai_service = ai_service

    def generate_and_validate_config(self, requirements: str, device_type: str):
        """Uses AI service to generate and validate a configuration."""
        try:
            # Parse requirements into parameters dict
            parameters = {
                "requirements": requirements,
                "device_type": device_type
            }
            
            # Generate configuration using AI service
            generated_config = self.ai_service.generate_configuration(
                config_type="vlan",  # Generic config type
                parameters=parameters
            )
            
            # Validate configuration using AI service  
            validation_result = self.ai_service.validate_configuration(
                config_content=generated_config,
                device_type=device_type
            )
            
            # Return structured result
            return {
                "generated_config": generated_config,
                "validation_result": validation_result,
                "device_type": device_type,
                "requirements": requirements
            }
            
        except Exception as e:
            print(f"Error in generate_and_validate_config: {e}")
            return {
                "error": str(e),
                "generated_config": "",
                "validation_result": "Failed to validate due to error",
                "device_type": device_type,
                "requirements": requirements
            }

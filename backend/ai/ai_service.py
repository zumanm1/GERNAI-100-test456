import openai
from backend.database.models import AIConversation, NetworkDevice, OperationLog, User, SystemConfig
from backend.database.database import get_db
from sqlalchemy.orm import Session
import json
import os
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
import logging
from .llm_manager import llm_manager, initialize_llm_manager

logger = logging.getLogger(__name__)

class AIService:
    """Service class for AI operations matching PRD specifications"""

    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.groq_client = None
        self.openrouter_client = None
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize AI clients from environment variables"""
        try:
            # Initialize OpenAI client
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key and openai_api_key not in ["your_openai_api_key", "sk-your-openai-api-key-here", ""]:
                print(f"🔑 Initializing OpenAI client with key: {openai_api_key[:10]}...")
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                print("✅ OpenAI client initialized successfully")
            else:
                print("⚠️ OpenAI API key not found or is placeholder")
            
            # Initialize Anthropic client
            anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_api_key and anthropic_api_key not in ["your_anthropic_api_key", "sk-ant-your-anthropic-key-here", ""]:
                try:
                    import anthropic
                    print(f"🔑 Initializing Anthropic client with key: {anthropic_api_key[:10]}...")
                    self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
                    print("✅ Anthropic client initialized successfully")
                except ImportError:
                    logger.warning("Anthropic package not available")
            else:
                print("⚠️ Anthropic API key not found or is placeholder")
                
            # Initialize Groq client (uses OpenAI-compatible API)
            groq_api_key = os.getenv("GROQ_API_KEY")
            if groq_api_key and groq_api_key not in ["your_groq_api_key", "gsk_your-groq-api-key-here", ""]:
                try:
                    print(f"🔑 Initializing Groq client with key: {groq_api_key[:10]}...")
                    self.groq_client = openai.OpenAI(
                        base_url="https://api.groq.com/openai/v1",
                        api_key=groq_api_key
                    )
                    print("✅ Groq client initialized successfully")
                except Exception as e:
                    print(f"❌ Groq client initialization failed: {e}")
            else:
                print("⚠️ Groq API key not found or is placeholder")
                
            # Initialize OpenRouter client (uses OpenAI-compatible API)
            openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
            if openrouter_api_key and openrouter_api_key not in ["your_openrouter_api_key", "sk-or-your-key-here", ""]:
                try:
                    print(f"🔑 Initializing OpenRouter client with key: {openrouter_api_key[:10]}...")
                    self.openrouter_client = openai.OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=openrouter_api_key
                    )
                    print("✅ OpenRouter client initialized successfully")
                except Exception as e:
                    print(f"❌ OpenRouter client initialization failed: {e}")
            else:
                print("⚠️ OpenRouter API key not found or is placeholder")
                    
        except Exception as e:
            logger.error(f"Error initializing AI clients: {e}")

    def get_response(self, user_message: str, session_id: str, user_id: str, db: Session) -> str:
        """Get AI response to user message"""
        try:
            # Get the current provider from the settings
            provider_name = self._get_provider_name(db)
            
            # Get conversation context
            context = self._get_conversation_context(session_id, user_id, db)
            
            # Get system context (device info, recent operations)
            system_context = self._get_system_context(user_id, db)
            
            # Prepare messages for AI
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a GENAI network assistant specialized in Cisco network automation. 
                    You help with network configuration, troubleshooting, and automation tasks.
                    
                    Current system context:
                    {json.dumps(system_context, indent=2)}
                    
                    Provide helpful, accurate responses about network operations. If you need to perform 
                    actions on devices, explain what you would do but note that actual device operations 
                    require manual confirmation."""
                }
            ]
            
            # Add conversation history
            for msg in context:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Debug logging
            print(f"🔍 Debug: provider_name={provider_name}, openai_client_exists={self.openai_client is not None}, groq_client_exists={self.groq_client is not None}")
            
            # Try Groq if selected
            if provider_name == "groq" and self.groq_client:
                try:
                    print(f"🤖 Making Groq API call with {len(messages)} messages")
                    response = self.groq_client.chat.completions.create(
                        model="llama3-70b-8192",
                        messages=messages,
                        max_tokens=1000,
                        temperature=0.7
                    )
                    ai_response = response.choices[0].message.content
                    print(f"✅ Groq response received: {ai_response[:100]}...")
                    
                    # Save conversation to database
                    self.save_conversation(user_id, session_id, "user", user_message, db)
                    self.save_conversation(user_id, session_id, "assistant", ai_response, db)
                    
                    return ai_response
                except Exception as e:
                    print(f"❌ Groq request failed: {e}")
                    logger.warning(f"Groq request failed: {e}")
            
            # Try OpenRouter if available and selected
            elif provider_name == "openrouter" and self.openrouter_client:
                try:
                    print(f"🤖 Making OpenRouter API call with {len(messages)} messages")
                    response = self.openrouter_client.chat.completions.create(
                        model="anthropic/claude-3.5-sonnet",
                        messages=messages,
                        max_tokens=1000,
                        temperature=0.7
                    )
                    ai_response = response.choices[0].message.content
                    print(f"✅ OpenRouter response received: {ai_response[:100]}...")
                    
                    # Save conversation to database
                    self.save_conversation(user_id, session_id, "user", user_message, db)
                    self.save_conversation(user_id, session_id, "assistant", ai_response, db)
                    
                    return ai_response
                except Exception as e:
                    print(f"❌ OpenRouter request failed: {e}")
                    logger.warning(f"OpenRouter request failed: {e}")
            
            # Try OpenAI if available and selected
            elif provider_name == "openai" and self.openai_client:
                try:
                    print(f"🤖 Making OpenAI API call with {len(messages)} messages")
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=messages,
                        max_tokens=1000,
                        temperature=0.7
                    )
                    ai_response = response.choices[0].message.content
                    print(f"✅ OpenAI response received: {ai_response[:100]}...")
                    
                    # Save conversation to database
                    self.save_conversation(user_id, session_id, "user", user_message, db)
                    self.save_conversation(user_id, session_id, "assistant", ai_response, db)
                    
                    return ai_response
                except Exception as e:
                    print(f"❌ OpenAI request failed: {e}")
                    logger.warning(f"OpenAI request failed: {e}")
            
            # Try Anthropic as fallback
            if self.anthropic_client:
                try:
                    response = self.anthropic_client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=1000,
                        messages=messages[1:],  # Claude doesn't need system message in messages array
                        system=messages[0]["content"]
                    )
                    ai_response = response.content[0].text
                    
                    # Save conversation to database
                    self.save_conversation(user_id, session_id, "user", user_message, db)
                    self.save_conversation(user_id, session_id, "assistant", ai_response, db)
                    
                    return ai_response
                except Exception as e:
                    logger.warning(f"Anthropic request failed: {e}")
            
            # Fallback response
            fallback_response = "I apologize, but I'm experiencing technical difficulties connecting to AI services. Please check your API configuration in the settings page and try again later."
            
            # Save conversation to database even for fallback
            self.save_conversation(user_id, session_id, "user", user_message, db)
            self.save_conversation(user_id, session_id, "assistant", fallback_response, db)
            
            return fallback_response
            
        except Exception as e:
            logger.error(f"AI service error: {e}")
            error_response = f"An error occurred while processing your request: {str(e)}"
            
            # Save conversation to database even for errors
            try:
                self.save_conversation(user_id, session_id, "user", user_message, db)
                self.save_conversation(user_id, session_id, "assistant", error_response, db)
            except:
                pass
                
            return error_response

    def _get_provider_name(self, db: Session) -> str:
        """Get the current provider name from the settings"""
        try:
            core_settings = db.query(SystemConfig).filter(SystemConfig.config_key == "core_settings").first()
            if core_settings and core_settings.config_value:
                provider = core_settings.config_value.get("default_chat_provider", "groq")
                logger.info(f"Using provider from database settings: {provider}")
                return provider
        except Exception as e:
            logger.warning(f"Could not get provider from database: {e}")
        
        # Default fallback priority based on available API keys: groq > openrouter > openai > anthropic
        import os
        if self.groq_client and os.getenv("GROQ_API_KEY"):
            logger.info("Using Groq as default provider (API key available)")
            return "groq"
        elif self.openrouter_client and os.getenv("OPENROUTER_API_KEY"):
            logger.info("Using OpenRouter as default provider (API key available)")
            return "openrouter"
        elif self.openai_client and os.getenv("OPENAI_API_KEY"):
            logger.info("Using OpenAI as default provider (API key available)")
            return "openai"
        else:
            logger.info("Using Anthropic as fallback provider")
            return "anthropic"

    def _get_conversation_context(self, session_id: str, user_id: str, db: Session, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation context"""
        try:
            conversations = db.query(AIConversation).filter(
                AIConversation.session_id == session_id,
                AIConversation.user_id == user_id
            ).order_by(
                AIConversation.created_at.desc()
            ).limit(limit).all()

            return [{"role": conv.message_role, "content": conv.message_content} for conv in reversed(conversations)]
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return []

    
    def _get_system_context(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get current system context for AI"""
        try:
            # Get device information for this user
            devices = db.query(NetworkDevice).filter(NetworkDevice.owner_id == user_id).all()
            device_summary = []
            
            for device in devices:
                device_summary.append({
                    'name': device.name,
                    'ip': device.ip_address,
                    'model': device.model,
                    'status': device.status,
                    'uptime': device.uptime_formatted
                })
            
            # Get recent operations for this user
            recent_operations = db.query(OperationLog).filter(
                OperationLog.user_id == user_id
            ).order_by(
                OperationLog.created_at.desc()
            ).limit(5).all()
            
            operation_summary = []
            for op in recent_operations:
                operation_summary.append({
                    'type': op.operation_type,
                    'status': op.status,
                    'device': op.device.name if op.device else 'Unknown',
                    'timestamp': op.created_at.isoformat(),
                    'error': op.error_message
                })
            
            return {
                'devices': device_summary,
                'recent_operations': operation_summary,
                'total_devices': len(devices),
                'online_devices': len([d for d in devices if d.status == 'online'])
            }
        except Exception as e:
            logger.error(f"Error getting system context: {e}")
            return {'devices': [], 'recent_operations': [], 'total_devices': 0, 'online_devices': 0}
    
    def generate_configuration(self, config_type: str, parameters: Dict[str, Any]) -> str:
        """Generate network configuration using AI"""
        prompt = f"""Generate a Cisco IOS configuration for {config_type} with the following parameters:
        {json.dumps(parameters, indent=2)}
        
        Provide a complete, production-ready configuration with:
        1. Proper syntax and commands
        2. Security best practices
        3. Comments explaining key sections
        4. Error handling where applicable
        
        Format the response as a code block with proper indentation."""
        
        try:
            # Try Groq first
            if self.groq_client:
                response = self.groq_client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert Cisco network engineer. Generate accurate, secure, and production-ready configurations."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=2000,
                    temperature=0.3  # Lower temperature for more consistent technical output
                )
                return response.choices[0].message.content
            
            elif self.openrouter_client:
                response = self.openrouter_client.chat.completions.create(
                    model="anthropic/claude-3.5-sonnet",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert Cisco network engineer. Generate accurate, secure, and production-ready configurations."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=2000,
                    temperature=0.3
                )
                return response.choices[0].message.content
                
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    system="You are an expert Cisco network engineer. Generate accurate, secure, and production-ready configurations."
                )
                return response.content[0].text
            
            else:
                # Fallback response
                return f"""! Configuration generation service temporarily unavailable
! Requested: {config_type}
! Parameters: {json.dumps(parameters, indent=2)}
!
! Please configure your AI API keys in the settings and try again.
"""
                
        except Exception as e:
            logger.error(f"Configuration generation error: {e}")
            # Return a helpful fallback instead of raising an exception
            return f"""! Error generating configuration: {str(e)}
! Requested: {config_type} 
! Parameters: {json.dumps(parameters, indent=2)}
!
! Please check your AI API configuration and try again.
"""
    
    async def generate_configuration_async(self, requirements: Dict[str, Any], device_type: str) -> str:
        """Asynchronous configuration generation using AI"""
        return self.generate_configuration("ai_generated", requirements)

    async def validate_configuration_async(self, config: str, device_type: str, validation_level: str) -> Dict[str, Any]:
        """Asynchronous configuration validation"""
        validation = self.validate_configuration(config, device_type)
        validation['level'] = validation_level
        return validation

    async def optimize_configuration(self, config: str, device_type: str, validation_result: Dict[str, Any]) -> str:
        """Asynchronous configuration optimization"""
        # Assume some optimization is performed based on validation
        if validation_result.get("valid", False):
            return config  # No optimization needed if valid

        # Placeholder for actual optimization logic
        optimized_config = config + "\n! Optimized Configuration\n"
        return optimized_config

    async def enhance_requirements(self, requirements: str, device_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance user requirements with AI analysis"""
        try:
            prompt = f"""Analyze and enhance these network requirements:
            
            Requirements: {requirements}
            Device Type: {device_type}
            Parameters: {json.dumps(params, indent=2)}
            
            Provide enhanced requirements with:
            1. Missing technical details
            2. Best practice recommendations
            3. Security considerations
            4. Implementation steps
            """
            
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a network design expert. Enhance user requirements with technical depth and best practices."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=1500,
                    temperature=0.4
                )
                
                return {
                    "original": requirements,
                    "enhanced": response.choices[0].message.content,
                    "device_type": device_type,
                    "parameters": params
                }
            
            # Fallback if no AI available
            return {
                "original": requirements,
                "enhanced": requirements,
                "device_type": device_type,
                "parameters": params
            }
        except Exception as e:
            logger.error(f"Requirements enhancement error: {e}")
            return {
                "original": requirements,
                "enhanced": requirements,
                "device_type": device_type,
                "parameters": params
            }

    def save_conversation(self, user_id: str, session_id: str, role: str, content: str, db: Session, metadata: Optional[Dict] = None) -> AIConversation:
        try:
            conversation = AIConversation(
                user_id=user_id,
                session_id=session_id,
                message_role=role,
                message_content=content,
                metadata=metadata,
                created_at=datetime.now(timezone.utc)
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            return conversation
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            db.rollback()
            raise
    
    def validate_configuration(self, config_content: str, device_type: str = "ios") -> Dict[str, Any]:
        """Validate network configuration using AI"""
        prompt = f"""Analyze the following {device_type.upper()} configuration for:
        1. Syntax errors
        2. Security vulnerabilities
        3. Best practice violations
        4. Potential issues
        
        Configuration:
        ```
        {config_content}
        ```
        
        Provide a structured analysis with:
        - Overall status (valid/invalid/warning)
        - List of issues found
        - Recommendations for improvement
        - Risk level assessment
        """
        
        try:
            # Try Groq first
            if self.groq_client:
                response = self.groq_client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a network security expert. Analyze configurations thoroughly for errors, security issues, and best practices."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=1500,
                    temperature=0.2
                )
                
                # Parse response and structure it
                analysis_text = response.choices[0].message.content
                return {
                    'status': 'analyzed',
                    'analysis': analysis_text,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            elif self.openrouter_client:
                response = self.openrouter_client.chat.completions.create(
                    model="anthropic/claude-3.5-sonnet",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a network security expert. Analyze configurations thoroughly for errors, security issues, and best practices."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=1500,
                    temperature=0.2
                )
                
                # Parse response and structure it
                analysis_text = response.choices[0].message.content
                return {
                    'status': 'analyzed',
                    'analysis': analysis_text,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1500,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    system="You are a network security expert. Analyze configurations thoroughly for errors, security issues, and best practices."
                )
                
                return {
                    'status': 'analyzed',
                    'analysis': response.content[0].text,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            else:
                return {
                    'status': 'analyzed',
                    'analysis': 'AI validation service temporarily unavailable. Manual review recommended.',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return {
                'status': 'analyzed',
                'analysis': f'Validation failed: {str(e)}. Manual review recommended.',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def get_configuration_analysis(self, prompt: str) -> str:
        """Get AI analysis for configuration audit"""
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert Cisco network engineer and security analyst. Provide detailed, structured analysis of network configurations with specific findings, recommendations, and risk assessments."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=2000,
                    temperature=0.3
                )
                return response.choices[0].message.content
            
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    system="You are an expert Cisco network engineer and security analyst. Provide detailed, structured analysis of network configurations with specific findings, recommendations, and risk assessments."
                )
                return response.content[0].text
            
            else:
                return "AI configuration analysis service is currently unavailable. Please check your API configuration."
                
        except Exception as e:
            logger.error(f"Configuration analysis error: {e}")
            return f"Configuration analysis failed: {str(e)}"
    
    def analyze_troubleshooting_scenario(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered troubleshooting analysis"""
        try:
            prompt = f"""
            Analyze this network troubleshooting scenario and provide AI-powered diagnosis:
            
            Problem Description: {scenario_data.get('problem_description', '')}
            Problem Domain: {scenario_data.get('problem_domain', '')}
            Affected Devices: {scenario_data.get('affected_devices', [])}
            Symptoms: {scenario_data.get('symptoms', [])}
            
            Provide:
            1. Likely root causes (ranked by probability)
            2. Diagnostic steps to confirm the issue
            3. Resolution procedures
            4. Prevention recommendations
            5. Estimated resolution time
            
            Format the response as JSON with structured diagnostic information.
            """
            
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a senior network engineer with expertise in Cisco technologies and network troubleshooting. Provide systematic, actionable troubleshooting guidance."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=2000,
                    temperature=0.4
                )
                
                analysis_text = response.choices[0].message.content
                
                return {
                    'status': 'completed',
                    'analysis': analysis_text,
                    'confidence': 'high',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    system="You are a senior network engineer with expertise in Cisco technologies and network troubleshooting. Provide systematic, actionable troubleshooting guidance."
                )
                
                return {
                    'status': 'completed',
                    'analysis': response.content[0].text,
                    'confidence': 'high',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            else:
                return {
                    'status': 'error',
                    'message': 'AI troubleshooting service unavailable',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Troubleshooting analysis error: {e}")
            return {
                'status': 'error',
                'message': f'Troubleshooting analysis failed: {str(e)}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def generate_baseline_recommendations(self, devices_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI-powered baseline configuration recommendations"""
        try:
            prompt = f"""
            Analyze these network devices and generate baseline configuration recommendations:
            
            Devices: {json.dumps(devices_data, indent=2)}
            
            Generate:
            1. Golden configuration template
            2. Security hardening recommendations
            3. Performance optimization settings
            4. Compliance configuration (PCI-DSS, NIST)
            5. Monitoring and logging setup
            
            Format as structured JSON with separate sections for each recommendation category.
            """
            
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a network architecture expert specializing in Cisco technologies. Generate comprehensive, production-ready baseline configurations."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=2500,
                    temperature=0.3
                )
                
                return {
                    'status': 'completed',
                    'recommendations': response.choices[0].message.content,
                    'confidence': 'high',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2500,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    system="You are a network architecture expert specializing in Cisco technologies. Generate comprehensive, production-ready baseline configurations."
                )
                
                return {
                    'status': 'completed',
                    'recommendations': response.content[0].text,
                    'confidence': 'high',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            else:
                return {
                    'status': 'error',
                    'message': 'AI baseline service unavailable',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Baseline generation error: {e}")
            return {
                'status': 'error',
                'message': f'Baseline generation failed: {str(e)}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

# Global AI service instance
ai_service = AIService()

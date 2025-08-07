from ..database.models import SystemConfig
from sqlalchemy.orm import Session

def get_genai_settings(db: Session):
    return db.query(SystemConfig).filter(SystemConfig.config_key.like('genai_%')).all()

def update_genai_settings(db: Session, settings: dict):
    for key, value in settings.items():
        config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        if config:
            config.config_value = value
        else:
            config = SystemConfig(config_key=key, config_value=value)
            db.add(config)
    db.commit()


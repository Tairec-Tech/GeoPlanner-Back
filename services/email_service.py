# services/email_service.py
import os
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader, Template
from typing import Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Verificar si las variables de entorno están configuradas
        self.mail_configured = all([
            os.getenv("MAIL_USERNAME"),
            os.getenv("MAIL_PASSWORD"),
            os.getenv("MAIL_FROM"),
            os.getenv("MAIL_SERVER")
        ])
        
        # Para desarrollo, puedes forzar modo simulación
        # Cambia esto a True si quieres probar sin email real
        self.force_simulation = False
        
        if self.mail_configured and not self.force_simulation:
            try:
                # Configuración SMTP
                self.conf = ConnectionConfig(
                    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
                    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
                    MAIL_FROM=os.getenv("MAIL_FROM"),
                    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
                    MAIL_SERVER=os.getenv("MAIL_SERVER"),
                    MAIL_STARTTLS=True,
                    MAIL_SSL_TLS=False,
                    USE_CREDENTIALS=True
                )
                self.fastmail = FastMail(self.conf)
                logger.info("EmailService configurado correctamente con SMTP")
            except Exception as e:
                logger.error(f"Error configurando SMTP: {e}")
                self.mail_configured = False
                self.fastmail = None
        else:
            self.fastmail = None
            if self.force_simulation:
                logger.info("EmailService: Modo simulación forzado para desarrollo")
            else:
                logger.warning("EmailService: Variables de entorno SMTP no configuradas. Los emails no se enviarán.")
        
        # Configurar Jinja2
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
        logger.info(f"EmailService inicializado. Templates dir: {self.templates_dir}")
    
    def _render_template(self, template_name: str, **kwargs) -> str:
        """Renderiza una plantilla Jinja2"""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**kwargs)
        except Exception as e:
            logger.error(f"Error renderizando plantilla {template_name}: {e}")
            # Fallback a plantilla básica
            return self._get_fallback_template(**kwargs)
    
    def _get_fallback_template(self, **kwargs) -> str:
        """Plantilla de respaldo si falla Jinja2"""
        username = kwargs.get('username', 'Usuario')
        verification_code = kwargs.get('verification_code', '000000')
        
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px;">
                    <h2 style="color: #2c3e50;">Verificación GeoPlanner</h2>
                    <p>Hola <strong>{username}</strong>,</p>
                    <p>Tu código de verificación es:</p>
                    <div style="background: #f8f9fa; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0;">
                        <span style="font-size: 24px; font-weight: bold; color: #e74c3c; letter-spacing: 3px;">{verification_code}</span>
                    </div>
                    <p>Este código expirará en 10 minutos.</p>
                </div>
            </body>
        </html>
        """
    
    async def send_verification_email(self, email: str, username: str, verification_code: str) -> bool:
        """Envía email de verificación"""
        if not self.mail_configured:
            logger.warning(f"Email no configurado. Simulando envío a {email} con código {verification_code}")
            return True  # Simular éxito para desarrollo
            
        try:
            # Renderizar plantilla
            html_content = self._render_template(
                "verification_email.html",
                username=username,
                verification_code=verification_code,
                app_name="GeoPlanner"
            )
            
            message = MessageSchema(
                subject="🌍 Verifica tu cuenta de GeoPlanner",
                recipients=[email],
                body=html_content,
                subtype="html"
            )
            
            await self.fastmail.send_message(message)
            logger.info(f"Email de verificación enviado exitosamente a {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email de verificación a {email}: {e}")
            return False
    
    async def send_welcome_email(self, email: str, username: str) -> bool:
        """Envía email de bienvenida después de verificación"""
        if not self.mail_configured:
            logger.warning(f"Email no configurado. Simulando envío de bienvenida a {email}")
            return True  # Simular éxito para desarrollo
            
        try:
            html_content = self._render_template(
                "welcome_email.html",
                username=username,
                app_name="GeoPlanner"
            )
            
            message = MessageSchema(
                subject="🎉 ¡Bienvenido a GeoPlanner!",
                recipients=[email],
                body=html_content,
                subtype="html"
            )
            
            await self.fastmail.send_message(message)
            logger.info(f"Email de bienvenida enviado exitosamente a {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email de bienvenida a {email}: {e}")
            return False
    
    async def send_password_reset_email(self, email: str, username: str, reset_token: str) -> bool:
        """Envía email de reset de contraseña"""
        if not self.mail_configured:
            logger.warning(f"Email no configurado. Simulando envío de reset a {email}")
            return True  # Simular éxito para desarrollo
            
        try:
            reset_url = f"http://localhost:5173/reset-password?token={reset_token}"
            
            html_content = self._render_template(
                "password_reset_email.html",
                username=username,
                reset_code=reset_token,
                email=email,
                reset_url=reset_url,
                app_name="GeoPlanner"
            )
            
            message = MessageSchema(
                subject="🔑 Restablece tu contraseña de GeoPlanner",
                recipients=[email],
                body=html_content,
                subtype="html"
            )
            
            await self.fastmail.send_message(message)
            logger.info(f"Email de reset de contraseña enviado exitosamente a {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email de reset de contraseña a {reset_token}: {e}")
            return False
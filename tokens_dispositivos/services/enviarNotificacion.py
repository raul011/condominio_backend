
# ejecutar antes python manage.py shell
# verificar que el token generado en flutter , sea el que esta en la base de datos

from tokens_dispositivos.services.notification_service import NotificationService

result = NotificationService.send_to_user(
    user_id=1,
    title="Hola 🚀",
    message="Este es un mensaje de prueba con FCM v1",
    notification_type="alert"
)

print(result)

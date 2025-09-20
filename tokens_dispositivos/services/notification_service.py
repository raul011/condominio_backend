import requests
import google.auth.transport.requests
from google.oauth2 import service_account
from django.conf import settings
from tokens_dispositivos.models import DeviceToken

class NotificationService:
    @staticmethod
    def _get_access_token():
        """
        Generar token OAuth2 válido para FCM v1
        """
        SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

        credentials = service_account.Credentials.from_service_account_file(
            settings.FIREBASE_CREDENTIALS, scopes=SCOPES
        )
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token

    @staticmethod
    def send_to_user(user_id, title, message, notification_type):
        """
        Enviar notificación a todos los dispositivos de un usuario (FCM v1)
        """
        # Obtener tokens de dispositivos activos
        tokens = DeviceToken.objects.filter(
            user_id=user_id, is_active=True
        ).values_list("token", flat=True)

        if not tokens:
            return {"success": False, "error": "No hay tokens registrados"}

        access_token = NotificationService._get_access_token()
        url = f"https://fcm.googleapis.com/v1/projects/{settings.FIREBASE_PROJECT_ID}/messages:send"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; UTF-8",
        }

        results = []
        for token in tokens:
            body = {
                "message": {
                    "token": token,
                    "notification": {
                        "title": title,
                        "body": message,
                    },
                    "data": {  # Datos personalizados
                        "type": notification_type
                    }
                }
            }
            response = requests.post(url, headers=headers, json=body)
            results.append({
                "token": token,
                "status": response.status_code,
                "response": response.json()
            })

        return {"success": True, "results": results}

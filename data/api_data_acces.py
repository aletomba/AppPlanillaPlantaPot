import logging
import requests
import urllib.parse
import json
import os

logger = logging.getLogger(__name__)

class APIDataAccess:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def fetch_data(self, endpoint, params=None):
        """
        Obtiene datos con soporte para paginación y filtros
        
        :param endpoint: URL del endpoint
        :param params: dict con parámetros (page, pageSize, procedencia, etc)
        """
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            parsed_url = urllib.parse.urlparse(url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                raise ValueError("Invalid URL")
            
            response = requests.get(url, params=params, timeout=10, verify=False)
            response.raise_for_status()
            logger.debug("Datos recibidos de %s: %s", url, response.text)
            data = response.json()
            
            # Si es una respuesta paginada, devolver con metadatos
            if isinstance(data, dict) and 'items' in data:
                return data, None
            
            # Si es una lista simple, envolver en dict
            if isinstance(data, list):
                return {'items': data}, None
            
            return data, None
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            try:
                error_detail = e.response.json().get("message", e.response.text)
            except:
                error_detail = e.response.text
            return None, f"Error al obtener datos (HTTP {status_code}): {error_detail} (URL: {url})"
        except requests.exceptions.ConnectionError:
            return None, f"Error de conexión: No se pudo conectar al servidor (URL: {url})"
        except requests.exceptions.Timeout:
            return None, f"Error de tiempo de espera: La solicitud tardó demasiado (URL: {url})"
        except requests.exceptions.RequestException as e:
            return None, f"Error al obtener datos: {e} (URL: {url})"
        except json.JSONDecodeError:
            return None, f"La respuesta no es un JSON válido: {response.text} (URL: {url})"
        except ValueError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Error inesperado: {e}"

    def post_data(self, endpoint, data):
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            headers = {"Content-Type": "application/json"}
            logger.debug("JSON enviado a %s: %s", url, json.dumps(data, indent=2))
            response = requests.post(url, json=data, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            try:
                error_detail = e.response.json()
                logger.error("Respuesta de error de la API (POST %s): %s", url, json.dumps(error_detail, indent=2))
            except:
                error_detail = e.response.text
                logger.error("Respuesta de error no JSON (POST %s): %s", url, error_detail)
            return None, f"Error al enviar datos (HTTP {status_code}): {error_detail} (URL: {url})"
        except requests.exceptions.ConnectionError:
            return None, f"Error de conexión: No se pudo conectar al servidor (URL: {url})"
        except requests.exceptions.Timeout:
            return None, f"Error de tiempo de espera: La solicitud tardó demasiado (URL: {url})"
        except requests.exceptions.RequestException as e:
            return None, f"Error al enviar datos: {e} (URL: {url})"
        except json.JSONDecodeError:
            return None, f"La respuesta no es un JSON válido: {e.response.text} (URL: {url})"
        except Exception as e:
            return None, f"Error inesperado: {e}"

    def put_data(self, endpoint, data):
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            headers = {"Content-Type": "application/json"}
            logger.debug("JSON enviado a %s: %s", url, json.dumps(data, indent=2))
            response = requests.put(url, json=data, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            try:
                error_detail = e.response.json()
                logger.error("Respuesta de error de la API (PUT %s): %s", url, json.dumps(error_detail, indent=2))
            except:
                error_detail = e.response.text
                logger.error("Respuesta de error no JSON (PUT %s): %s", url, error_detail)
            return None, f"Error al enviar datos (HTTP {status_code}): {error_detail} (URL: {url})"
        except requests.exceptions.ConnectionError:
            return None, f"Error de conexión: No se pudo conectar al servidor (URL: {url})"
        except requests.exceptions.Timeout:
            return None, f"Error de tiempo de espera: La solicitud tardó demasiado (URL: {url})"
        except requests.exceptions.RequestException as e:
            return None, f"Error al enviar datos: {e} (URL: {url})"
        except json.JSONDecodeError:
            return None, f"La respuesta no es un JSON válido: {e.response.text} (URL: {url})"
        except Exception as e:
            return None, f"Error inesperado: {e}"

    def delete_data(self, endpoint):
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = requests.delete(url, timeout=10, verify=False)
            response.raise_for_status()
            return response.json() if response.text else {}, None
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            try:
                error_detail = e.response.json()
                logger.error("Respuesta de error de la API (DELETE %s): %s", url, json.dumps(error_detail, indent=2))
            except:
                error_detail = e.response.text
                logger.error("Respuesta de error no JSON (DELETE %s): %s", url, error_detail)
            return None, f"Error al eliminar datos (HTTP {status_code}): {error_detail} (URL: {url})"
        except requests.exceptions.ConnectionError:
            return None, f"Error de conexión: No se pudo conectar al servidor (URL: {url})"
        except requests.exceptions.Timeout:
            return None, f"Error de tiempo de espera: La solicitud tardó demasiado (URL: {url})"
        except requests.exceptions.RequestException as e:
            return None, f"Error al eliminar datos: {e} (URL: {url})"
        except json.JSONDecodeError:
            return None, f"La respuesta no es un JSON válido: {e.response.text} (URL: {url})"
        except Exception as e:
            return None, f"Error inesperado: {e}"

    def get_binary(self, endpoint):
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            headers = {"Accept": "application/pdf, application/octet-stream"}
            response = requests.get(url, headers=headers, timeout=30, verify=False)
            response.raise_for_status()
            return response.content, None
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            try:
                error_detail = e.response.text
            except:
                error_detail = str(e)
            return None, f"Error al obtener binario (HTTP {status_code}): {error_detail} (URL: {url})"
        except requests.exceptions.ConnectionError:
            return None, f"Error de conexión: No se pudo conectar al servidor (URL: {url})"
        except requests.exceptions.Timeout:
            return None, f"Error de tiempo de espera: La solicitud tardó demasiado (URL: {url})"
        except requests.exceptions.RequestException as e:
            return None, f"Error al obtener binario: {e} (URL: {url})"
        except Exception as e:
            return None, f"Error inesperado: {e}"
import json
import os
from datetime import datetime


class NotificacionesManager:
    """Gestiona el estado de notificaciones vistas/no vistas"""
    
    def __init__(self):
        self.config_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "notificaciones_vistas.json"
        )
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Asegura que el archivo de configuración existe"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        if not os.path.exists(self.config_file):
            self._save_data({"ultima_vista": None, "count_visto": 0})
    
    def _load_data(self):
        """Carga los datos del archivo"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"ultima_vista": None, "count_visto": 0}
    
    def _save_data(self, data):
        """Guarda los datos en el archivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error guardando notificaciones: {e}")
    
    def marcar_como_vistas(self, count_actual: int):
        """Marca las notificaciones actuales como vistas"""
        data = {
            "ultima_vista": datetime.now().isoformat(),
            "count_visto": count_actual
        }
        self._save_data(data)
    
    def get_count_no_vistas(self, count_actual: int) -> int:
        """Obtiene el número de notificaciones no vistas"""
        data = self._load_data()
        count_visto = data.get("count_visto", 0)
        
        # Si hay más notificaciones que las que se vieron, mostrar la diferencia
        nuevas = max(0, count_actual - count_visto)
        return nuevas
    
    def reset(self):
        """Resetea el contador"""
        self._save_data({"ultima_vista": None, "count_visto": 0})

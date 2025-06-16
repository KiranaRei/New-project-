import json
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_file="data/server_configs.json"):
        self.config_file = config_file
        self.configs = {}
        self._ensure_data_directory()
        self._load_configs()

    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

    def _load_configs(self):
        """Load configurations from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.configs = json.load(f)
            else:
                self.configs = {}
        except Exception as e:
            print(f"Error loading configs: {e}")
            self.configs = {}

    def _save_configs(self):
        """Save configurations to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.configs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving configs: {e}")

    def get_server_config(self, guild_id: str) -> Dict[str, Any]:
        """Get configuration for a specific server"""
        if guild_id not in self.configs:
            self.configs[guild_id] = self._get_default_config()
            self._save_configs()
        return self.configs[guild_id].copy()

    def update_server_config(self, guild_id: str, updates: Dict[str, Any]):
        """Update configuration for a specific server"""
        if guild_id not in self.configs:
            self.configs[guild_id] = self._get_default_config()
        
        self.configs[guild_id].update(updates)
        self._save_configs()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for a new server"""
        return {
            "welcome_channel": None,
            "welcome_message": "Welcome to {server}, {user}! Please read the rules and enjoy your stay.",
            "welcome_bg_image": None,
            "announcement_channel": None,
            "mod_log_channel": None,
            "rules": [
                "Hormati semua anggota server",
                "Dilarang spam atau promosi berlebihan",
                "Jaga percakapan tetap sopan dan ramah",
                "Gunakan channel sesuai dengan tujuannya",
                "Dilarang melakukan harassment atau hate speech",
                "Ikuti Syarat dan Ketentuan Discord",
                "Dengarkan dan patuhi moderator serta admin"
            ],
            "rules_image": "https://cdn.discordapp.com/attachments/1321194434959691776/1321194589435023380/8da8698a5362140d0ac4499fdfce576c_1750057984927.jpg",
            "warnings": {},
            "auto_roles": [],
            "translate_channel": None
        }

    def remove_server_config(self, guild_id: str):
        """Remove configuration for a server (when bot leaves)"""
        if guild_id in self.configs:
            del self.configs[guild_id]
            self._save_configs()

    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all server configurations"""
        return self.configs.copy()

"""
read and write some option in toml file settings
"""
import os
import toml

DB_NAME = ""

with open(f"/home/{os.getlogin()}/.config/lightDB/settings.toml",
          mode="r", encoding='utf-8') as file:
    toml_settings = file.read()
settings = toml.loads(toml_settings)


def change_setting(setting_path, setting_name, setting_value):
    """change someone in toml file"""
    settings[setting_path][setting_name] = setting_value
    with open(f"/home/{os.getlogin()}/.config/lightDB/settings.toml",
              mode="w", encoding="utf-8") as file_toml:
        toml.dump(settings, file_toml)


def change_setting_style(setting_parent, setting_path, setting_name, setting_value):
    """change style setting in toml file"""
    settings[setting_parent][setting_path][0][setting_name] = setting_value
    with open(f"/home/{os.getlogin()}/.config/lightDB/settings.toml",
              mode="w", encoding="utf-8") as file_toml:
        toml.dump(settings, file_toml)

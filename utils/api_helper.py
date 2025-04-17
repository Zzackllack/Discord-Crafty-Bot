import json
import requests

def load_config():
    """Load configuration from config.json"""
    try:
        with open("config.json", "r") as config_file:
            return json.load(config_file)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def get_headers():
    """Get common headers for API calls"""
    config = load_config()
    CRAFTY_API_TOKEN = config.get("crafty_api_token")
    return {
        "Authorization": f"Bearer {CRAFTY_API_TOKEN}",
        "Content-Type": "application/json",
    }

def get_api_url():
    """Get the Crafty API URL from config"""
    config = load_config()
    return config.get("crafty_api_url", "https://localhost:8443/api/v2")

def get_server_info(server_id):
    """Get information about a specific server"""
    try:
        response = requests.get(
            f"{get_api_url()}/servers/{server_id}", 
            headers=get_headers(), 
            verify=False
        )
        return response.json()
    except Exception as e:
        print(f"Error getting server info: {e}")
        return {"status": "error", "message": str(e)}

def get_server_stats(server_id):
    """Get statistics for a specific server"""
    try:
        response = requests.get(
            f"{get_api_url()}/servers/{server_id}/stats", 
            headers=get_headers(), 
            verify=False
        )
        return response.json()
    except Exception as e:
        print(f"Error getting server stats: {e}")
        return {"status": "error", "message": str(e)}

def get_server_logs(server_id, params=None):
    """Get logs for a specific server"""
    if params is None:
        params = {"raw": "true", "file": "true"}
    
    try:
        response = requests.get(
            f"{get_api_url()}/servers/{server_id}/logs",
            headers=get_headers(),
            params=params,
            verify=False,
        )
        return response.json()
    except Exception as e:
        print(f"Error getting server logs: {e}")
        return {"status": "error", "message": str(e)}

def server_action(server_id, action):
    """Perform an action on a server (start, stop, etc.)"""
    try:
        response = requests.post(
            f"{get_api_url()}/servers/{server_id}/action/{action}",
            headers=get_headers(),
            verify=False,
        )
        return response.json()
    except Exception as e:
        print(f"Error performing server action: {e}")
        return {"status": "error", "message": str(e)}

def get_all_servers():
    """Get list of all available servers"""
    try:
        response = requests.get(
            f"{get_api_url()}/servers", 
            headers=get_headers(), 
            verify=False
        )
        return response.json()
    except Exception as e:
        print(f"Error getting servers: {e}")
        return {"status": "error", "message": str(e)}

def get_backup_info(server_id):
    """Get backup information for a specific server"""
    try:
        response = requests.get(
            f"{get_api_url()}/servers/{server_id}/backups",
            headers=get_headers(),
            verify=False,
        )
        return response.json()
    except Exception as e:
        print(f"Error getting backup info: {e}")
        return {"status": "error", "message": str(e)}

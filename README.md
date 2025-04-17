# Discord Crafty Bot  

![Discord Crafty Bot](https://img.shields.io/badge/Discord-Bot-blue?style=for-the-badge&logo=discord)  
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)  
![License](https://img.shields.io/badge/License-BSD3-green?style=for-the-badge)  

A sleek and modern Discord bot designed to interact with the Crafty Controller API, providing seamless server management for Minecraft servers.  

## 🚀 Features

- **Server Management**: Start, stop, and monitor your Minecraft servers directly from Discord.  
- **Real-Time Logs**: Fetch and display the latest server logs in Discord.  
- **Server Info**: Get detailed information about your servers, including status, IP, and more.  
- **Server List**: View all available servers managed by Crafty Controller.  
- **Customizable Commands**: Easily extend and modify commands to suit your needs.  

## 🛠️ Installation

### Prerequisites
- Python 3.10+  
- A Discord bot token ([Get one here](https://discord.com/developers/applications))  
- Crafty Controller API credentials  

### Steps

1. Clone the repository:
    ```bash  
    git clone https://github.com/zzackllack/Discord-Crafty-Bot.git  
    cd Discord-Crafty-Bot  
    ```  

2. Install dependencies:
    ```bash  
    pip install -r requirements.txt  
    ```  

3. Configure the bot:
    - Copy `config.example.json` to `config.json`.
    - Fill in your `discord_token`, `crafty_api_token`, and `crafty_api_url`.

4. Run the bot:
    ```bash
    python main.py
    ```  

## 📚 Commands

| Command         | Description                                   | Example Usage                |  
|------------------|-----------------------------------------------|------------------------------|  
| `/servers`       | List all available Minecraft servers.         | `/servers`                   |  
| `/serverinfo`    | Get detailed information about a server.      | `/serverinfo <server_id>`    |  
| `/start`         | Start a Minecraft server.                    | `/start <server_id>`         |  
| `/stop`          | Stop a Minecraft server.                     | `/stop <server_id>`          |  
| `/logs`          | Fetch the latest logs of a server.           | `/logs <server_id> <lines>`  |
| `/backup`        | Create a backup of a server.                  | `/backup <server_id>`        |

## 🧩 Project Structure

```plaintext  
Discord-Crafty-Bot/  
├── commands/          # Command modules for the bot  
├── utils/             # Utility functions and API helpers  
├── main.py            # Main entry point for the bot  
├── config.json        # Configuration file (user-provided)  
├── requirements.txt   # Python dependencies  
└── README.md          # Project documentation  
```  

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the bot.  

## 📄 License

This project is licensed under the BSD 3-Clause License. See the [LICENSE](LICENSE) file for details.  

## 🌟 Acknowledgments

- [Crafty Controller](https://github.com/crafty-controller/crafty-4) for the amazing API.  
- [discord.py](https://discordpy.readthedocs.io/) for the robust Discord library.  

🎉 **Enjoy managing your Minecraft servers with Discord!**  
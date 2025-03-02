import unittest
from unittest.mock import MagicMock
from requests import patch

from bot import servers
from unittest.mock import MagicMock, patch
from discord import Interaction


class TestServersCommand(unittest.TestCase):

    @patch('bot.requests.get')
    @patch('bot.discord.Interaction.response.send_message')
    async def test_servers_success(self, mock_send_message, mock_requests_get):
        # Mock the API response for successful retrieval of servers
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "ok",
            "data": [
                {
                    "server_name": "Test Server",
                    "server_id": "123",
                    "type": "Vanilla",
                    "running": True
                }
            ]
        }
        mock_requests_get.return_value = mock_response

        # Create a mock interaction
        mock_interaction = MagicMock(spec=Interaction)

        # Call the servers function
        await servers(mock_interaction)

        # Assert that send_message was called with the expected embed
        self.assertTrue(mock_send_message.called)
        args, kwargs = mock_send_message.call_args
        embed = args[0]
        self.assertIn("Available Minecraft Servers", embed.title)
        self.assertIn("Test Server", embed.fields[0].name)

    @patch('bot.requests.get')
    @patch('bot.discord.Interaction.response.send_message')
    async def test_servers_no_servers(self, mock_send_message, mock_requests_get):
        # Mock the API response for no servers found
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "ok",
            "data": []
        }
        mock_requests_get.return_value = mock_response

        # Create a mock interaction
        mock_interaction = MagicMock(spec=Interaction)

        # Call the servers function
        await servers(mock_interaction)

        # Assert that send_message was called with "No servers found."
        mock_send_message.assert_called_once_with("No servers found.")

    @patch('bot.requests.get')
    @patch('bot.discord.Interaction.response.send_message')
    async def test_servers_failed_retrieval(self, mock_send_message, mock_requests_get):
        # Mock the API response for failed retrieval of servers
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "error"
        }
        mock_requests_get.return_value = mock_response

        # Create a mock interaction
        mock_interaction = MagicMock(spec=Interaction)

        # Call the servers function
        await servers(mock_interaction)

        # Assert that send_message was called with "Failed to retrieve servers."
        mock_send_message.assert_called_once_with("Failed to retrieve servers.")

    @patch('bot.requests.get')
    @patch('bot.discord.Interaction.response.send_message')
    async def test_servers_exception_handling(self, mock_send_message, mock_requests_get):
        # Mock the API response to raise an exception
        mock_requests_get.side_effect = Exception("API Error")

        # Create a mock interaction
        mock_interaction = MagicMock(spec=Interaction)

        # Call the servers function
        await servers(mock_interaction)

        # Assert that send_message was called with the error message
        mock_send_message.assert_called_once_with("Error retrieving servers: API Error")

if __name__ == '__main__':
    unittest.main()
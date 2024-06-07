import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from service import RealTimeService
import aiohttp

class TestRealTimeService(unittest.IsolatedAsyncioTestCase):

    @patch('aiohttp.ClientSession.get')
    async def test_get_data_from_service_1(self, mock_get):
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'distance': 100,
            'altitude': 200,
            'air_temperature': 25
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        service = RealTimeService('http://service1.example.com/data', 'http://targetsystem.example.com/receive')
        async with aiohttp.ClientSession() as session:
            service.session = session
            data = await service.get_data_from_service_1()

        self.assertEqual(data, {
            'distance': 100,
            'altitude': 200,
            'air_temperature': 25
        })

    def test_calculate_fuel_cost(self):
        service = RealTimeService('http://service1.example.com/data', 'http://targetsystem.example.com/receive')
        fuel_cost = service.calculate_fuel_cost(100, 200, 25)
        self.assertAlmostEqual(fuel_cost, 10.5)

    @patch('aiohttp.ClientSession.post')
    async def test_send_data_to_target_system(self, mock_post):
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        service = RealTimeService('http://service1.example.com/data', 'http://targetsystem.example.com/receive')
        async with aiohttp.ClientSession() as session:
            service.session = session
            await service.send_data_to_target_system({'key': 'value'})

        mock_post.assert_called_once_with('http://targetsystem.example.com/receive', json={'key': 'value'})

if __name__ == '__main__':
    unittest.main()

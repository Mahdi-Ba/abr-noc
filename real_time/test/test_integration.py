import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from tasks import calculate_fuel_cost_task
from service import RealTimeService
import aiohttp


class TestIntegrationRealTimeService(unittest.IsolatedAsyncioTestCase):

    @patch('aiohttp.ClientSession.get')
    @patch('service.app.send_task')
    async def test_service_integration(self, mock_send_task, mock_get):
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'distance': 100,
            'altitude': 200,
            'air_temperature': 25
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        mock_task = AsyncMock()
        mock_task.get.return_value = calculate_fuel_cost_task(100, 200, 25)
        mock_send_task.return_value = mock_task

        service = RealTimeService('http://service1.example.com/data', 'http://targetsystem.example.com/receive')

        async with aiohttp.ClientSession() as session:
            service.session = session
            data = await service.get_data_from_service_1()
            self.assertEqual(data, {
                'distance': 100,
                'altitude': 200,
                'air_temperature': 25
            })

            task = service.app.send_task('tasks.calculate_fuel_cost_task', args=(100, 200, 25))
            fuel_cost = await task.get()

            self.assertAlmostEqual(fuel_cost, 10.5)


if __name__ == '__main__':
    unittest.main()

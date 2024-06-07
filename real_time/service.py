import logging
import aiohttp
import asyncio
from tasks import app

# Set up the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# mock endpoints for Service 1 and the target system
SERVICE_1_URL = 'http://service1.example.com/data'
TARGET_SYSTEM_URL = 'http://targetsystem.example.com/receive'

class RealTimeService:
    def __init__(self, service1_url, target_url):
        self.service1_url = service1_url
        self.target_url = target_url
        self.session = None

    async def get_data_from_service_1(self):
        try:
            async with self.session.get(self.service1_url) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching data from Service 1: {e}")
            return None

    async def send_data_to_target_system(self, data):
        try:
            async with self.session.post(self.target_url, json=data) as response:
                response.raise_for_status()
                logger.info("Data successfully sent to the target system")
        except aiohttp.ClientError as e:
            logger.error(f"Error sending data to the target system: {e}")

    async def run(self):
        async with aiohttp.ClientSession() as session:
            self.session = session
            while True:
                data = await self.get_data_from_service_1()
                if data:
                    distance = data.get('distance')
                    altitude = data.get('altitude')
                    air_temperature = data.get('air_temperature')

                    if distance is not None and altitude is not None and air_temperature is not None:
                        task = app.send_task('tasks.calculate_fuel_cost_task', args=(distance, altitude, air_temperature))
                        fuel_cost = await task.get()

                        processed_data = {
                            'distance': distance,
                            'altitude': altitude,
                            'air_temperature': air_temperature,
                            'fuel_cost': fuel_cost
                        }
                        await self.send_data_to_target_system(processed_data)
                    else:
                        logger.error("Incomplete data received from Service 1")
                else:
                    logger.error("Failed to retrieve data from Service 1")

                await asyncio.sleep(1)

if __name__ == '__main__':
    service = RealTimeService(SERVICE_1_URL, TARGET_SYSTEM_URL)
    asyncio.run(service.run())

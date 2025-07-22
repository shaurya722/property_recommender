import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Property, PropertyInterest, CustomUser
from .pinecone_client import search_properties_in_index

class PropertyWatchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    @database_sync_to_async
    def process_watch(self, user_id, property_id, watch_time):
        try:
            user = CustomUser.objects.get(id=user_id)
            prop = Property.objects.get(id=property_id)
        except (CustomUser.DoesNotExist, Property.DoesNotExist):
            return {'error': 'User or Property not found'}

        interested = False
        if watch_time >= 10:
            PropertyInterest.objects.update_or_create(
                user=user,
                property=prop,
                defaults={"watch_time": watch_time}
            )
            interested = True
        pinecone_results = search_properties_in_index(prop.description)
        recommendations = pinecone_results.get('matches', [])
        return {
            "status": "tracked",
            "interested": interested,
            "recommendations": recommendations
        }

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_id = data.get('user_id')
        property_id = data.get('property_id')
        watch_time = data.get('watch_time')
        if not user_id or not property_id or watch_time is None:
            await self.send(text_data=json.dumps({"error": "user_id, property_id, and watch_time are required"}))
            return
        result = await self.process_watch(user_id, property_id, watch_time)
        await self.send(text_data=json.dumps(result)) 
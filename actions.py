# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import requests
import json

from typing import Dict, Text, Any, List

from rasa_core_sdk import ActionExecutionRejection
from rasa_core_sdk import Tracker
from rasa_core_sdk.events import SlotSet
from rasa_core_sdk.executor import CollectingDispatcher
from rasa_core_sdk import Action
from rasa_core_sdk.forms import FormAction, REQUESTED_SLOT


logger = logging.getLogger(__name__)


class ActionJoke(Action):
    def name(self):
        # define the name of the action which can then be included in training stories
        return "action_joke"

    def run(self, dispatcher, tracker, domain):
        # what your action should do
        request = json.loads(requests.get(
            'http://api.laifudao.com/open/xiaohua.json').text)  # make an api call
        # extract a joke from returned json response
        joke = request[16]['content']
        dispatcher.utter_message(joke)  # send the message back to the user
        return []


class RestaurantForm(FormAction):

    def name(self):
        # type: () -> Text
        return 'restaurant_form'

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ['food', 'price', 'area']

    def slot_mappings(self):

        return {
            'food': self.from_entity(entity='food'),
            'price': self.from_entity(entity='price'),
            'area': self.from_entity(entity='area')
        }

    def validate(self,
                 dispatcher: CollectingDispatcher,
                 tracker: Tracker,
                 domain: Dict[Text, Any]) -> List[Dict]:
        slots_values = self.extract_other_slots(dispatcher, tracker, domain)
        slot_to_fill = tracker.get_slot(REQUESTED_SLOT)
        if slot_to_fill:
            slots_values.update(self.extract_requested_slot(dispatcher, tracker,
                                                            domain))
            if not slots_values:
                raise ActionExecutionRejection(self.name(),
                                               "Failed to validate slot {0} \
                                               with action {1}"
                                               .format(slot_to_fill,
                                                       self.name))

        return [SlotSet(slot, value) for slot, value in slots_values.items()]

    def submit(self, dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict]:
        return []


class ActionRestaurant(Action):
    def name(self):
        # define the name of the action which can then be included in training
        # stories
        return "action_restaurant"

    def run(self, dispatcher, tracker, domain):
        # what your action should do
        fd = open("./data/restaurant.json")
        restaurant_db = json.load(fd)
        for item in restaurant_db:
            if item['price_range'] == tracker.get_slot('price') and \
               item['tag'] == tracker.get_slot('food') and \
               item['area'] == tracker.get_slot('area'):
                dispatcher.utter_message('已经为你找到{}，请问还有什么要求吗？'.format(item['name']))
        return []

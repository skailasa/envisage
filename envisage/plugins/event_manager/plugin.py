#
#
# (C) Copyright 2011 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in LICENSE.txt
#
""" This module provides a plugin which adds an EventManager instance as
a service to the application.

"""

# Enthought library imports.
from envisage.api import Plugin, ServiceOffer
from traits.api import List

EVENT_MANAGER_PROTOCOL = 'encore.events.abstract_event_manager.BaseEventManager'

class EventManagerPlugin(Plugin):
    """ Plugin to add event manager to the application. """

    id = 'envisage.event_manager'

    SERVICE_OFFERS = 'envisage.service_offers'
    service_offers = List(contributes_to=SERVICE_OFFERS)

    def _service_offers_default(self):
        evt_mgr_service_offer = ServiceOffer(
            protocol   = EVENT_MANAGER_PROTOCOL,
            factory    = lambda: self._create_event_manager,
        )
        return [evt_mgr_service_offer]

    def _create_event_manager(self):
        from encore.events.event_manager import EventManager
        return EventManager()

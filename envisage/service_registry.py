""" The service registry. """


# Standard library imports.
import logging

# Enthought library imports.
from traits.api import (
    Dict, Event, HasTraits, Int, Interface, provides, Undefined
)
from traits.util.deprecated import deprecated

# Local imports.
from i_service_registry import IServiceRegistry
from import_manager import ImportManager


# Logging.
logger = logging.getLogger(__name__)


class NoSuchServiceError(Exception):
    """ Raised when a required service is not found. """


@provides(IServiceRegistry)
class ServiceRegistry(HasTraits):
    """ The service registry. """

    ####  IServiceRegistry interface ##########################################

    # An event that is fired when a service is registered.
    registered = Event(Int)

    # An event that is fired when a service is unregistered.
    unregistered = Event(Int)

    ####  Private interface ###################################################

    # Services registered by *name* (aka the 'White Pages').
    #
    # { service_id : (name, obj, properties) }
    #
    # where:
    #
    # 'name' is the service name.
    #
    # 'obj' is the object that is registered (any old, Python object!).
    #
    # 'properties' is the arbitrary dictionary of properties that were
    # registered with the object.
    _named_services = Dict

    # Services registered by *protocol* (aka the 'Yellow Pages').
    #
    # { service_id : (protocol_name, obj, properties) }
    #
    # where:
    #
    # 'protocol_name' is the (possible dotted) name of the interface, type or
    # class that the object is registered against.
    #
    # 'obj' is the object that is registered (any old, Python object!).
    #
    # 'properties' is the arbitrary dictionary of properties that were
    # registered with the object.
    _services = Dict

    # The next service Id (service Ids are never persisted between process
    # invocations so this is simply an ever increasing integer!).
    _service_id = Int

    ###########################################################################
    # 'IServiceRegistry' interface.
    ###########################################################################

    def get_required_service(self, protocol, query='', minimize='',maximize=''):
        """ Return the first service that matches the specified query. """

        service = self.get_service(protocol, query, minimize, maximize)
        if service is None:
            raise NoSuchServiceError(protocol)

        return service

    def get_service(self, protocol, query='', minimize='', maximize=''):
        """ Return the first service service that matches the specified query.

        """

        services = self.get_services(protocol, query, minimize, maximize)
        if len(services) > 0:
            service = services[0]

        else:
            service = None

        return service

    def get_service_by_name(self, name):
        """ Return the service with the given name. """

        for service_id, (offer_name, obj, properties) in \
            self._named_services.iteritems():
            if offer_name == name:
                break

        else:
            return None

        # Is the registered service actually a service *factory*?
        if self._is_service_factory(obj):
            # Use the factory to create the actiual service object.
            obj = self._get_object_from_factory(obj, properties)

            # The resulting service object replaces the factory in the cache
            # (i.e. the factory will not get called again unless it is
            # unregistered first).
            self._named_services[service_id] = (name, obj, properties)

        return obj

    def get_service_by_id(self, service_id):
        """ Return the service with the specified id. """

        if service_id in self._services:
            protocol, obj, properties = self._services[service_id]

        elif service_id in self._named_services:
            name, obj, properties = self._named_services[service_id]

        else:
            raise ValueError('no service with id <%d>' % service_id)

        return obj

    @deprecated('use "get_service_by_id"')
    def get_service_from_id(self, service_id):
        """ Return the service with the specified id. """

        return self.get_service_by_id(service_id)

    def get_services(self, protocol, query='', minimize='', maximize=''):
        """ Return all services that match the specified query. """

        services = []
        for service_id, (protocol_name, obj, properties) \
            in self._services.items():
            if self._get_protocol_name(protocol) == protocol_name:
                # If the protocol is a string then we need to import it!
                if isinstance(protocol, basestring):
                    actual_protocol = ImportManager().import_symbol(protocol)

                # Otherwise, it is an actual protocol, so just use it!
                else:
                    actual_protocol = protocol

                # If the registered service is actually a factory then use it
                # to create the actual object.
                obj = self._resolve_factory(
                    actual_protocol, protocol_name, obj, properties, service_id
                )

                # If a query was specified then only add the service if it
                # matches it!
                if len(query) == 0 or self._eval_query(obj, properties, query):
                    services.append(obj)

        # Are we minimizing or maximising anything? If so then sort the list
        # of services by the specified attribute/property.
        if minimize != '':
            services.sort(None, lambda x: getattr(x, minimize))

        elif maximize != '':
            services.sort(None, lambda x: getattr(x, maximize), reverse=True)

        return services

    def get_service_properties(self, service_id):
        """ Return the dictionary of properties associated with a service. """

        if service_id in self._services:
            protocol, obj, properties = self._services[service_id]

        elif service_id in self._named_services:
            name, obj, properties = self._services[service_id]

        else:
            raise ValueError('no service with id <%d>' % service_id)

        return properties.copy()

    def register_service(self, protocol, obj, properties=None):
        """ Register a service. """

        protocol_name = self._get_protocol_name(protocol)

        # Make sure each service gets its own properties dictionary.
        if properties is None:
            properties = {}

        service_id = self._next_service_id()
        self._services[service_id] = (protocol_name, obj, properties)
        self.registered = service_id

        logger.debug('service <%d> registered %s', service_id, protocol_name)

        return service_id

    def register_service_by_name(self, name, obj, properties=None):
        """ Register a service by name. """

        # Make sure each service gets its own properties dictionary.
        if properties is None:
            properties = {}

        service_id = self._next_service_id()
        self._named_services[service_id] = (name, obj, properties)
        self.registered = service_id

        logger.debug('service <%d> registered by name %s', service_id, name)

        return service_id

    def set_service_properties(self, service_id, properties):
        """ Set the dictionary of properties associated with a service. """

        if service_id in self._services:
            protocol, obj, old_properties = self._services[service_id]
            self._services[service_id] = (protocol, obj, properties)

        elif service_id in self._named_services:
            name, obj, old_properties = self._named_services[service_id]
            self._named_services[service_id] = (name, obj, properties)

        else:
            raise ValueError('no service with id <%d>' % service_id)

        return

    def unregister_service(self, service_id):
        """ Unregister the service with the given Id. """

        if service_id in self._services:
            self._services.pop(service_id)

        elif service_id in self._named_services:
            self._named_services.pop(service_id)

        else:
            raise ValueError('no service with id <%d>' % service_id)

        self.unregistered = service_id
        logger.debug('service <%d> unregistered', service_id)

        return

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _create_namespace(self, service, properties):
        """ Create a namespace in which to evaluate a query. """

        namespace = {}
        namespace.update(service.__dict__)
        namespace.update(properties)

        return namespace

    def _eval_query(self, service, properties, query):
        """ Evaluate a query over a single service.

        Return True if the service matches the query, otherwise return False.

        """

        namespace = self._create_namespace(service, properties)
        try:
            result = eval(query, namespace)

        except:
            result = False

        return result

    def _get_object_from_factory(self, factory, properties):
        """ Use the given factory to create the actual service object. """

        # A service factory is any callable that takes the (possibly empty)
        # dictionary of properties as *keyword* arguments.
        #
        # If the factory is specified as a symbol path then import it.
        if isinstance(factory, basestring):
            factory = ImportManager().import_symbol(factory)

        return factory(**properties)

    def _get_protocol_name(self, protocol_or_name):
        """ Returns the full class name for a protocol. """

        if isinstance(protocol_or_name, basestring):
            name = protocol_or_name

        else:
            name = '%s.%s' % (
                protocol_or_name.__module__, protocol_or_name.__name__
            )

        return name

    def _is_service_factory(self, obj, protocol=None):
        """ Is the object actually a *factory* for the service object? """

        # fixme: We should have had a formal notion of service factory with an
        # appropriate API so that we can *definitely* tell whether or not an
        # object is a factory!
        #
        # Instead we make the following 'best guesses':-
        #
        # For objects registered by protocol, we look to see if the object
        # is an instance of the protocol, and if *not* assume it is a factory
        # for one that does. This is not too bad, but...
        #
        # For objects registered by name, we don't even have a protocol to
        # check for, so we look to see if the object is callable and, if it is,
        # assume it is a factory. Of course this will break if your actual
        # service object is callable (i.e. implements __call__)!
        if protocol is not None:
            is_service_factory = not isinstance(obj, protocol)

        else:
            is_service_factory = callable(obj)

        return is_service_factory

    def _next_service_id(self):
        """ Returns the next service ID. """

        self._service_id += 1

        return self._service_id

    def _resolve_factory(
        self, protocol, protocol_name, obj, properties, service_id
    ):
        """ If 'obj' is a factory then use it to create the actual service. """

        # Is the registered service actually a service *factory*?
        if self._is_service_factory(obj, protocol):
            # Use the factory to create the actiual service object.
            obj = self._get_object_from_factory(obj, properties)

            # The resulting service object replaces the factory in the cache
            # (i.e. the factory will not get called again unless it is
            # unregistered first).
            self._services[service_id] = (protocol_name, obj, properties)

        return obj

#### EOF ######################################################################

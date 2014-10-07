""" The service registry interface. """


# Enthought library imports.
from traits.api import Event, Int, Interface


class IServiceRegistry(Interface):
    """ The service registry interface.

    Services are the real 'guts' of an Envisage application -- they are the
    objects that do the actual work! To get the job done, services obviously
    need to interact, and so Envisage provides a way for them to find each
    other. This is where the *service registry* comes in.

    Don't be fazed by the term *service*. In Envisage it just means any objects
    in your application that you want to share between plugins. Services can be
    any Python object and do not have to inherit from any Envisage class or even
    implement any particular interface!

    There are two different ways to publish your services, depending on how
    you would want clients to use them:-

    1) The 'Yellow Pages' (IServiceRegistry.register_service).

    The first way is a 'Yellow Pages' style mechanism where services are
    published and looked up by protocol (meaning, *interface*, *type*, or
    *class* (for old-style classes!).

    It is called a 'Yellow Pages' mechanism because it is just like looking up
    a telephone number in the 'Yellow Pages' phone book. You use the
    'Yellow Pages' instead of the 'White Pages' when you don't know the *name*
    of the specific person you want to call but you do know what *kind*,
    of service you require. For example, if you have a leaking pipe, you know
    you need a plumber, so you pick up your 'Yellow Pages', go to the
    'Plumbers' section and choose one that seems to fit the bill based on
    price, location, certification, etc. The service registry does exactly
    the same thing as the 'Yellow Pages', only with objects.

    Use the 'Yellow Pages' style (via the 'register_service' method) if you
    have many objects that provide the same function and your client's don't
    care about which specific one they get when they do a lookup (via the
    'get_service(s)' methods). For example, you might have multiple objects that
    offer some compute service (say 'IComputeService'). Clients that need the
    service don't care which one they get, they just need somebody to execute
    some code for them. You could even put the 'cpu load' (for example) as a
    property of the service and then clients can query for the least busy
    'IComputeService' object.

    2) The 'White Pages' (IServiceRegistry.register_service_by_name)

    The second way is a 'White Pages' style mechanism, where services are
    published and looked up by (some arbitrary) name (e.g. 'event_manager').

    This is just like the real 'White Pages', where you already know the name
    of the specific person that you want to contact, and so you can simply
    look it up. This is just a flat (think dictionary) namespace, and so it is
    common to use names such as 'enthought/event_manager' to emulate a naming
    hierarchy.

    Use the 'White Pages' style (via the 'register_service_by_name' method) if
    you have a single, well-known object that provides a particular service.

    """

    # An event that is fired when a service is registered.
    #
    # The value of the event is the Id of the service that was registered.
    registered = Event(Int)

    # An event that is fired when a service is unregistered.
    #
    # The value of the event is the Id of the service that was unregistered.
    unregistered = Event(Int)

    def get_required_service(self, protocol, query='', minimize='',maximize=''):
        """ Return the first service that matches the specified query.

        Raise a 'NoSuchServiceError' exception if no such service exists.

        """

    def get_service(self, protocol, query='', minimize='', maximize=''):
        """ Return the first service that matches the specified query.

        The protocol can be an actual class or interface, or the *name* of a
        class or interface in the form '<module_name>.<class_name>'.

        Return None if no such service is found.

        If no query is specified then a service that provides the specified
        protocol is returned (if one exists).

        NOTE: If more than one service exists that match the criteria then
        Don't try to guess *which* one it will return - it is random!

        """

    def get_service_by_name(self, name):
        """ Return the service with the given name.

        Return None if no such service is found.

        """

    def get_service_by_id(self, service_id):
        """ Return the service with the specified id.

        If no such service exists a 'ValueError' exception is raised.

        """

    # Deprecated: Use 'get_service_by_id'
    def get_service_from_id(self, service_id):
        """ Return the service with the specified id.

        If no such service exists a 'ValueError' exception is raised.

        """

    def get_services(self, protocol, query='', minimize='', maximize=''):
        """ Return all services that match the specified query.

        The protocol can be an actual class or interface, or the *name* of a
        class or interface in the form '<module_name>.<class_name>'.

        If no services match the query, then an empty list is returned.

        If no query is specified then all services that provide the specified
        protocol are returned (if any exist).

        """

    def get_service_properties(self, service_id):
        """ Return the dictionary of properties associated with a service.

        If no such service exists a 'ValueError' exception is raised.

        The properties returned are 'live' i.e. changing them immediately
        changes the service registration.

        """

    def register_service(self, protocol, obj, properties=None):
        """ Register a service.

        The protocol can be an actual class or interface, or the *name* of a
        class or interface in the form::

            'foo.bar.baz'

        Which is turned into the equivalent of an import statement that
        looks like::

            from foo.bar import baz

        Return a service Id that can be used to unregister the service and to
        get/set any service properties.

        If 'obj' does not implement the specified protocol then it is treated
        as a 'service factory' that will be called the first time a service of
        the appropriate type is requested. A 'service factory' is simply a
        callable that takes the properties specified here as keyword arguments
        and returns an object. For *really* lazy loading, the factory can also
        be specified as a string which is used to import the callable.

        """

    def register_service_by_name(self, name, obj, properties=None):
        """ Register a service by name.

        Return a service Id that can be used to unregister the service and to
        get/set any service properties.

        If 'obj' is callable then it is treated as a 'service factory' that
        will be called the first time the service is looked up. A 'service
        factory' is simply a callable that takes the properties specified here
        as keyword arguments and returns an object. For *really* lazy loading,
        the factory can also be specified as a string which is used to import
        the callable.

        """

    def set_service_properties(self, service_id, properties):
        """ Set the dictionary of properties associated with a service.

        If no such service exists a 'ValueError' exception is raised.

        """

    def unregister_service(self, service_id):
        """ Unregister the service with the given Id.

        If no such service exists a 'ValueError' exception is raised.

        """

#### EOF ######################################################################

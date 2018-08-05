"""Cement core hooks module."""

import operator
import types
from ..core import exc
from ..utils.misc import minimal_logger

LOG = minimal_logger(__name__)


class HookManager(object):
    """
    Manages the hook system to define, get, run, etc hooks within the
    the Cement Framework and applications Built on Cement (tm).

    """

    def __init__(self, app):
        self.app = app
        self.__hooks__ = {}

    def list(self):
        """
        List all defined hooks.

        Returns:
            hooks (list): List of registered hook labels.
        """
        return list(self.__hooks__.keys())

    def define(self, name):
        """
        Define a hook namespace that the application and plugins can register
        hooks in.

        Args:
            name (str): The name of the hook, stored as hooks['name']

        Raises:
            cement.core.exc.FrameworkError: If the hook name is already
                defined

        Example:

            .. code-block:: python

                from cement import App

                with App('myapp') as app:
                    app.hook.define('my_hook_name')

        """
        LOG.debug("defining hook '%s'" % name)
        if name in self.__hooks__:
            raise exc.FrameworkError("Hook name '%s' already defined!" % name)
        self.__hooks__[name] = []

    def defined(self, hook_name):
        """
        Test whether a hook name is defined.

        Args:
            hook_name (str): The name of the hook.
                I.e. ``my_hook_does_awesome_things``.

        Returns:
            bool: ``True`` if the hook is defined, ``False`` otherwise.

        Example:

            .. code-block:: python

                from cement import App

                with App('myapp') as app:
                    app.hook.defined('some_hook_name'):
                        # do something about it
                        pass

        """
        if hook_name in self.__hooks__:
            return True
        else:
            return False

    def register(self, name, func, weight=0):
        """
        Register a function to a hook.  The function will be called, in order
        of weight, when the hook is run.

        Args:
            name (str): The name of the hook to register too.
                I.e. ``pre_setup``, ``post_run``, etc.
            func (function): The function to register to the hook.  This is an
            *un-instantiated*, non-instance method, simple function.

        Keywork Args:
            weight (int):  The weight in which to order the hook function.

        Example:

            .. code-block:: python

                from cement import App

                def my_hook_func(app):
                    # do something with app?
                    return True

                with App('myapp') as app:
                    app.hook.define('my_hook_name')
                    app.hook.register('my_hook_name', my_hook_func)

        """
        if name not in self.__hooks__:
            LOG.debug("hook name '%s' is not defined! ignoring..." % name)
            return False

        LOG.debug("registering hook '%s' from %s into hooks['%s']" %
                  (func.__name__, func.__module__, name))

        # Hooks are as follows: (weight, name, func)
        self.__hooks__[name].append((int(weight), func.__name__, func))

    def run(self, name, *args, **kwargs):
        """
        Run all defined hooks in the namespace.

        Args:
            name (str): The name of the hook function.
            args (tuple): Additional arguments to be passed to the hook
                functions.
            kwargs (dict): Additional keyword arguments to be passed to the
                hook functions.

        Yields:
            The result of each hook function executed.

        Raises:
            cement.core.exc.FrameworkError: If the hook ``name`` is not
                defined

        Example:

            .. code-block:: python

                from cement import App

                def my_hook_func(app):
                    # do something with app?
                    return True

                with App('myapp') as app:
                    app.hook.define('my_hook_name')
                    app.hook.register('my_hook_name', my_hook_func)
                    for res in app.hook.run('my_hook_name', app):
                        # do something with the result?
                        pass

        """
        if name not in self.__hooks__:
            raise exc.FrameworkError("Hook name '%s' is not defined!" % name)

        # Will order based on weight (the first item in the tuple)
        self.__hooks__[name].sort(key=operator.itemgetter(0))
        for hook in self.__hooks__[name]:
            LOG.debug("running hook '%s' (%s) from %s" %
                      (name, hook[2], hook[2].__module__))
            res = hook[2](*args, **kwargs)

            # Check if result is a nested generator - needed to support e.g.
            # asyncio
            if isinstance(res, types.GeneratorType):
                for _res in res:
                    yield _res
            else:
                yield res

"""
A client controlling a remote shell.
"""

# Enthought library imports
from enthought.traits.api import implements

# Local imports
from enthought.plugins.remote_editor.communication.client import Client
from i_remote_shell import IRemoteShell


class RemoteShellController(Client):
    """ A Client used to control a remote shell.
    """
    implements(IRemoteShell)

    # Client interface

    self_type = "python_editor"
    other_type = "python_shell"

    def run_file(self, path):
        self.send_command('run_file', path)

    def run_text(self, text):
        self.send_command('run_text', text)



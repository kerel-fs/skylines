from flask_script import Manager

from .merge import Merge
from .delete import Delete

manager = Manager(help="Perform operations related to user accounts")
manager.add_command('merge', Merge())
manager.add_command('delete', Delete())

import os 

if os.environ.get('MODE','DEV') == 'DEV':
    from .dev import * 

else:
    from .prod import *
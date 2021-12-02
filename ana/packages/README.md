## Logging Practices
We use the levels of the python logging package
- 'critical': channel bugs
- ‘error’ for user error
- 'info’ for platform logging/errors
- 'debug' for platform testing

Set the logger in all modules of lib/ and nodes/.  All node exec() methods should log themselves.

```
import logging

logger = logging.getLogger(__name__)

class XYZ(Node):
    """Implement a xyz node"""
    def exec(self):
        logger.info("Executing {}".format(self.name))
        ...
```

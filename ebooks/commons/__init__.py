'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''
import threading

# Local thread container instantiated here to be shared between all submodules in this package
# Note that thread.local() is not singleton!!!
# We use local thread container for sharing the transaction_id of request for logs
local_context = threading.local()

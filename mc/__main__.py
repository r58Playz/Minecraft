import mc.main
import sys
from mc.serverclient.native import tests, server
if sys.argv[-1] == 'client':
    mc.main.main()
elif sys.argv[-1] == 'server':
    mc.serverclient.native.server.start_server()
elif sys.argv[-1] == 'testcs':
    mc.serverclient.native.tests.test_pr()

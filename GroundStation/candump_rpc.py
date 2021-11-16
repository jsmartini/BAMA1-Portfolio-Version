from GS.Telemetry4.Comm import csp_init
from GS import *

cspinit(can=True)


BAMA1Cli().cmdloop()


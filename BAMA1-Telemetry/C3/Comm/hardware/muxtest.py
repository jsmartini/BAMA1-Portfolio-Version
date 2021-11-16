from mux import multiplex as mux
import os
x = mux(2)

for i in range(8):
	print(f"channel {i}")
	x.channel(i)
	print(os.popen(f"i2cdetect -r -y 2").read())

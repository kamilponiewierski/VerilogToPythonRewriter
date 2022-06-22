from verilogstructures import *
ReLU = Module(None, ['X'], ['Y'])
ReLU.add_wire("zero", Wire(1))
ReLU.assign("zero", 0)
ReLU.assign("Y", None, (("X", ">", 0), "X", 0))

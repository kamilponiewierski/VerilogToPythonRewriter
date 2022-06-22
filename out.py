from verilogstructures import *
delay = Module(None, ['clk', 'X'], ['Y'])
delay.add_register("ac", Register(1))
delay.assign("Y", "ac")
delay.add_synchronous_block(SynchronousBlock([], ['clk'], []))
delay.synchronous_block.add_procedure(synch_assign, ("ac", "X"))

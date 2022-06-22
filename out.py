from verilogstructures import *
ACC = Module(None, ['clk', 'X'], ['Y'])
ACC.add_register("acc", Register(1))
ACC.assign("Y", "acc")
ACC.add_synchronous_block(SynchronousBlock([], ['clk'], []))
ACC.synchronous_block.add_procedure(synch_assign, ("acc", binary_operator("acc", "+", "X")))

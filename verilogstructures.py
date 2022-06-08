# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 18:42:36 2022

@author: igor
"""
from typing import Dict, Tuple


def synch_assign(left_side, right_side):
    left_side[:] = right_side[:]


class SynchronousBlock:
    def __init__(self, sensitivity_list, posedge_signals, negedge_signals):
        self.sensitivity_list = sensitivity_list
        self._sensitivity_list_previous = sensitivity_list[:]

        self.pes = posedge_signals
        self.posedge_signals = posedge_signals
        self._posedge_signals_previous = posedge_signals[:]

        self.negedge_signals = negedge_signals
        self._negedge_signals_previous = negedge_signals[:]

        self.functions = []
        self.parameters = []

    def proceed(self) -> bool:
        t = False
        # for signal, Bsignal in zip(self.sensitivity_list, self._sensitivity_list_previous):
        #     if signal != Bsignal:
        #         t = True

        for signal, Bsignal in zip(self.posedge_signals, self._posedge_signals_previous):

            try:
                if signal > Bsignal:
                    t = True
            except:
                if [signal] > Bsignal:
                    t = True
        # for signal, Bsignal in zip(self.negedge_signals, self._negedge_signals_previous):
        #     if signal < Bsignal:
        #         t =  True

        return t

    def tick(self):
        self.posedge_signals = self.pes[0]

        z = self.proceed()
        if z:
            self.body()

        self._sensitivity_list_previous = self.sensitivity_list[:]
        self._posedge_signals_previous = self.posedge_signals[:]
        self._negedge_signals_previous = self.negedge_signals[:]

    def add_procedure(self, function, param):
        self.functions.append(function)
        self.parameters.append(param)

    def body(self):
        for func, params in zip(self.functions, self.parameters):
            func(*params)


class Wire:

    def __init__(self, size: int, channels: int = 1):
        self.size = size
        self.channels = channels
        self.wire = [0 for _ in range(self.size)]
        # self.wire = [[0 for _ in range(self.size)] for _ in range(self.channels)]

    def wire_connect(self):
        pass


class Register:

    def __init__(self, size: int, channels: int = 1):
        self.size = size
        self.channels = channels
        self.register = [0 for _ in range(self.size)]
        # self.register = [[0 for _ in range(self.size)] for _ in range(self.channels)]


class Module:
    def __init__(self, parameters, inputs, outputs):
        self.parameters = parameters
        self.inputs = inputs
        self.outputs = outputs

        self.module_left_side = tuple()
        self.module_right_side = tuple()

        self.synchronous_block = None

        self.module_wires: Dict[str, Wire] = {}
        self.module_registers = {}
        self.module_modules = {}

        self._initialize_wires()

    def _initialize_wires(self):
        for name, wire in self.inputs.items():
            self.module_wires[name] = wire
        for name, wire in self.outputs.items():
            self.module_wires[name] = wire

    def add_synchronous_block(self, block):
        self.synchronous_block = block

    # def add_synchronous_block(self, sensitivity_list_names, posedge_names, negedge_names):
    #     sl = [wire.wire for name, wire in self.module_wires if name in sensitivity_list_names]
    #     pl = [wire.wire for name, wire in self.module_wires if name in posedge_names]
    #     nl = [wire.wire for name, wire in self.module_wires if name in negedge_names]

    #     self.synchronous_block = SynchronousBlock(sl, pl, nl)       

    def add_wire(self, wire_name: str, wire: Wire):
        self.module_wires[wire_name] = wire

    def add_register(self, register_name: str, register: Register):
        self.module_registers[register_name] = register

    def add_module(self, module_name: str, module, connections):
        for port, wire in connections.items():
            module.module_wires[port].wire[0] = self.module_wires[wire].wire[0]
        self.module_modules[module_name] = module

    def assign(self, name_left, name_right):
        self.module_left_side += (self.module_wires[name_left].wire,)
        if name_right in self.module_registers.keys():
            self.module_right_side += (self.module_registers[name_right].register,)
        elif name_right in self.module_wires.keys():
            self.module_right_side += (self.module_wires[name_right].wire,)

    def step(self):
        self.synchronous_block.tick()
        for l, r in zip(self.module_left_side, self.module_right_side):
            l[0] = r[0]

    def behavioral_simulation(self, steps: int, input_wires_signals):
        result = []
        for i in range(steps):
            for key, value in input_wires_signals.items():
                self.module_wires[key].wire[0] = value[i]
            self.step()
            print(self.module_wires["Y"].wire[0])
            # print(self.module_registers["acc"].register[0])


input_wires = {
    "clk": [0, 1, 0, 1, 0, 1, 0, 1],
    "X": [0, 0, 1, 1, 0, 0, 0, 0]
}

delay = Module(None, {"X": Wire(1), "clk": Wire(1)}, {"Y": Wire(1)})
delay.add_register("acc", Register(1))

SB = SynchronousBlock([], [delay.module_wires["clk"].wire], [])
SB.add_procedure(synch_assign, (delay.module_registers["acc"].register, delay.module_wires["X"].wire))

delay.add_synchronous_block(SB)

delay.assign("Y", "acc")

delay.behavioral_simulation(8, input_wires)

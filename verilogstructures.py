# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 18:42:36 2022

@author: igor
"""
from typing import Dict


def synch_assign(left_side, right_side, arguments=None):
    if arguments is None:
        left_side[:] = right_side[:]
    else:
        left_side[:] = binary_operator(*arguments)


def condition(arg1, operator=None, arg2=None) -> bool:
    if operator is None:
        return bool(arg1)
    elif operator == ">":
        return arg1 > arg2
    elif operator == "<":
        return arg1 < arg2
    elif operator == "==":
        return arg1 == arg2
    elif operator == ">=":
        return arg1 >= arg2
    elif operator == "<=":
        return arg1 <= arg2


def binary_operator(arg1, operator, arg2):
    if operator == "-":
        return [arg1[0] - arg2[0]]
    elif operator == "+":
        return [arg1[0] + arg2[0]]
    elif operator == "&":
        return int(arg1 and arg2)
    elif operator == "|":
        return int(arg1 or arg2)


def tenary_operator(condition_args, true_proceedings, false_proceedings):
    return true_proceedings if condition(*condition_args) else false_proceedings


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

    def procced(self) -> bool:
        t = False
        for signal, Bsignal in zip(self.sensitivity_list, self._sensitivity_list_previous):
            try:
                if signal != Bsignal:
                    t = True
            except:
                if [signal] != Bsignal:
                    t = True

        for signal, Bsignal in zip(self.posedge_signals, self._posedge_signals_previous):
            try:
                if signal > Bsignal:
                    t = True
            except:
                if [signal] > Bsignal:
                    t = True
        for signal, Bsignal in zip(self.negedge_signals, self._negedge_signals_previous):
            try:
                if signal < Bsignal:
                    t = True
            except:
                if [signal] > Bsignal:
                    t = True
        return t

    def tick(self):
        self.posedge_signals = self.pes[0]

        z = self.procced()
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

    def __init__(self, size: int, channels: int = 1, value=0):
        self.size = size
        self.channels = channels
        self.wire = [value for _ in range(self.size)]
        # self.wire = [[0 for _ in range(self.size)] for _ in range(self.channels)]


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

    def add_wire(self, wire_name: str, wire: Wire):
        self.module_wires[wire_name] = wire

    def add_register(self, register_name: str, register: Register):
        self.module_registers[register_name] = register

    def add_module(self, module_name: str, module, connections):
        for port, wire in connections.items():
            module.module_wires[port].wire[0] = self.module_wires[wire].wire[0]
        self.module_modules[module_name] = module

    def assign(self, name_left, name_right, tenary_args=None):
        if tenary_args is None:
            self.module_left_side += (self.module_wires[name_left].wire,)
            if name_right in self.module_registers.keys():
                self.module_right_side += (self.module_registers[name_right].register,)
            elif name_right in self.module_wires.keys():
                self.module_right_side += (self.module_wires[name_right].wire,)
        else:
            self.module_left_side += (self.module_wires[name_left].wire,)
            self.module_right_side += (tenary_args,)

    def step(self):
        if self.synchronous_block is not None:
            self.synchronous_block.tick()

        for l_side, r in zip(self.module_left_side, self.module_right_side):
            try:
                l_side[0] = tenary_operator(
                    (self.module_wires[r[0][0]].wire[0], r[0][1], self.module_wires[r[0][2]].wire[0]),
                    self.module_wires[r[1]].wire[0],
                    self.module_wires[r[2]].wire[0])
            except:
                l_side[0] = r[0]

    def behavioral_simulation(self, steps: int, input_wires_signals):
        result = []
        for i in range(steps):
            for key, value in input_wires_signals.items():
                self.module_wires[key].wire[0] = value[i]
            self.step()
            result.append([self.module_wires[key].wire[0] for key, value in self.outputs.items()])
        return result

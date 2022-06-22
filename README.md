# Verilog To Python Rewriter

A lexer and parser of Verilog built using Python and PLY

## Requirements

[PLY 3.11](http://www.dabeaz.com/ply/) is used for the purpose of parsing the source file and is required to run this program.

## Command Line Usage

This rewriter can be run from the command line. In your terminal window, simply type:

```
main.py file_name
```

where file_name is path to verilog source file.

## Examples

Several examples are provided within the repository, under `examples` directory. 

`acc.txt` and `relu.txt` are basic examples of verilog modules which can be rewritten in Python.


Files prefaced with `fail` showcase error catching, both during lexing and parsing.

## Limitations

Currently, this program is able to rewrite one file at a time.

To comply with Python's limitations, verilog source files must follow given order, in short, the assignments go first, followed by wire/register declarations.


from magia import Module, Input, Output, Signal
from functools import reduce


class FullAdder(Module):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.io += [
            Input("a", 1),
            Input("b", 1),
            Input("cin", 1),
            Output("q", 1),
            Output("cout", 1),
        ]
        self.io.q <<= self.io.a ^ self.io.b ^ self.io.cin
        self.io.cout <<= self.io.a & self.io.b | (self.io.cin & (self.io.a & self.io.b))


class RCA(Module):
    def __init__(self, width, **kwargs):
        super().__init__(**kwargs)

        self.io += [
            Input("a", width),
            Input("b", width),
            Input("cin", 1),
            Output("q", width),
            Output("cout", 1),
        ]
        fa = FullAdder()
        carry = self.io.cin
        q = [Signal(1) for _ in range(width)]
        for i in range(width):
            fa_i = fa.instance(
                io={
                    "a": self.io.a[i],
                    "b": self.io.b[i],
                    "cin": carry,
                    "q": q[i],
                }
            )
            carry = fa_i.outputs.cout
        output = reduce(
          lambda reduced, bit: bit if reduced is None else bit @ reduced,
          q, None
        )

        self.io.q <<= output
        self.io.cout <<= carry


class Top(Module):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        width = 6
        self.io += [
            Input("a", width),
            Input("b", width),
            Output("q", width),
            Input("cin", 1),
            Output("cout", 1),
        ]

        RCA(width).instance(io={
            "a": self.io.a,
            "b": self.io.b,
            "cin": self.io.cin,
            "q": self.io.q,
            "cout": self.io.cout,
        })


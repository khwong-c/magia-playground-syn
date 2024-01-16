from magia import Module, Input, Output


class SubMod(Module):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.io += [
            Input("x0", 8),
            Input("x1", 8),
            Output("y0", 8),
            Output("y1", 8),
        ]
        self.io.y0 <<= self.io.x0 + self.io.x1
        self.io.y1 <<= self.io.x0 - self.io.x1


class Top(Module):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.io += [
            Input("x0", 8),
            Input("x1", 8),
            Output("y0", 8),
            Output("y1", 8),
        ]

        sub = SubMod()
        sub0 = sub.instance(
            io={
                "x0": self.io.x0,
                "x1": self.io.x1,
            }
        )
        sub1 = sub.instance(
            io={
                "x0": sub0.outputs.y1,
                "x1": sub0.outputs.y0,
                "y0": self.io.y0,
                "y1": self.io.y1
            }
        )

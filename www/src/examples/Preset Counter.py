from magia import Module, Input, Output, Signal, Register


class Top(Module):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        width = 8
        self.io += [
            Input("clk", 1),
            Input("preset", 1),
            Input("d", width),
            Output("q", width),
        ]
        cur_count = Register(width, clk=self.io.clk)
        cur_count <<= (cur_count + 1).when(~self.io.preset, else_=self.io.d)
        self.io.q <<= cur_count

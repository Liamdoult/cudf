# Copyright (c) 2018-2020, NVIDIA CORPORATION.


class GDFError(Exception):
    def __init__(self, errcode, msg):
        self.errcode = errcode
        super(GDFError, self).__init__(msg)

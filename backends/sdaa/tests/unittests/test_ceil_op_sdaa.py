# BSD 3- Clause License Copyright (c) 2023, Tecorigin Co., Ltd. All rights
# reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software
# without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY,OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)  ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
# OF SUCH DAMAGE.

from __future__ import print_function

import numpy as np
import unittest

from op_test import OpTest, skip_check_grad_ci
import paddle
from paddle.static import Program, program_guard

paddle.enable_static()
SEED = 1024


@skip_check_grad_ci(reason="The backward test is not supported yet on sdaa.")
class TestCeilOp(OpTest):
    def setUp(self):
        self.op_type = "ceil"
        self.python_api = paddle.ceil
        self.set_sdaa()
        self.init_dtype()
        self.init_shape()

        np.random.seed(1024)
        x = np.random.uniform(0, 1, self.shape).astype(self.dtype)
        out = np.ceil(x)

        self.inputs = {"X": x}
        self.outputs = {"Out": out}

    def set_sdaa(self):
        self.__class__.use_custom_device = True
        self.place = paddle.CustomPlace("sdaa", 0)

    def init_shape(self):
        self.shape = [10, 12]

    def init_dtype(self):
        self.dtype = np.float32

    def test_check_output(self):
        self.check_output_with_place(self.place)


class TestCeil_ZeroDim(TestCeilOp):
    def init_shape(self):
        self.shape = []


class TestCeilOpFp16(TestCeilOp):
    def init_dtype(self):
        self.dtype = np.float16


class TestCeilOpDouble(TestCeilOp):
    def init_dtype(self):
        self.dtype = np.double


# In static graph mode, inplace strategy will not be used in Inplace APIs.
class TestStaticAutoGeneratedCeilAPI(unittest.TestCase):
    def setUp(self):
        paddle.enable_static()
        paddle.device.set_device("sdaa")
        self.init_data()
        self.set_np_compare_func()

    def init_data(self):
        self.dtype = np.float32
        self.shape = [10, 20]
        self.np_x = np.random.uniform(-5, 5, self.shape).astype(self.dtype)

    def set_np_compare_func(self):
        self.np_compare = np.array_equal

    def executed_paddle_api(self, x):
        return x.ceil()

    def executed_numpy_api(self, x):
        return np.ceil(x)

    def test_api(self):
        main_prog = Program()
        with program_guard(main_prog, Program()):
            x = paddle.static.data(name="x", shape=self.shape, dtype=self.dtype)
            out = self.executed_paddle_api(x)

        exe = paddle.static.Executor(place=paddle.CPUPlace())
        fetch_x, fetch_out = exe.run(
            main_prog, feed={"x": self.np_x}, fetch_list=[x, out]
        )

        np.testing.assert_array_equal(fetch_x, self.np_x)
        self.assertTrue(self.np_compare(fetch_out, self.executed_numpy_api(self.np_x)))


class TestStaticInplaceAutoGeneratedCeilAPI(TestStaticAutoGeneratedCeilAPI):
    def executed_paddle_api(self, x):
        return x.ceil_()


# In dygraph mode, inplace strategy will be used in Inplace APIs.
class TestDygraphAutoGeneratedCeilAPI(unittest.TestCase):
    def setUp(self):
        paddle.disable_static()
        paddle.device.set_device("sdaa")
        self.init_data()
        self.set_np_compare_func()

    def init_data(self):
        self.dtype = np.float32
        self.shape = [10, 20]
        self.np_x = np.random.uniform(-5, 5, self.shape).astype(self.dtype)

    def set_np_compare_func(self):
        self.np_compare = np.array_equal

    def executed_paddle_api(self, x):
        return x.ceil()

    def executed_numpy_api(self, x):
        return np.ceil(x)

    def test_api(self):
        x = paddle.to_tensor(self.np_x, dtype=self.dtype)
        out = self.executed_paddle_api(x)

        self.assertTrue(
            self.np_compare(out.numpy(), self.executed_numpy_api(self.np_x))
        )


class TestDygraphInplaceAutoGeneratedCeilAPI(TestDygraphAutoGeneratedCeilAPI):
    def executed_paddle_api(self, x):
        return x.ceil_()


class TestDygraphInplaceAutoGeneratedCeilFp16API(
    TestDygraphInplaceAutoGeneratedCeilAPI
):
    def init_data(self):
        self.dtype = np.float16
        self.shape = [10, 20]
        self.np_x = np.random.uniform(-5, 5, self.shape).astype(self.dtype)


class TestDygraphInplaceAutoGeneratedCeilDoubleAPI(
    TestDygraphInplaceAutoGeneratedCeilAPI
):
    def init_data(self):
        self.dtype = np.double
        self.shape = [10, 20]
        self.np_x = np.random.uniform(-5, 5, self.shape).astype(self.dtype)


if __name__ == "__main__":
    unittest.main()

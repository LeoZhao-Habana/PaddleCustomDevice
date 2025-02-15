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

import unittest
import numpy as np

import paddle
import paddle.nn.functional as F
from paddle.framework import set_flags


def set_sdaa():
    paddle.device.set_device("sdaa")


unary_api_list = [
    paddle.nn.functional.elu,
    paddle.nn.functional.gelu,
    paddle.nn.functional.hardsigmoid,
    paddle.nn.functional.hardswish,
    paddle.nn.functional.hardshrink,
    paddle.nn.functional.hardtanh,
    paddle.nn.functional.leaky_relu,
    paddle.nn.functional.log_sigmoid,
    paddle.nn.functional.relu,
    paddle.nn.functional.relu6,
    paddle.nn.functional.sigmoid,
    paddle.nn.functional.softplus,
    paddle.nn.functional.softshrink,
    paddle.nn.functional.softsign,
    paddle.nn.functional.swish,
    paddle.nn.functional.tanhshrink,
    paddle.nn.functional.thresholded_relu,
    paddle.stanh,
    paddle.nn.functional.celu,
    paddle.nn.functional.selu,
    paddle.nn.functional.mish,
    paddle.nn.functional.silu,
    paddle.nn.functional.tanh,
    paddle.cosh,
    paddle.sinh,
    paddle.abs,
    paddle.acos,
    paddle.asin,
    paddle.atan,
    paddle.ceil,
    paddle.cos,
    paddle.exp,
    paddle.floor,
    paddle.log,
    paddle.log1p,
    paddle.reciprocal,
    paddle.round,
    paddle.sin,
    paddle.sqrt,
    paddle.square,
    paddle.tanh,
    paddle.acosh,
    paddle.asinh,
    paddle.atanh,
    paddle.expm1,
    paddle.log10,
    paddle.log2,
    paddle.tan,
    paddle.erf,
    paddle.erfinv,
    paddle.rsqrt,
    paddle.sign,
    paddle.deg2rad,
    paddle.rad2deg,
    paddle.neg,
    paddle.logit,
    paddle.trunc,
    paddle.digamma,
    paddle.lgamma,
    paddle.poisson,
    paddle.bernoulli,
    paddle.nn.functional.softmax,
    paddle.nn.functional.log_softmax,
]

unary_api_list_ = [
    paddle.nn.functional.dropout,
]

inplace_api_list = [
    paddle.nn.functional.relu_,
    paddle.nn.functional.tanh_,
]


# Use to test zero-dim in unary API.
class TestUnaryAPI(unittest.TestCase):
    def test_dygraph_unary(self):
        paddle.disable_static()
        set_sdaa()
        for api in unary_api_list:
            x = paddle.rand([])
            x.stop_gradient = False
            x.retain_grads()
            out = api(x)
            out.retain_grads()
            out.backward()

            self.assertEqual(x.shape, [])
            self.assertEqual(out.shape, [])
            if x.grad is not None:
                self.assertEqual(x.grad.shape, [])
                self.assertEqual(out.grad.shape, [])

        for api in inplace_api_list:
            x = paddle.rand([])
            out = api(x)
            self.assertEqual(x.shape, [])
            self.assertEqual(out.shape, [])

        paddle.enable_static()

    def test_dygraph_unary_(self):
        paddle.disable_static()
        set_sdaa()
        for api in unary_api_list_:
            x = paddle.rand([])
            x.stop_gradient = False
            x.retain_grads()
            out = api(x)
            out.retain_grads()
            out.backward()

            self.assertEqual(x.shape, [])
            self.assertEqual(out.shape, [])
            if x.grad is not None:
                self.assertEqual(x.grad.shape, [])
                self.assertEqual(out.grad.shape, [])

        paddle.enable_static()


reduce_api_list = [
    paddle.sum,
    paddle.mean,
    paddle.nansum,
    paddle.nanmean,
    paddle.min,
    paddle.max,
    paddle.amin,
    paddle.amax,
    paddle.prod,
    paddle.logsumexp,
    paddle.all,
    paddle.any,
]


# Use to test zero-dim of reduce API
class TestReduceAPI(unittest.TestCase):
    def test_dygraph_reduce(self):
        paddle.disable_static()
        set_sdaa()
        for api in reduce_api_list:
            # 1) x is 0D
            if api in [paddle.all, paddle.any]:
                x = paddle.randint(0, 2, []).astype("bool")
            else:
                x = paddle.rand([])
            x.stop_gradient = False
            x.retain_grads()
            out = api(x, None)
            out.retain_grads()
            out.backward()

            self.assertEqual(x.shape, [])
            self.assertEqual(out.shape, [])
            np.testing.assert_allclose(out.numpy(), x.numpy(), rtol=1e-6)
            if x.grad is not None:
                self.assertEqual(x.grad.shape, [])
                self.assertEqual(out.grad.shape, [])
                np.testing.assert_allclose(x.grad.numpy(), np.array(1.0))
                np.testing.assert_allclose(out.grad.numpy(), np.array(1.0))

        paddle.enable_static()


binary_api_list = [
    {"func": paddle.add, "cls_method": "__add__"},
    {"func": paddle.subtract, "cls_method": "__sub__"},
    {"func": paddle.multiply, "cls_method": "__mul__"},
    {"func": paddle.divide, "cls_method": "__div__"},
    # {
    #     "func": paddle.pow,
    #     "cls_method": "__pow__"
    # },   # because tecodnnElementwisePow only support x.dims() == y.dims()
    {"func": paddle.equal, "cls_method": "__eq__"},
    {"func": paddle.not_equal, "cls_method": "__ne__"},
    {"func": paddle.greater_equal, "cls_method": "__ge__"},
    {"func": paddle.greater_than, "cls_method": "__gt__"},
    {"func": paddle.less_equal, "cls_method": "__le__"},
    {"func": paddle.less_than, "cls_method": "__lt__"},
    {"func": paddle.remainder, "cls_method": "__mod__"},
    paddle.mod,
    paddle.floor_mod,
    paddle.logical_and,
    paddle.logical_or,
    paddle.logical_xor,
    paddle.maximum,
    paddle.minimum,
]

binary_int_api_list = [
    paddle.bitwise_and,
    paddle.bitwise_or,
    paddle.bitwise_xor,
]


# Use to test zero-dim of binary API
class TestBinaryAPI(unittest.TestCase):
    def test_dygraph_binary(self):
        paddle.disable_static()
        set_sdaa()
        for api in binary_api_list:
            # 1) x is 0D, y is 0D
            x = paddle.rand([])
            y = paddle.rand([])
            x.stop_gradient = False
            y.stop_gradient = False
            x.retain_grads()
            y.retain_grads()
            if isinstance(api, dict):
                out = api["func"](x, y)
                out_cls = getattr(paddle.Tensor, api["cls_method"])(x, y)
                np.testing.assert_array_equal(out_cls.numpy(), out.numpy())
            else:
                out = api(x, y)
            out.retain_grads()
            out.backward()

            self.assertEqual(x.shape, [])
            self.assertEqual(y.shape, [])
            self.assertEqual(out.shape, [])
            if x.grad is not None:
                self.assertEqual(x.grad.shape, [])
                self.assertEqual(y.grad.shape, [])
                self.assertEqual(out.grad.shape, [])

            # 2) x is ND, y is 0D
            x = paddle.rand([2, 3, 4])
            y = paddle.rand([])
            x.stop_gradient = False
            y.stop_gradient = False
            if isinstance(api, dict):
                out = api["func"](x, y)
                out_cls = getattr(paddle.Tensor, api["cls_method"])(x, y)
                np.testing.assert_array_equal(out_cls.numpy(), out.numpy())
            else:
                out = api(x, y)
            out.retain_grads()
            out.backward()

            self.assertEqual(x.shape, [2, 3, 4])
            self.assertEqual(y.shape, [])
            self.assertEqual(out.shape, [2, 3, 4])
            if x.grad is not None:
                self.assertEqual(x.grad.shape, [2, 3, 4])
                self.assertEqual(y.grad.shape, [])
                self.assertEqual(out.grad.shape, [2, 3, 4])

            # 3) x is 0D , y is ND
            # maximum and minimum kernel in sdaa only support y broadcast to x.
            if not (api == paddle.maximum or api == paddle.minimum):
                x = paddle.rand([])
                y = paddle.rand([2, 3, 4])
                x.stop_gradient = False
                y.stop_gradient = False
                if isinstance(api, dict):
                    out = api["func"](x, y)
                    out_cls = getattr(paddle.Tensor, api["cls_method"])(x, y)
                    np.testing.assert_array_equal(out_cls.numpy(), out.numpy())
                else:
                    out = api(x, y)
                out.retain_grads()
                out.backward()

                self.assertEqual(x.shape, [])
                self.assertEqual(y.shape, [2, 3, 4])
                self.assertEqual(out.shape, [2, 3, 4])
                if x.grad is not None:
                    self.assertEqual(x.grad.shape, [])
                    self.assertEqual(y.grad.shape, [2, 3, 4])
                    self.assertEqual(out.grad.shape, [2, 3, 4])

            # 4) x is 0D , y is scalar
            x = paddle.rand([])
            x.stop_gradient = False
            y = 0.5
            if isinstance(api, dict):
                out = getattr(paddle.Tensor, api["cls_method"])(x, y)
                out.retain_grads()
                out.backward()

                self.assertEqual(x.shape, [])
                self.assertEqual(out.shape, [])
                if x.grad is not None:
                    self.assertEqual(x.grad.shape, [])
                    self.assertEqual(out.grad.shape, [])

        for api in binary_int_api_list:
            # 1) x is 0D, y is 0D
            x_np = np.random.randint(-10, 10, [])
            y_np = np.random.randint(-10, 10, [])
            out_np = eval("np.%s(x_np, y_np)" % api.__name__)

            x = paddle.to_tensor(x_np)
            y = paddle.to_tensor(y_np)
            out = api(x, y)

            self.assertEqual(out.shape, [])
            np.testing.assert_array_equal(out.numpy(), out_np)

            # 2) x is ND, y is 0D
            x_np = np.random.randint(-10, 10, [3, 5])
            y_np = np.random.randint(-10, 10, [])
            out_np = eval("np.%s(x_np, y_np)" % api.__name__)

            x = paddle.to_tensor(x_np)
            y = paddle.to_tensor(y_np)
            out = api(x, y)

            self.assertEqual(out.shape, [3, 5])
            np.testing.assert_array_equal(out.numpy(), out_np)

            # 3) x is 0D , y is ND
            x_np = np.random.randint(-10, 10, [])
            y_np = np.random.randint(-10, 10, [3, 5])
            out_np = eval("np.%s(x_np, y_np)" % api.__name__)

            x = paddle.to_tensor(x_np)
            y = paddle.to_tensor(y_np)
            out = api(x, y)

            self.assertEqual(out.shape, [3, 5])
            np.testing.assert_array_equal(out.numpy(), out_np)

        paddle.enable_static()


# Use to test zero-dim of Sundry API, which is unique and can not be classified
# with others. It can be implemented here flexibly.
class TestSundryAPI(unittest.TestCase):
    def setUp(self):
        paddle.disable_static()
        set_sdaa()
        self.x = paddle.rand([])

    def _test_argmin(self):
        x = paddle.rand([])
        out1 = paddle.argmin(x, 0)
        out2 = paddle.argmin(x, -1)
        out3 = paddle.argmin(x, None)
        self.assertEqual(out1.shape, [])
        np.testing.assert_allclose(out1, 0.0)

        self.assertEqual(out2.shape, [])
        np.testing.assert_allclose(out2, 0.0)

        self.assertEqual(out3.shape, [])
        np.testing.assert_allclose(out3, 0.0)

    def _test_argmax(self):
        x = paddle.rand([])
        out1 = paddle.argmax(x, 0)
        out2 = paddle.argmax(x, -1)
        out3 = paddle.argmax(x, None)
        self.assertEqual(out1.shape, [])
        np.testing.assert_allclose(out1, 0.0)

        self.assertEqual(out2.shape, [])
        np.testing.assert_allclose(out2, 0.0)

        self.assertEqual(out3.shape, [])
        np.testing.assert_allclose(out3, 0.0)

    def test_median(self):
        x = paddle.rand([])
        x.stop_gradient = False
        out1 = paddle.median(x, 0)
        out2 = paddle.median(x, -1)
        out3 = paddle.median(x, None)

        out1.backward()
        out2.backward()
        out3.backward()

        self.assertEqual(out1.shape, [])
        np.testing.assert_allclose(out1, x, rtol=1e-3, atol=1e-3)

        self.assertEqual(out2.shape, [])
        np.testing.assert_allclose(out2, x, rtol=1e-3, atol=1e-3)

        self.assertEqual(out3.shape, [])
        np.testing.assert_allclose(out3, x, rtol=1e-3, atol=1e-3)

        self.assertEqual(x.grad.shape, [])
        np.testing.assert_allclose(x.grad, 3.0, rtol=1e-3, atol=1e-3)

    def test_getitem(self):
        set_flags({"FLAGS_set_to_1d": False})
        # case1: When all axis have a scalar indice, output should be a 0-d Tensor;
        x = paddle.arange(2 * 3 * 4 * 5).reshape((2, 3, 4, 5))
        x.stop_gradient = False
        out = x[1, 2, 3, 4]
        out.retain_grads()
        out.backward()
        self.assertEqual(out.shape, [])
        np.testing.assert_allclose(out, np.array(119))
        self.assertEqual(out.grad.shape, [])
        np.testing.assert_allclose(out.grad, 1.0)
        self.assertEqual(x.grad.shape, [2, 3, 4, 5])
        x_grad_expected = np.zeros((2, 3, 4, 5))
        x_grad_expected[1, 2, 3, 4] = 1.0
        np.testing.assert_allclose(x.grad, x_grad_expected)

        # case2: When one axis has a 0-d Tensor indice, the output should be same as int indice.
        x = paddle.arange(2 * 3 * 4 * 5).reshape((2, 3, 4, 5))
        out1 = x[1, 2]
        out2 = x[paddle.full([], 1, dtype="int32"), paddle.full([], 2, dtype="int32")]
        np.testing.assert_allclose(out1, out2)

        # case3: When all axis have a scalar indice (i.e. case1) and has None indice,
        # ndim of output should be same with numbers of None.
        x = paddle.arange(2 * 3 * 4 * 5).reshape((2, 3, 4, 5))
        out1 = x[1, 2, None, 3, 4]
        self.assertEqual(out1.shape, [1])
        np.testing.assert_allclose(out1, np.array([119]))
        out2 = x[1, None, 2, None, 3, 4]
        self.assertEqual(out2.shape, [1, 1])
        np.testing.assert_allclose(out2, np.array([[119]]))

        # case4: 1-D Tensor will be treated as vector, no axis decrease will happen.
        x = paddle.ones((2, 3, 4))
        indice = paddle.ones([1], dtype="int32")
        out1 = x[indice]
        self.assertEqual(out1.shape, [1, 3, 4])
        np.testing.assert_allclose(out1, np.ones((1, 3, 4)))
        out2 = x[indice, indice]
        self.assertEqual(out2.shape, [1, 4])
        np.testing.assert_allclose(out2, np.ones((1, 4)))

    def test_setitem(self):
        set_flags({"FLAGS_set_to_1d": False})
        # case1: all axis have a scalar indice
        x = paddle.arange(2 * 3 * 4 * 5).reshape((2, 3, 4, 5))
        x.stop_gradient = False
        out = x * 2
        out[1, 2, 3, 4] = 10
        out.backward()

        self.assertEqual(out.shape, x.shape)
        np.testing.assert_allclose(out[1, 2, 3, 4], np.array(10))
        self.assertEqual(x.grad.shape, [2, 3, 4, 5])
        x_grad_expected = np.ones((2, 3, 4, 5)) * 2
        x_grad_expected[1, 2, 3, 4] = 0
        np.testing.assert_allclose(x.grad, x_grad_expected)

        # case2: 0-D Tensor indice in some axis
        # NOTE(zoooo0820): Now, int/slice with 0-D Tensor will still be
        # treated as combined indexing, which is not support backward.
        # There should have more test cases such as out[1, indice, :] = 0.5 when this
        # problem is fixed.
        x = paddle.randn((2, 3, 4, 5))
        x.stop_gradient = False
        indice = paddle.full([], 1, dtype="int32")
        out = x * 1
        out[indice, indice] = 0.5
        out.backward()

        self.assertEqual(out.shape, x.shape)
        np.testing.assert_allclose(out[1, 1], np.ones((4, 5)) * 0.5)
        x_grad_expected = np.ones((2, 3, 4, 5))
        x_grad_expected[1, 1] = 0
        np.testing.assert_allclose(x.grad, x_grad_expected)

        # case3：0-D Tensor indice in some axis, value is a Tensor
        # and there is broadcast
        x = paddle.randn((2, 3, 4, 5))
        x.stop_gradient = False
        v = paddle.ones((4, 5), dtype="float32") * 5
        v.stop_gradient = False
        indice = paddle.full([], 1, dtype="int32")
        out = x * 1
        out[indice] = v
        out.backward()

        self.assertEqual(out.shape, x.shape)
        np.testing.assert_allclose(out[1], np.ones((3, 4, 5)) * 5)
        x_grad_expected = np.ones((2, 3, 4, 5))
        x_grad_expected[1] = 0
        np.testing.assert_allclose(x.grad, x_grad_expected)
        value_grad_expected = np.ones((4, 5)) * 3
        np.testing.assert_allclose(v.grad, value_grad_expected)

        # case4: value is a 0-D tensor and there is broadcast
        x = paddle.randn((2, 3, 4, 5))
        x.stop_gradient = False
        v = paddle.ones([], dtype="float32") * 5
        v.stop_gradient = False
        out = x * 1
        indice = paddle.full([], 0, dtype="int32")
        out[indice] = v
        out.backward()

        self.assertEqual(out.shape, x.shape)
        self.assertEqual(v.grad.shape, [])
        np.testing.assert_allclose(out[0], np.ones((3, 4, 5)) * 5)
        x_grad_expected = np.ones((2, 3, 4, 5))
        x_grad_expected[0] = 0
        np.testing.assert_allclose(x.grad, x_grad_expected)
        value_grad_expected = np.ones(()) * 3 * 4 * 5
        np.testing.assert_allclose(v.grad, value_grad_expected)

        # case5: indice / value is 0-D Tensor, and there is no broadcast
        x = paddle.randn((2, 3, 4, 5))
        x.stop_gradient = False
        v = paddle.ones([], dtype="float32") * 2
        v.stop_gradient = False
        out = x * 1
        indice = paddle.full([], 0, dtype="int32")
        out[indice, indice, indice, indice] = v
        out.backward()

        self.assertEqual(out.shape, x.shape)
        self.assertEqual(v.grad.shape, [])
        np.testing.assert_allclose(out[0, 0, 0, 0], np.ones(()) * 2)
        x_grad_expected = np.ones((2, 3, 4, 5))
        x_grad_expected[0, 0, 0, 0] = 0
        np.testing.assert_allclose(x.grad, x_grad_expected)
        value_grad_expected = np.ones(())
        np.testing.assert_allclose(v.grad, value_grad_expected)

    def test_expand(self):
        # case1
        x = paddle.full([], 1, "float32")
        x.stop_gradient = False
        out = paddle.expand(x, shape=[1])
        out.retain_grads()
        out.backward()

        self.assertEqual(out.shape, [1])
        np.testing.assert_allclose(out, 1.0)
        self.assertEqual(x.grad.shape, [])
        np.testing.assert_allclose(x.grad, 1.0)
        self.assertEqual(out.grad.shape, [1])
        np.testing.assert_allclose(out.grad, 1.0)

        # case2
        x1 = paddle.full([], 1, "float32")
        x1.stop_gradient = False
        out1 = paddle.expand(x1, shape=[])
        out1.retain_grads()
        out1.backward()

        self.assertEqual(out1.shape, [])
        np.testing.assert_allclose(out1, 1.0)
        self.assertEqual(x1.grad.shape, [])
        np.testing.assert_allclose(x1.grad, 1.0)
        self.assertEqual(out1.grad.shape, [])
        np.testing.assert_allclose(out1.grad, 1.0)

        # case3
        x2 = paddle.full([], 1, "float32")
        x2.stop_gradient = False
        out2 = paddle.expand(x2, shape=[1, 1])
        out2.retain_grads()
        out2.backward()

        self.assertEqual(out2.shape, [1, 1])
        np.testing.assert_allclose(out2, 1.0)
        self.assertEqual(x2.grad.shape, [])
        np.testing.assert_allclose(x2.grad, 1.0)
        self.assertEqual(out2.grad.shape, [1, 1])
        np.testing.assert_allclose(out2.grad, 1.0)

        # case4
        x3 = paddle.full([], 1, "float32")
        x3.stop_gradient = False
        out3 = paddle.expand(x3, shape=[3, 3])
        out3.retain_grads()
        out3.backward()

        self.assertEqual(out3.shape, [3, 3])
        np.testing.assert_allclose(out3, 1.0)
        self.assertEqual(x3.grad.shape, [])
        np.testing.assert_allclose(x3.grad, 9.0)
        self.assertEqual(out3.grad.shape, [3, 3])
        np.testing.assert_allclose(out3.grad, 1.0)

    def test_expand_as(self):
        x = paddle.full([], 1, "float32")
        x.stop_gradient = False
        y = paddle.full([], 1, "float32")
        y.stop_gradient = False
        out = paddle.expand_as(x, y)
        out.backward()
        self.assertEqual(x.shape, [])
        self.assertEqual(x.item(), 1.0)
        self.assertEqual(x.grad.shape, [])
        self.assertEqual(x.grad.item(), 1.0)
        self.assertEqual(out.shape, [])
        self.assertEqual(out.item(), 1.0)
        self.assertEqual(out.grad, None)

        x1 = paddle.full([], 1, "float32")
        x1.stop_gradient = False
        y1 = paddle.full([1], 1, "float32")
        out1 = paddle.expand_as(x1, y1)
        out1.backward()
        self.assertEqual(x1.shape, [])
        self.assertEqual(x1.item(), 1.0)
        self.assertEqual(x1.grad.shape, [])
        self.assertEqual(x1.grad.item(0), 1.0)
        self.assertEqual(out1.shape, [1])
        self.assertEqual(out1.item(0), 1.0)
        self.assertEqual(out1.grad, None)

        x2 = paddle.full([], 1, "float32")
        x2.stop_gradient = False
        y2 = paddle.full([3, 3], 1, "float32")
        out2 = paddle.expand_as(x2, y2)
        out2.backward()
        self.assertEqual(x2.shape, [])
        self.assertEqual(x2.item(), 1.0)
        self.assertEqual(x2.grad.shape, [])
        self.assertEqual(x2.grad.item(0), 9.0)
        self.assertEqual(out2.shape, [3, 3])
        self.assertEqual(out2.item(0), 1.0)
        self.assertEqual(out2.grad, None)

    def test_top_k(self):
        x = paddle.full([], 1, "float32")
        x.stop_gradient = False
        out, indices = paddle.topk(x, k=1, axis=0)
        out.retain_grads()
        out.backward()
        self.assertEqual(indices.shape, [])
        self.assertEqual(indices.item(), 0)
        self.assertEqual(x.shape, [])
        self.assertEqual(x.item(), 1.0)
        self.assertEqual(x.grad.shape, [])
        self.assertEqual(x.grad.item(0), 1.0)
        self.assertEqual(out.shape, [])
        self.assertEqual(out.item(), 1.0)
        self.assertEqual(out.grad, 1.0)

        x1 = paddle.full([], 1, "float32")
        x1.stop_gradient = False
        out1, indices1 = paddle.topk(x1, k=1, axis=-1)
        out1.retain_grads()
        out1.backward()
        self.assertEqual(indices1.shape, [])
        self.assertEqual(indices1.item(), 0)
        self.assertEqual(x1.shape, [])
        self.assertEqual(x1.item(), 1.0)
        self.assertEqual(x.grad.shape, [])
        self.assertEqual(x.grad.item(0), 1.0)
        self.assertEqual(out1.shape, [])
        self.assertEqual(out1.item(), 1.0)
        self.assertEqual(out1.grad, 1.0)

        with self.assertRaises(ValueError):
            tmp = paddle.topk(x1, k=1, axis=2)

    def test_linear(self):
        x = paddle.randn([3, 2])
        w = paddle.full(shape=[2, 4], fill_value=0.5)
        b = paddle.zeros([])

        np.testing.assert_array_equal(F.linear(x, w, b).numpy(), F.linear(x, w).numpy())

    def test_is_floating_point(self):
        self.assertTrue(paddle.is_floating_point(self.x))

    def test_is_integer(self):
        x = paddle.randint(0, 10, [])
        self.assertTrue(paddle.is_integer(x))

    def test_is_tensor(self):
        self.assertTrue(paddle.is_tensor(self.x))

    def test_is_empty(self):
        x = paddle.rand([3, 0, 5])
        self.assertTrue(paddle.is_empty(x))

    def test_isfinite(self):
        out = paddle.isfinite(self.x)
        np.testing.assert_array_equal(out.numpy(), np.array(True))

    def test_isinf(self):
        x = paddle.to_tensor(np.array(float("-inf")))
        out = paddle.isinf(x)
        np.testing.assert_array_equal(out.numpy(), np.array(True))

    def test_isnan(self):
        x = paddle.to_tensor(np.array(float("nan")))
        out = paddle.isnan(x)
        np.testing.assert_array_equal(out.numpy(), np.array(True))

    def test_isclose(self):
        out = paddle.isclose(self.x, self.x)
        np.testing.assert_array_equal(out.numpy(), np.array(True))

    def test_clone(self):
        out = paddle.clone(self.x)
        np.testing.assert_array_equal(out.numpy(), self.x.numpy())

    def test_assign(self):
        out = paddle.assign(self.x)
        np.testing.assert_array_equal(out.numpy(), self.x.numpy())

    def test_item(self):
        x = paddle.full([], 0.5)
        self.assertEqual(x.item(), 0.5)

    def test_tolist(self):
        x = paddle.full([], 0.5)
        self.assertEqual(x.tolist(), 0.5)

    def test_numpy(self):
        x = paddle.full([], 0.5)
        np.testing.assert_array_equal(x.numpy(), np.array(0.5))

    def test_numel(self):
        out = paddle.numel(self.x)
        self.assertEqual(out.shape, [])
        np.testing.assert_array_equal(out.numpy(), np.array(1))

    def test_rank(self):
        out = paddle.rank(self.x)
        self.assertEqual(out.shape, [])
        np.testing.assert_array_equal(out.numpy(), np.array(0))

    def test_shape(self):
        out = paddle.shape(self.x)
        self.assertEqual(out.shape, [0])
        np.testing.assert_array_equal(out.numpy(), np.array([]))

    def test_pow_factor(self):
        x = paddle.rand([])
        x.stop_gradient = False
        x.retain_grads()
        out = paddle.pow(x, 2.0)
        out.retain_grads()
        out.backward()

        self.assertEqual(out.shape, [])
        self.assertEqual(out.grad.shape, [])
        self.assertEqual(x.grad.shape, [])

    def test_cast(self):
        x = paddle.full([], 1.0, "float32")
        x.stop_gradient = False
        x.retain_grads()
        out = paddle.cast(x, "int32")
        out.retain_grads()
        out.backward()

        self.assertEqual(out.shape, [])
        self.assertEqual(out.grad.shape, [])
        self.assertEqual(x.grad.shape, [])

    def test_clip(self):
        x = paddle.uniform([], None, -10, 10)
        x.stop_gradient = False
        x.retain_grads()
        out = paddle.clip(x, -5, 5)
        out.retain_grads()
        out.backward()

        self.assertEqual(out.shape, [])
        self.assertEqual(out.grad.shape, [])
        self.assertEqual(x.grad.shape, [])

    def test_increment(self):
        x = paddle.rand([])
        x.stop_gradient = False
        x.retain_grads()
        out = paddle.increment(x, 1.0)
        out.retain_grads()
        out.backward()

        self.assertEqual(out.shape, [])
        self.assertEqual(out.grad.shape, [])
        self.assertEqual(x.grad.shape, [])

    def test_bitwise_not(self):
        x_np = np.random.randint(-10, 10, [])
        out_np = ~x_np

        x = paddle.to_tensor(x_np)
        out = ~x

        self.assertEqual(out.shape, [])
        np.testing.assert_array_equal(out.numpy(), out_np)

    def test_logical_not(self):
        x = paddle.randint(0, 1, [])
        out = paddle.logical_not(x)

        self.assertEqual(out.shape, [])

    def test_searchsorted(self):
        x = paddle.to_tensor([1, 3, 5, 7, 9])
        y = paddle.rand([])

        # only has forward kernel
        out = paddle.searchsorted(x, y)

        self.assertEqual(out.shape, [])
        self.assertEqual(out.numpy(), 0)

    def test_transpose(self):
        x = paddle.rand([])
        x.stop_gradient = False
        x.retain_grads()
        out = paddle.transpose(x, [])
        out.retain_grads()
        out.backward()

        self.assertEqual(out.shape, [])
        self.assertEqual(out, x)
        self.assertEqual(out.grad.shape, [])
        self.assertEqual(x.grad.shape, [])
        self.assertEqual(x.grad, 1.0)

        with self.assertRaises(ValueError):
            x = paddle.transpose(x, [0])

    def test_moveaxis(self):
        x = paddle.rand([])
        x.stop_gradient = False
        x.retain_grads()
        out = paddle.moveaxis(x, [], [])
        out.retain_grads()
        out.backward()

        self.assertEqual(out.shape, [])
        self.assertEqual(out, x)
        self.assertEqual(out.grad.shape, [])
        self.assertEqual(x.grad.shape, [])
        self.assertEqual(x.grad, 1.0)

        with self.assertRaises(AssertionError):
            x = paddle.moveaxis(x, [1], [0])

    def test_gather_1D(self):
        x = paddle.to_tensor([1.0, 3.0, 5.0, 7.0, 9.0], stop_gradient=False)
        x.retain_grads()
        index = paddle.full([], 2, "int64")
        out = paddle.gather(x, index)
        out.retain_grads()
        out.backward()

        self.assertEqual(out.shape, [])
        self.assertEqual(out.numpy(), 5)
        self.assertEqual(x.grad.shape, [5])
        self.assertEqual(out.grad.shape, [])

    def test_gather_xD_axis_0(self):
        x = paddle.to_tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], stop_gradient=False)
        x.retain_grads()
        index = paddle.full([], 1, "int64")
        out = paddle.gather(x, index)
        out.retain_grads()
        out.backward()

        self.assertEqual(out.shape, [3])
        np.testing.assert_array_equal(out.numpy(), x.numpy()[1, :])
        self.assertEqual(x.grad.shape, [2, 3])
        self.assertEqual(out.grad.shape, [3])

    @unittest.skip("gather_grad in sdaa only support axis=0")
    def test_gather_xD_axis_1(self):
        x = paddle.to_tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], stop_gradient=False)
        x.retain_grads()
        index = paddle.full([], 1, "int64")
        out = paddle.gather(x, index, axis=1)
        out.retain_grads()
        out.backward()

        self.assertEqual(out.shape, [2])
        np.testing.assert_array_equal(out.numpy(), [2.0, 5.0])
        self.assertEqual(x.grad.shape, [2, 3])
        self.assertEqual(out.grad.shape, [2])

    def test_gather_nd(self):
        x1 = paddle.to_tensor([1.0, 3.0, 5.0, 7.0, 9.0], stop_gradient=False)
        x2 = paddle.to_tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], stop_gradient=False)

        index1 = paddle.full([1], 1, "int64")
        index2 = paddle.full([2], 1, "int64")

        out1 = paddle.gather_nd(x1, index1)
        out2 = paddle.gather_nd(x2, index2)

        out1.retain_grads()
        out2.retain_grads()

        out1.backward()
        out2.backward()

        self.assertEqual(out1.shape, [])
        self.assertEqual(out2.shape, [])
        np.testing.assert_array_equal(out1, np.array(3.0))
        np.testing.assert_array_equal(out2, np.array(5.0))
        self.assertEqual(x1.grad.shape, [5])
        self.assertEqual(x2.grad.shape, [2, 3])
        self.assertEqual(out1.grad.shape, [])
        self.assertEqual(out2.grad.shape, [])

    def test_scatter_1D(self):
        # have no backward, not register
        x = paddle.to_tensor([1.0, 3.0, 5.0, 7.0, 9.0])
        index = paddle.full([], 2, "int64")
        updates = paddle.full([], 4.0)
        out = paddle.scatter(x, index, updates)

        self.assertEqual(out.shape, [5])
        self.assertEqual(out.numpy()[2], 4)

    def test_scatter_XD(self):
        # have no backward now, not register
        x = paddle.to_tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        index = paddle.full([], 1, "int64")
        updates = paddle.to_tensor([1.0, 2.0, 3.0])
        out = paddle.scatter(x, index, updates)

        self.assertEqual(out.shape, [2, 3])
        np.testing.assert_array_equal(out.numpy()[1], [1.0, 2.0, 3.0])

    def test_diagflat(self):
        x1 = paddle.rand([])
        x2 = paddle.rand([])
        x3 = paddle.rand([])
        x1.stop_gradient = False
        x2.stop_gradient = False
        x3.stop_gradient = False
        x1.retain_grads()
        x2.retain_grads()
        x3.retain_grads()

        out1 = paddle.diagflat(x1, 1)
        out2 = paddle.diagflat(x2, -1)
        out3 = paddle.diagflat(x3, 0)
        out1.retain_grads()
        out2.retain_grads()
        out3.retain_grads()

        out1.backward()
        out2.backward()
        out3.backward()

        self.assertEqual(out1.shape, [2, 2])
        self.assertEqual(out2.shape, [2, 2])
        self.assertEqual(out3.shape, [1, 1])

        self.assertEqual(out1.grad.shape, [2, 2])
        self.assertEqual(out2.grad.shape, [2, 2])
        self.assertEqual(out3.grad.shape, [1, 1])

        self.assertEqual(x1.grad.shape, [])
        self.assertEqual(x2.grad.shape, [])
        self.assertEqual(x3.grad.shape, [])

    def test_scatter__1D(self):
        x = paddle.to_tensor([1.0, 3.0, 5.0, 7.0, 9.0])
        index = paddle.full([], 2, "int64")
        updates = paddle.full([], 4.0)
        out = paddle.scatter_(x, index, updates)

        self.assertEqual(out.numpy()[2], 4)

    def test_scatter__XD(self):
        x = paddle.to_tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        index = paddle.full([], 1, "int64")
        updates = paddle.to_tensor([1.0, 2.0, 3.0])
        out = paddle.scatter_(x, index, updates)
        np.testing.assert_array_equal(out.numpy()[1], [1.0, 2.0, 3.0])

    def test_flatten(self):
        x = paddle.full([], 1, "float32")
        x.stop_gradient = False
        x.retain_grads()

        start_axis = 0
        stop_axis = -1

        out = paddle.flatten(x, start_axis=start_axis, stop_axis=stop_axis)
        out.retain_grads()
        out.backward()

        self.assertEqual(out.shape, [1])
        self.assertEqual(x.grad.shape, [])

    def test_scale(self):
        x = paddle.rand([])
        x.stop_gradient = False
        x.retain_grads()
        out = paddle.scale(x, scale=2.0, bias=1.0)
        out.retain_grads()
        out.backward()

        self.assertEqual(out.shape, [])
        self.assertEqual(out.grad.shape, [])
        self.assertEqual(x.grad.shape, [])

    def test_floor_divide(self):
        # 1-d // 0-d
        x = paddle.to_tensor([1, -2, 3], dtype="int64")
        y = paddle.full([], 2, dtype="int64")
        out1_1 = paddle.floor_divide(x, y)
        out1_2 = paddle.Tensor.__floordiv__(x, y)

        np.testing.assert_array_equal(out1_1.numpy(), out1_2.numpy())
        np.testing.assert_array_equal(out1_1.numpy(), np.asarray([0, -1, 1]))

        # 0-d // 1-d
        out2_1 = paddle.floor_divide(y, x)
        out2_2 = paddle.Tensor.__floordiv__(y, x)

        np.testing.assert_array_equal(out2_1.numpy(), out2_2.numpy())
        np.testing.assert_array_equal(out2_2.numpy(), np.asarray([2, -1, 0]))

        # 0-d // 0-d
        x = paddle.full([], 3, dtype="int64")
        out3_1 = paddle.floor_divide(x, y)
        out3_2 = paddle.Tensor.__floordiv__(x, y)

        np.testing.assert_array_equal(out3_1.numpy(), out3_2.numpy())
        np.testing.assert_array_equal(out3_2.numpy(), np.asarray(1))

    def test_add_n(self):
        x1 = paddle.rand([])
        x1.stop_gradient = False
        x2 = paddle.rand([])
        x2.stop_gradient = False
        x3 = paddle.rand([])
        x3.stop_gradient = False

        out1 = paddle.add_n(x1)
        out2 = paddle.add_n([x2, x3])

        out1.retain_grads()
        out2.retain_grads()

        out1.backward()
        out2.backward()

        self.assertEqual(out1.shape, [])
        self.assertEqual(out1.grad.shape, [])
        self.assertEqual(out2.shape, [])
        self.assertEqual(out2.grad.shape, [])

    def test_where(self):
        x1 = paddle.full([], 1)
        x2 = paddle.full([], 2)
        x1.stop_gradient = False
        x2.stop_gradient = False
        x1.retain_grads()
        x2.retain_grads()
        out = paddle.where(x1 > x2, x1, x2)
        out.retain_grads()
        out.backward()
        self.assertEqual(out.shape, [])
        self.assertEqual(out.numpy(), 2)
        self.assertEqual(out.grad.shape, [])
        self.assertEqual(x1.grad.shape, [])
        self.assertEqual(x2.grad.shape, [])
        self.assertEqual(x1.grad.numpy(), 0)
        self.assertEqual(x2.grad.numpy(), 1)

    def test_reshape_list(self):
        x = paddle.rand([])
        x.stop_gradient = False

        out = paddle.reshape(x, [])
        out.backward()
        self.assertEqual(x.grad.shape, [])
        self.assertEqual(out.shape, [])
        self.assertEqual(out.grad.shape, [])

        out = paddle.reshape(x, [1])
        out.retain_grads()
        out.backward()
        self.assertEqual(x.grad.shape, [])
        self.assertEqual(out.shape, [1])
        self.assertEqual(out.grad.shape, [1])

        out = paddle.reshape(x, [-1])
        out.retain_grads()
        out.backward()
        self.assertEqual(x.grad.shape, [])
        self.assertEqual(out.shape, [1])
        self.assertEqual(out.grad.shape, [1])

        out = paddle.reshape(x, [-1, 1])
        out.retain_grads()
        out.backward()
        self.assertEqual(x.grad.shape, [])
        self.assertEqual(out.shape, [1, 1])
        self.assertEqual(out.grad.shape, [1, 1])

    def test_reshape_tensor(self):
        x = paddle.rand([1, 1])
        x.stop_gradient = False

        out = paddle.reshape(x, [])
        out.retain_grads()
        out.backward()
        self.assertEqual(x.grad.shape, [1, 1])
        self.assertEqual(out.shape, [])
        self.assertEqual(out.grad.shape, [])

        new_shape = paddle.to_tensor([1, 1, 1], "int32")
        out = paddle.reshape(x, new_shape)
        out.retain_grads()
        out.backward()
        self.assertEqual(x.grad.shape, [1, 1])
        self.assertEqual(out.shape, [1, 1, 1])
        self.assertEqual(out.grad.shape, [1, 1, 1])

        new_shape = paddle.to_tensor([-1], "int32")
        out = paddle.reshape(x, new_shape)
        out.retain_grads()
        out.backward()
        self.assertEqual(x.grad.shape, [1, 1])
        self.assertEqual(out.shape, [1])
        self.assertEqual(out.grad.shape, [1])

        new_shape = [paddle.full([], -1, "int32"), paddle.full([], 1, "int32")]
        out = paddle.reshape(x, new_shape)
        out.retain_grads()
        out.backward()
        self.assertEqual(x.grad.shape, [1, 1])
        self.assertEqual(out.shape, [1, 1])
        self.assertEqual(out.grad.shape, [1, 1])

    def test_reshape__list(self):
        x = paddle.rand([])
        out = paddle.reshape_(x, [])
        self.assertEqual(out.shape, [])

        out = paddle.reshape_(x, [1])
        self.assertEqual(out.shape, [1])

        out = paddle.reshape_(x, [-1])
        self.assertEqual(out.shape, [1])

        out = paddle.reshape_(x, [-1, 1])
        self.assertEqual(out.shape, [1, 1])

    def test_reshape__tensor(self):
        x = paddle.rand([1, 1])
        out = paddle.reshape_(x, [])
        self.assertEqual(out.shape, [])

        new_shape = paddle.full([1], 1, "int32")
        out = paddle.reshape_(x, new_shape)
        self.assertEqual(out.shape, [1])

        new_shape = paddle.full([1], -1, "int32")
        out = paddle.reshape_(x, new_shape)
        self.assertEqual(out.shape, [1])

        new_shape = [paddle.full([], -1, "int32"), paddle.full([], 1, "int32")]
        out = paddle.reshape_(x, new_shape)
        self.assertEqual(out.shape, [1, 1])

    @unittest.skip(
        "argsort only supports special shapes in SDAA, skip this case for now."
    )
    def test_sort(self):
        x1 = paddle.rand([])
        x2 = paddle.rand([])
        x1.stop_gradient = False
        x2.stop_gradient = False

        out1 = paddle.sort(x1, axis=-1)
        out2 = paddle.sort(x2, axis=0)
        out1.retain_grads()
        out2.retain_grads()

        out1.backward()
        out2.backward()

        self.assertEqual(out1.shape, [])
        self.assertEqual(out2.shape, [])
        self.assertEqual(out1.numpy(), x1.numpy())
        self.assertEqual(out2.numpy(), x2.numpy())
        self.assertEqual(out1.grad.shape, [])
        self.assertEqual(out2.grad.shape, [])
        self.assertEqual(x1.grad.shape, [])
        self.assertEqual(x2.grad.shape, [])
        self.assertEqual(x1.grad.numpy(), 1)
        self.assertEqual(x2.grad.numpy(), 1)

    @unittest.skip(
        "argsort only supports special shapes in SDAA, skip this case for now."
    )
    def test_argsort(self):
        x1 = paddle.rand([])
        x2 = paddle.rand([])
        x1.stop_gradient = False
        x2.stop_gradient = False

        out1 = paddle.argsort(x1, axis=-1)
        out2 = paddle.argsort(x2, axis=0)
        out1.retain_grads()
        out2.retain_grads()

        out1.backward()
        out2.backward()

        self.assertEqual(out1.shape, [])
        self.assertEqual(out2.shape, [])
        self.assertEqual(out1.numpy(), 0)
        self.assertEqual(out2.numpy(), 0)
        self.assertEqual(out1.grad.shape, [])
        self.assertEqual(out2.grad.shape, [])
        self.assertEqual(x1.grad.shape, [])
        self.assertEqual(x2.grad.shape, [])
        self.assertEqual(x1.grad.numpy(), 0)
        self.assertEqual(x2.grad.numpy(), 0)

    def test_unstack(self):
        x1 = paddle.full([1], 0)
        x2 = paddle.full([2], 2)
        x1.retain_grads()
        x2.retain_grads()
        x1.stop_gradient = False
        x2.stop_gradient = False

        [out1] = paddle.unstack(x1, 0)
        out1.retain_grads()
        out1.backward()
        [out2_1, out2_2] = paddle.unstack(x2, 0)
        out2 = paddle.add_n([out2_1, out2_2])
        out2.retain_grads()
        out2.backward()

        self.assertEqual(out1.shape, [])
        self.assertEqual(out1.numpy(), 0)

        self.assertEqual(out2_1.shape, [])
        self.assertEqual(out2_1.numpy(), 2)
        self.assertEqual(out2_2.shape, [])
        self.assertEqual(out2_2.numpy(), 2)
        self.assertEqual(x2.grad.shape, [2])

    def test_maseked_select(self):
        # have no backward, not register
        x = paddle.rand([])
        mask = paddle.full([], True, dtype="bool")
        y = paddle.masked_select(x, mask)

        self.assertEqual(y.shape, [1])
        self.assertEqual(y.numpy(), x.numpy())

    def test_squeeze(self):
        x1 = paddle.full([], 2)
        x1.stop_gradient = False
        x1.retain_grads()
        out1 = paddle.squeeze(x1, axis=0)
        out1.retain_grads()
        out1.backward()
        self.assertEqual(out1.shape, [])
        self.assertEqual(x1.grad.shape, [])

        x2 = paddle.full([], 3)
        x3 = paddle.full([1], 0, dtype="int32")
        x2.stop_gradient = False
        x2.retain_grads()
        out2 = paddle.squeeze(x2, axis=x3)
        out2.retain_grads()
        out2.backward()
        self.assertEqual(out2.shape, [])
        self.assertEqual(x2.grad.shape, [])

    def test_unsqueeze(self):
        x1 = paddle.full([], 2)
        x1.stop_gradient = False
        out1 = paddle.unsqueeze(x1, axis=0)
        out1.retain_grads()
        out1.backward()
        self.assertEqual(out1.shape, [1])
        self.assertEqual(x1.grad.shape, [])

        x2 = paddle.full([], 0, dtype="int32")
        out2 = paddle.unsqueeze(x1, axis=x2)
        out2.retain_grads()
        out2.backward()
        self.assertEqual(out2.shape, [1])

    def test_prelu(self):
        x1 = paddle.full([], 1.0, "float32")
        x1.stop_gradient = False
        w1 = paddle.full([], 0.25, dtype="float32")
        w1.stop_gradient = False
        out1 = paddle.nn.functional.prelu(x1, w1)
        out1.retain_grads()
        out1.backward()
        self.assertEqual(out1.shape, [])
        self.assertEqual(out1.numpy(), 1.0)
        self.assertEqual(out1.grad.shape, [])
        self.assertEqual(x1.grad.shape, [])
        self.assertEqual(x1.grad.numpy(), 1.0)

    def test_cov(self):
        xt = paddle.randn((3, 4))
        xt.stop_gradient = False
        xt_1 = paddle.randn((12,))
        xt_1.stop_gradient = False

        xt_out = paddle.linalg.cov(xt)
        xt_out.retain_grads()
        xt_out.backward()
        self.assertEqual(xt_out.shape, [3, 3])
        self.assertEqual(xt.grad.shape, [3, 4])

        xt_1_out = paddle.linalg.cov(xt_1)
        xt_1.retain_grads()
        xt_1_out.backward()
        self.assertEqual(xt_1_out.shape, [])
        self.assertEqual(xt_1.grad.shape, [12])

    def test_is_empty(self):
        # 1) x is 0D
        x = paddle.rand([])
        out = paddle.is_empty(x)
        self.assertFalse(out)
        self.assertEqual(out.shape, [])

        # 2) x is 1D
        x = paddle.rand([5])
        out = paddle.is_empty(x)
        self.assertFalse(out)
        self.assertEqual(out.shape, [])

        # 3) x is ND
        x = paddle.rand([3, 5])
        out = paddle.is_empty(x)
        self.assertFalse(out)
        self.assertEqual(out.shape, [])

        x = paddle.rand([3, 0, 5])
        out = paddle.is_empty(x)
        self.assertTrue(out)
        self.assertEqual(out.shape, [])

    def test_squeeze_(self):
        # 1) x is 0D
        x = paddle.rand([])
        x.squeeze_(0)
        self.assertEqual(x.shape, [])

        # 2) x is 1D
        x = paddle.rand([1])
        x.squeeze_(0)
        self.assertEqual(x.shape, [])

        # 3）x is ND
        x = paddle.rand([2, 1])
        x.squeeze_(1)
        self.assertEqual(x.shape, [2])

    def test_inner(self):
        # 0) input is 0D
        x = paddle.rand([])
        x.stop_gradient = False
        y = paddle.rand([])
        y.stop_gradient = False
        out = paddle.inner(x, y)
        out.retain_grads()
        out.backward()

        self.assertEqual(x.grad.shape, [])
        self.assertEqual(out.shape, [])
        self.assertEqual(out.grad.shape, [])

        # 1) input is 1D
        x = paddle.rand([2])
        x.stop_gradient = False
        y = paddle.rand([2])
        y.stop_gradient = False
        out = paddle.inner(x, y)
        out.retain_grads()
        out.backward()

        self.assertEqual(x.grad.shape, [2])
        self.assertEqual(out.shape, [])
        self.assertEqual(out.grad.shape, [])

        # 2) input is 2D
        x = paddle.rand([2, 3])
        x.stop_gradient = False
        y = paddle.rand([3, 3])
        y.stop_gradient = False
        out = paddle.inner(x, y)
        out.retain_grads()
        out.backward()

        self.assertEqual(x.grad.shape, [2, 3])
        self.assertEqual(out.shape, [2, 3])
        self.assertEqual(out.grad.shape, [2, 3])

    def test_tensordot(self):

        # 1) input is 1D
        x = paddle.arange(10, dtype="float64")
        x.stop_gradient = False
        y = paddle.arange(10, dtype="float64")
        y.stop_gradient = False
        out = paddle.tensordot(x, y, axes=1)
        out.retain_grads()
        out.backward()

        self.assertEqual(x.grad.shape, [10])
        self.assertEqual(out.shape, [])
        self.assertEqual(out.grad.shape, [])

        # 2) input is 2D
        x = paddle.arange(6, dtype="float64").reshape([2, 3])
        y = paddle.arange(6, dtype="float64").reshape([2, 3])
        x.stop_gradient = False
        out = paddle.tensordot(x, y, axes=2)
        out.retain_grads()
        out.backward()

        self.assertEqual(x.grad.shape, [2, 3])
        self.assertEqual(out.shape, [])
        self.assertEqual(out.grad.shape, [])

    def test_metric_accuracy(self):
        x = paddle.full(shape=[2, 4], fill_value=0.25)
        y = paddle.full(shape=[2, 1], fill_value=1, dtype="int64")
        out = paddle.metric.accuracy(input=x, label=y, k=1)
        self.assertEqual(out.shape, [])

    def test_std(self):
        # 1) x is 0D
        x = paddle.rand([])
        x.stop_gradient = False
        out1 = paddle.std(x)
        out2 = paddle.std(x, [])
        out1.backward()
        out2.backward()

        self.assertEqual(out1.shape, [])
        self.assertEqual(out2.shape, [])
        self.assertLess(np.abs(out1.numpy()), 1e-8)
        self.assertLess(np.abs(out2.numpy()), 1e-8)

        self.assertEqual(x.grad.shape, [])

        # 2) x is ND
        x = paddle.rand([3, 5])
        x.stop_gradient = False
        out = paddle.std(x)
        out.backward()

        self.assertEqual(out.shape, [])
        self.assertEqual(x.grad.shape, [3, 5])

    def test_var(self):
        # 1) x is 0D
        x = paddle.rand([])
        x.stop_gradient = False
        out1 = paddle.var(x)
        out2 = paddle.var(x, [])
        out1.backward()
        out2.backward()

        self.assertEqual(out1.shape, [])
        self.assertEqual(out2.shape, [])
        self.assertEqual(out1, 0)
        self.assertEqual(out2, 0)

        self.assertEqual(x.grad.shape, [])
        np.testing.assert_allclose(x.grad, 0)

        # 2) x is ND
        x = paddle.rand([3, 5])
        x.stop_gradient = False
        out = paddle.std(x)
        out.backward()

        self.assertEqual(out.shape, [])
        self.assertEqual(x.grad.shape, [3, 5])

    def test_interpolate(self):
        from paddle.nn.functional import interpolate

        input_x = paddle.rand([2, 3, 6, 6])
        input_x.stop_gradient = False
        origin_result = interpolate(
            x=input_x, size=[12, 12], mode="bilinear", align_corners=False
        )

        output_size = [
            paddle.full([], 12, dtype="int32"),
            paddle.full([], 12, dtype="int32"),
        ]
        out1 = interpolate(
            x=input_x, size=output_size, mode="bilinear", align_corners=False
        )
        out1.backward()

        self.assertEqual(out1.shape, [2, 3, 12, 12])
        self.assertEqual(input_x.grad.shape, [2, 3, 6, 6])

        scale_1 = [paddle.full([], 2), paddle.full([], 2)]
        out2 = interpolate(
            x=input_x,
            scale_factor=scale_1,
            mode="bilinear",
            align_corners=False,
        )
        out2.backward()

        self.assertEqual(out2.shape, [2, 3, 12, 12])
        self.assertEqual(input_x.grad.shape, [2, 3, 6, 6])

        scale_2 = paddle.full([], 2)
        out3 = interpolate(
            x=input_x,
            scale_factor=scale_2,
            mode="bilinear",
            align_corners=False,
        )
        out3.backward()

        self.assertEqual(out3.shape, [2, 3, 12, 12])
        self.assertEqual(input_x.grad.shape, [2, 3, 6, 6])

        np.testing.assert_allclose(origin_result.numpy(), out1.numpy(), rtol=1e-05)
        np.testing.assert_allclose(origin_result.numpy(), out2.numpy(), rtol=1e-05)
        np.testing.assert_allclose(origin_result.numpy(), out3.numpy(), rtol=1e-05)


# Use to test API whose zero-dim input tensors don't have grad and not need to test backward in OpTest.
class TestNoBackwardAPI(unittest.TestCase):
    def setUp(self):
        paddle.disable_static()
        set_sdaa()
        self.shape = [
            paddle.full([], 2, "int32"),
            paddle.full([], 3, "int32"),
            paddle.full([], 4, "int32"),
        ]

    def test_slice(self):
        starts = [paddle.full([], 1, "int32"), paddle.full([], 1, "int32")]
        ends = [paddle.full([], 3, "int32"), paddle.full([], 3, "int32")]
        x = paddle.rand([5, 3, 3])
        out = paddle.slice(x, [1, 2], starts, ends)
        self.assertEqual(out.shape, [5, 2, 2])

    def test_strided_slice(self):
        starts = [paddle.full([], 0, "int32"), paddle.full([], 0, "int32")]
        ends = [paddle.full([], 4, "int32"), paddle.full([], 4, "int32")]
        strides = [paddle.full([], 2, "int32"), paddle.full([], 2, "int32")]
        x = paddle.rand([5, 5, 5])
        out = paddle.strided_slice(x, [1, 2], starts, ends, strides)
        self.assertEqual(out.shape, [5, 2, 2])

    def test_linspace(self):
        start = paddle.full([], 1.0)
        stop = paddle.full([], 5.0)
        num = paddle.full([], 5, "int32")
        out = paddle.linspace(start, stop, num)
        np.testing.assert_array_equal(out.numpy(), [1.0, 2.0, 3.0, 4.0, 5.0])

    def test_arange(self):
        start = paddle.full([], 1.0)
        stop = paddle.full([], 6.0)
        step = paddle.full([], 1.0)
        out = paddle.arange(start, stop, step)
        np.testing.assert_array_equal(out.numpy(), [1.0, 2.0, 3.0, 4.0, 5.0])

    def test_normal(self):
        mean = paddle.full([], 0.0)
        std = paddle.full([], 0.0)
        out = paddle.normal(mean, std)
        self.assertEqual(out.shape, [])

        out = paddle.normal(0.0, 1.0, [])
        self.assertEqual(out.shape, [])

        out = paddle.normal(0.0, 1.0, self.shape)
        self.assertEqual(out.shape, [2, 3, 4])

    def test_rand(self):
        out = paddle.rand([])
        self.assertEqual(out.shape, [])

        out = paddle.rand(self.shape)
        self.assertEqual(out.shape, [2, 3, 4])

    def test_randn(self):
        out = paddle.randn([])
        self.assertEqual(out.shape, [])

        out = paddle.randn(self.shape)
        self.assertEqual(out.shape, [2, 3, 4])

    def test_randint_and_randint_like(self):
        out = paddle.randint(-10, 10, [])
        self.assertEqual(out.shape, [])

        out = paddle.randint_like(out, -10, 10)
        self.assertEqual(out.shape, [])

        out = paddle.randint(-10, 10, self.shape)
        self.assertEqual(out.shape, [2, 3, 4])

    def test_standard_normal(self):
        out = paddle.standard_normal([])
        self.assertEqual(out.shape, [])

        out = paddle.standard_normal(self.shape)
        self.assertEqual(out.shape, [2, 3, 4])

    def test_uniform(self):
        out = paddle.uniform([])
        self.assertEqual(out.shape, [])

        out = paddle.uniform(self.shape)
        self.assertEqual(out.shape, [2, 3, 4])

    def test_empty_and_empty_like(self):
        out = paddle.empty([])
        self.assertEqual(out.shape, [])

        out = paddle.empty_like(out)
        self.assertEqual(out.shape, [])

        out = paddle.empty(self.shape)
        self.assertEqual(out.shape, [2, 3, 4])

    def test_full_and_full_like(self):
        out = paddle.full([], 0.5)
        self.assertEqual(out.shape, [])

        out = paddle.full_like(out, 0.5)
        self.assertEqual(out.shape, [])

        out = paddle.full(self.shape, 0.5)
        self.assertEqual(out.shape, [2, 3, 4])

    def test_ones_and_ones_like(self):
        out = paddle.ones([])
        self.assertEqual(out.shape, [])

        out = paddle.ones_like(out)
        self.assertEqual(out.shape, [])

        out = paddle.ones(self.shape)
        self.assertEqual(out.shape, [2, 3, 4])

    def test_zeros_and_zeros_like(self):
        out = paddle.zeros([])
        self.assertEqual(out.shape, [])

        out = paddle.zeros_like(out)
        self.assertEqual(out.shape, [])

        out = paddle.zeros(self.shape)
        self.assertEqual(out.shape, [2, 3, 4])

    def test_embedding(self):
        ids = paddle.full(shape=[], fill_value=1, dtype="int64")
        w0 = paddle.arange(3, 9).reshape((3, 2)).astype(paddle.float32)
        w = paddle.to_tensor(w0, stop_gradient=False)
        emb = paddle.nn.functional.embedding(
            x=ids, weight=w, sparse=True, name="embedding"
        )
        self.assertEqual(emb.shape, [2])
        res = [5.0, 6.0]
        for i in range(len(res)):
            self.assertEqual(emb.numpy()[i], res[i])

    def test_one_hot_label(self):
        label = paddle.full(shape=[], fill_value=2, dtype="int64")
        one_hot_label = paddle.nn.functional.one_hot(label, num_classes=4)
        self.assertEqual(one_hot_label.shape, [4])
        self.assertEqual(one_hot_label.numpy()[2], 1)


class TestLossAPI(unittest.TestCase):
    def setUp(self):
        paddle.disable_static()
        set_sdaa()

    def test_sigmoid_focal_loss(self):
        logit = paddle.to_tensor(
            [[0.97, 0.91, 0.03], [0.55, 0.43, 0.71]],
            dtype="float32",
            stop_gradient=False,
        )
        logit.retain_grads()
        label = paddle.to_tensor([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype="float32")
        fg_num_0 = paddle.full([], 2.0)
        fg_num_1 = paddle.full([1], 2.0)

        out0 = F.sigmoid_focal_loss(logit, label, normalizer=fg_num_0, reduction="sum")
        out1 = F.sigmoid_focal_loss(logit, label, normalizer=fg_num_1, reduction="sum")
        out0.retain_grads()

        np.testing.assert_array_equal(
            out0.numpy(),
            out1.numpy(),
        )

        out0.backward()
        self.assertEqual(out0.shape, [])
        self.assertEqual(out1.shape, [])
        self.assertEqual(out0.grad.shape, [])
        self.assertEqual(logit.grad.shape, [2, 3])

    def test_cross_entropy(self):
        input = paddle.rand([3, 5])
        input.stop_gradient = False
        label = paddle.randint(0, 5, shape=[3])

        loss = paddle.nn.functional.cross_entropy(input, label, reduction="sum")
        loss.backward()

        self.assertEqual(loss.shape, [])
        self.assertEqual(input.grad.shape, [3, 5])

    def test_l1_loss(self):
        input = paddle.rand([3, 5])
        input.stop_gradient = False
        label = paddle.rand([3, 5])

        loss = paddle.nn.functional.l1_loss(input, label, reduction="mean")
        loss.backward()

        self.assertEqual(loss.shape, [])
        self.assertEqual(input.grad.shape, [3, 5])


if __name__ == "__main__":
    unittest.main()

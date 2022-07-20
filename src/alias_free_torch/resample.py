import torch
import torch.nn as nn
import torch.nn.functional as F
from .filter import LowPassFilter1d, LowPassFilter2d
from .filter import kaiser_sinc_filter1d, kaiser_jinc_filter2d


class UpSample1d(nn.Module):
    def __init__(self, ratio=2, kernel_size=None):
        super().__init__()
        self.ratio = ratio
        self.kernel_size = int(6 * ratio // 2) * 2 if kernel_size is None else kernel_size
        self.stride = ratio
        self.pad = self.kernel_size // ratio - 1
        filter = kaiser_sinc_filter1d(cutoff=0.5 / ratio,
                                    half_width=0.6 / ratio,
                                    kernel_size=self.kernel_size)
        self.register_buffer("filter", filter)

    # x: [B,C,T]
    def forward(self, x):
        C = x.shape[1]
        x = F.pad(x, (self.pad, self.pad), mode = 'reflect')
        x = self.ratio * F.conv_transpose1d(
            x, self.filter, stride=self.stride, groups=C)
        pad_left = self.pad * self.stride + (self.kernel_size - self.stride) // 2
        pad_right = self.pad * self.stride + (self.kernel_size - self.stride + 1) // 2
        x = x[..., pad_left:-pad_right]
        return x


class DownSample1d(nn.Module):
    def __init__(self, ratio=2, kernel_size=None):
        super().__init__()
        self.ratio = ratio
        self.kernel_size = int(6 * ratio // 2) * 2 if kernel_size is None else kernel_size
        self.lowpass = LowPassFilter1d(cutoff=0.5 / ratio,
                                       half_width=0.6 / ratio,
                                       stride=ratio,
                                       kernel_size=self.kernel_size)

    def forward(self, x):
        xx = self.lowpass(x)
        return xx


class UpSample2d(nn.Module):
    def __init__(self, ratio=2, kernel_size=None):
        super().__init__()
        self.ratio = ratio
        self.kernel_size = int(6 * ratio // 2) * 2 if kernel_size is None else kernel_size
        self.stride = ratio
        self.pad = kernel_size // 2 - ratio // 2
        filter = kaiser_jinc_filter2d(cutoff=0.5 / ratio,
                                           half_width=0.6 / ratio,
                                           kernel_size=kernel_size)
        self.register_buffer("filter", filter)

    # x: [B,C,W,H]
    def forward(self, x):
        C = x.shape[1]
        x = F.pad(x, (self.pad, self.pad, self.pad, self.pad), mode = 'reflect')
        x = self.ratio**2 * F.conv_transpose2d(
            x, self.filter, stride=self.stride, groups=C)
        pad_left = self.pad * self.stride + (self.kernel_size - self.stride) // 2
        pad_right = self.pad * self.stride + (self.kernel_size - self.stride + 1) // 2
        x = x[...,pad_left:-pad_right, pad_left:-pad_right]
        return x


class DownSample2d(nn.Module):
    def __init__(self, ratio=2, kernel_size=None):
        super().__init__()
        self.ratio = ratio
        self.kernel_size = int(6 * ratio // 2) * 2 if kernel_size is None else kernel_size
        self.lowpass = LowPassFilter2d(cutoff=0.5 / ratio,
                                       half_width=0.6 / ratio,
                                       stride=ratio,
                                       kernel_size=self.kernel_size)

    def forward(self, x):
        xx = self.lowpass(x)
        return xx

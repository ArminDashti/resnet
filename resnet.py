# For more information
# https://debuggercafe.com/building-resnets-from-scratch-using-pytorch/

import torch.nn as nn
import torch
from torch import Tensor

class BasicBlock(nn.Module):
    def __init__(self, num_layers, in_channels, out_channels, stride=1, expansion=1, downsample=None):
        super(BasicBlock, self).__init__()
        self.num_layers = num_layers
        self.expansion = expansion
        self.downsample = downsample
        if num_layers > 34:
            self.conv0 = nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1, bias=False)
            self.bn0 = nn.BatchNorm2d(out_channels)
            in_channels = out_channels
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        if num_layers > 34:
            self.conv2 = nn.Conv2d(out_channels, out_channels*self.expansion, kernel_size=1, stride=1, bias=False)
            self.bn2 = nn.BatchNorm2d(out_channels*self.expansion)
        else:
            self.conv2 = nn.Conv2d(out_channels, out_channels*self.expansion, kernel_size=3, padding=1, bias=False)
            self.bn2 = nn.BatchNorm2d(out_channels*self.expansion)
        self.relu = nn.ReLU(inplace=True)
        
    def forward(self, x):
        identity = x
        if self.num_layers > 34:
            out = self.conv0(x)
            out = self.bn0(out)
            out = self.relu(out)
        if self.num_layers > 34:
            out = self.conv1(out)
        else:
            out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        if self.downsample is not None:
            identity = self.downsample(x)
        out = identity + out
        out = self.relu(out)
        return  out
    
    
class ResNet(nn.Module):
    def __init__(self, img_channels, num_layers, block, num_classes=1000):
        super(ResNet, self).__init__()
        if num_layers == 18:
            layers = [2, 2, 2, 2]
            self.expansion = 1
        if num_layers == 34:
            layers = [3, 4, 6, 3]
            self.expansion = 1
        if num_layers == 50:
            layers = [3, 4, 6, 3]
            self.expansion = 4
        if num_layers == 101:
            layers = [3, 4, 23, 3]
            self.expansion = 4
        if num_layers == 152:
            layers = [3, 8, 36, 3]
            self.expansion = 4
        self.in_channels = 64
        self.conv1 = nn.Conv2d(in_channels=img_channels, out_channels=self.in_channels, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(self.in_channels)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(block, 64, layers[0], num_layers=num_layers)
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2, num_layers=num_layers)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2, num_layers=num_layers)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2, num_layers=num_layers)
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512*self.expansion, num_classes)
        
    def _make_layer(self, block, out_channels, blocks, stride=1, num_layers=18):
        downsample = None
        if stride != 1 or self.in_channels != out_channels * self.expansion:
            downsample = nn.Sequential(nn.Conv2d(self.in_channels, out_channels*self.expansion, kernel_size=1,
                                                 stride=stride,bias=False),nn.BatchNorm2d(out_channels * self.expansion),)
        layers = []
        layers.append(block(num_layers, self.in_channels, out_channels, stride, self.expansion, downsample))
        self.in_channels = out_channels * self.expansion
        for i in range(1, blocks):
            layers.append(block(num_layers, self.in_channels, out_channels, expansion=self.expansion))
        return nn.Sequential(*layers)
    
    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x
    
   
model = ResNet(img_channels=3, num_layers=18, block=BasicBlock, num_classes=1000)
#%%
i = 2
j = 3
j += i
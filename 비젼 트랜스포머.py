# -*- coding: utf-8 -*-
"""비젼 트랜스포머

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EuqQTUhlCK8xOXTNhcqG1xCLt0WfoMza
"""

import torch
import torch.nn as nn

random_image = torch.randn(1,3,224,224)

conv2d = nn.Conv2d(in_channels = 3,
                             out_channels = 768,
                             kernel_size = 16,
                             stride=16,
                             padding=0)

# conv2d(demo_img).shape
# flatten = nn.Flatten(start_dim=2,end_dim=3)
# flatten(conv2d(demo_img)).shape

class patchembedding(nn.Module):
  #conv2d로 patch를 설정
  def __init__(self,in_channels=3,patchsize=16,embeddingdim=768):
    super().__init__() #nn.Module 상속
    # 이미지를 patch로 바꾸는 과정 3channel 에서 768개 channel로
    self.patcher = nn.Conv2d(in_channels = in_channels,
                             out_channels = embeddingdim,
                             kernel_size = patchsize,
                             stride=patchsize,
                             padding=0)
    self.patchsize = patchsize
    #patch feature을 1차원 벡터로 flatten
    self.flatten = nn.Flatten(start_dim=2,end_dim=3)
    # batch, channel, width,height이라 가정하면 width,height를 flatten
  def forward(self,x):
    resolution = x.shape[-1] #x의 마지막dim은 해상도

    assert resolution % self.patchsize == 0, f'입력해상도 {resolution}은 패치크기인 {patchsize}로 나눠지지 않습니다/ '
                            # class 생성자의 patchsize self로 설정 x
     #perform
    patch_x = self.patcher(x)
    flatten_x = self.flatten(patch_x)

    return flatten_x.permute(0, 2, 1)
    #  [batch_size, P^2•C, N] p = patchsize c = channel 임베딩을 마지막dim으로 재정렬
                  # batchsize |16제곱 * num_channel 3 = 768



embedder = patchembedding()
# pytorch color channel shape[1]에
patched_image=embedder(random_image)
patched_image.shape

#transformer encoder layer
encoder_layer = nn.TransformerEncoderLayer(d_model=768,#모델의 입력과 출력 벡터는 512차원
                                           nhead=12,
                                           dim_feedforward=3072,
                                           dropout=0.1,
                                           activation='gelu',
                                           batch_first=True,
                                           norm_first=True) #batchsize 가 shape[0]
encoder_layer

!pip install torchinfo
from torchinfo import summary
summary(model=encoder_layer,
        input_size=patched_image.shape)
# 1,3,224,224 -> 1,768,196
# 224,224 img 를 16,16 patch 로 16칸씩 옮겨가면 14*14 로 특징이 추출되서 축소된다
# inchannel 3 -> embedded_outchannel 768
# 임베딩 디멘션은 shape[-1]로 permute

transformer_encoder = nn.TransformerEncoder(encoder_layer=encoder_layer,
                                            num_layers=12)
#nn.Transformerencoder layer 12겹

class vit(nn.Module):
  def __init__(self,
               imgsize=224,
               patchsize=16,
               numchannel=3,
               embeddingdim=768,
               mlpsize=3072,#multi layer perceptron
               dropout=0.1, #10% 비활성화 뉴런
               num_transformer_layers=12,
               numheads=12,
               numclasses =1000): # 768/12 가 head 마다 embedding수
    super().__init__()
    #위의 patch embedding과정과 마찬가지로 image size 가 patchsize로 나뉘어야됨 아닐경우 error message
    assert imgsize % patchsize == 0, "이미지 사이즈가 패치사이즈로 나뉘어지지 않습니다"

    # 패치 임베딩 patch embedding
    self.patchembedding = patchembedding(in_channels = numchannel,patchsize =patchsize,
                                        embeddingdim = embeddingdim)
    #----------------------------------------------------------------
    #parameter로써 차원만 맞춰주면 계속 optimizer로 update됨
    # 클래스 토큰
    #이미지 전체에 대한 하나의 임베딩 모든패치 정보 종합 patched x = (1,196,768) 이므로 196 = 14 x 14 패치개수
    self.classtoken = nn.Parameter(torch.randn(1,1,embeddingdim),requires_grad=True)

    # 위치 정보 임베딩 positional embedding
    num_patches = (imgsize*imgsize) //patchsize**2
    self.positionalembedding = nn.Parameter(torch.randn(1,num_patches+1,embeddingdim))
    #  전체 이미지나 전역 위치에 대한 추가 학습 가능한 positional embedding을 포함시키기 위해 추가됨.
    # ---------------------------------------------------------------

    # dropout positional / patch embedding
    self.embeddingdropout = nn.Dropout(p=dropout)

    # 트랜스포머 인코더 layers 생성
    # self.encoder_layer = nn.TransformerEncoderLayer(d_model=embeddingdim,
    #                                                 nhead=numheads,
    #                                                 dim_feedforward = mlpsize,
    #                                                 activation='gelu',
    #                                                 batch_first=True,
    #                                                 norm_first=True)

    self.encoder = nn.TransformerEncoder(encoder_layer= nn.TransformerEncoderLayer(d_model=embeddingdim,
                                                                                  nhead=numheads,
                                                                                  dim_feedforward = mlpsize,
                                                                                  activation='gelu',
                                                                                  batch_first=True,
                                                                                  norm_first=True),
                                         num_layers=num_transformer_layers-1)
    # MLP head 생성
    self.mlphead = nn.Sequential(nn.LayerNorm(normalized_shape=embeddingdim),
                                nn.Linear(in_features=embeddingdim,
                                out_features= numclasses)
    )

  def forward(self,x):
    batchsize = x.shape[0]
    #패치 임베딩
    x =  self.patchembedding(x)
      #x 가 conv2d 16size kernel 즉 패치 통과 후flatten 통과한 값

    #클래스토큰
    classtoken = self.classtoken.expand(batchsize,-1,-1)
    #classtoken patchembedding과 concat할수있도록 shape 맞추기
    x = torch.cat((classtoken,x),dim=1)
    print(x.shape)

    #위치 임베딩
    x= x + self.positionalembedding
    print(x.shape)

    #뉴런 비활성화
    x = self.embeddingdropout(x)
    print(x.shape)

    #인코더 통과
    x = self.encoder(x)
    print(x.shape)
    # MLP 통과
    x = self.mlphead(x[:,0])

    return x

VIT = vit(numclasses=3)
demo_img= torch.randn(32,3,224,224)
VIT(demo_img)
# patcher = patchembedding()
# patched_img = patcher(demo_img)
# patched_img.shape
# 32,3,224,224 -> 32,197,768
#----------------------------------
# 32,3,224,224 patch 32,196,768 ->
# classtoken (1,1,768) | expanded_classtoken = (32,1,768) ->
# torch.cat -> 32,197,768

summary(model=VIT,
        input_size=demo_img.shape)

# classtoken = nn.Parameter(torch.randn(1,1,768),requires_grad=True)
# expandedclasstoken = classtoken.expand(32,-1,-1)
# expandedclasstoken.shape

"""![download.png](data:image/png;base64,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)"""

# Commented out IPython magic to ensure Python compatibility.
# %%writefile vit.py
# 
# import torch
# import torch.nn as nn
# class patchembedding(nn.Module):
#   #conv2d로 patch를 설정
#   def __init__(self,in_channels=3,patchsize=16,embeddingdim=768):
#     super().__init__() #nn.Module 상속
#     # 이미지를 patch로 바꾸는 과정 3channel 에서 768개 channel로
#     self.patcher = nn.Conv2d(in_channels = in_channels,
#                              out_channels = embeddingdim,
#                              kernel_size = patchsize,
#                              stride=patchsize,
#                              padding=0)
#     self.patchsize = patchsize
#     #patch feature을 1차원 벡터로 flatten
#     self.flatten = nn.Flatten(start_dim=2,end_dim=3)
#     # batch, channel, width,height이라 가정하면 width,height를 flatten
#   def forward(self,x):
#     resolution = x.shape[-1] #x의 마지막dim은 해상도
# 
#     assert resolution % self.patchsize == 0, f'입력해상도 {resolution}은 패치크기인 {patchsize}로 나눠지지 않습니다/ '
#                             # class 생성자의 patchsize self로 설정 x
#      #perform
#     patch_x = self.patcher(x)
#     flatten_x = self.flatten(patch_x)
# 
#     return flatten_x.permute(0, 2, 1)
#     #  [batch_size, P^2•C, N] p = patchsize c = channel 임베딩을 마지막dim으로 재정렬
#                   # batchsize |16제곱 * num_channel 3 = 768
# 
# class vit(nn.Module):
#   def __init__(self,
#                imgsize=224,
#                patchsize=16,
#                numchannel=3,
#                embeddingdim=768,
#                mlpsize=3072,#multi layer perceptron
#                dropout=0.1, #10% 비활성화 뉴런
#                num_transformer_layers=12,
#                numheads=12,
#                numclasses =1000): # 768/12 가 head 마다 embedding수
#     super().__init__()
#     #위의 patch embedding과정과 마찬가지로 image size 가 patchsize로 나뉘어야됨 아닐경우 error message
#     assert imgsize % patchsize == 0, "이미지 사이즈가 패치사이즈로 나뉘어지지 않습니다"
# 
#     # 패치 임베딩 patch embedding
#     self.patchembedding = patchembedding(in_channels = numchannel,patchsize =patchsize,
#                                         embeddingdim = embeddingdim)
#     #----------------------------------------------------------------
#     #parameter로써 차원만 맞춰주면 계속 optimizer로 update됨
#     # 클래스 토큰
#     #이미지 전체에 대한 하나의 임베딩 모든패치 정보 종합 patched x = (1,196,768) 이므로 196 = 14 x 14 패치개수
#     self.classtoken = nn.Parameter(torch.randn(1,1,embeddingdim),requires_grad=True)
# 
#     # 위치 정보 임베딩 positional embedding
#     num_patches = (imgsize*imgsize) //patchsize**2
#     self.positionalembedding = nn.Parameter(torch.randn(1,num_patches+1,embeddingdim))
#     #  전체 이미지나 전역 위치에 대한 추가 학습 가능한 positional embedding을 포함시키기 위해 추가됨.
#     # ---------------------------------------------------------------
# 
#     # dropout positional / patch embedding
#     self.embeddingdropout = nn.Dropout(p=dropout)
# 
#     # 트랜스포머 인코더 layers 생성
#     # self.encoder_layer = nn.TransformerEncoderLayer(d_model=embeddingdim,
#     #                                                 nhead=numheads,
#     #                                                 dim_feedforward = mlpsize,
#     #                                                 activation='gelu',
#     #                                                 batch_first=True,
#     #                                                 norm_first=True)
# 
#     self.encoder = nn.TransformerEncoder(encoder_layer= nn.TransformerEncoderLayer(d_model=embeddingdim,
#                                                                                   nhead=numheads,
#                                                                                   dim_feedforward = mlpsize,
#                                                                                   activation='gelu',
#                                                                                   batch_first=True,
#                                                                                   norm_first=True),
#                                          num_layers=num_transformer_layers-1)
#     # MLP head 생성
#     self.mlphead = nn.Sequential(nn.LayerNorm(normalized_shape=embeddingdim),
#                                 nn.Linear(in_features=embeddingdim,
#                                 out_features= numclasses)
#     )
# 
#   def forward(self,x):
#     batchsize = x.shape[0]
#     #패치 임베딩
#     x =  self.patchembedding(x)
#       #x 가 conv2d 16size kernel 즉 패치 통과 후flatten 통과한 값
# 
#     #클래스토큰
#     classtoken = self.classtoken.expand(batchsize,-1,-1)
#     #classtoken patchembedding과 concat할수있도록 shape 맞추기
#     x = torch.cat((classtoken,x),dim=1)
#     print(x.shape)
# 
#     #위치 임베딩
#     x= x + self.positionalembedding
#     print(x.shape)
# 
#     #뉴런 비활성화
#     x = self.embeddingdropout(x)
#     print(x.shape)
# 
#     #인코더 통과
#     x = self.encoder(x)
#     print(x.shape)
#     # MLP 통과
#     x = self.mlphead(x[:,0])
# 
#     return x

!python.vit.py

# %%writefile 로 쉽게 원하는class import
from vit import vit

import torchvision
weight = torchvision.models.ViT_B_16_Weights
pretr_vit = torchvision.models.vit_b_16(weights=weight)

for p in pretr_vit.parameters():
  p.requires_grad=False

embeddingdim= 768
pretr_vit.head= nn.Sequential(
    nn.LayerNorm(normalized_shape=embeddingdim),
    nn.Linear(in_features=embeddingdim,out_features=len(class_names)))
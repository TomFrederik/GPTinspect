import logging
from typing import Iterable

import numpy as np
import pytest
import torch
from unseal.hooks import util


def test_create_slice_from_str():
    arr = np.random.rand(10,10,10)
    valid_idx_strings = [
        '...,3:5,:',
        '4:5,:,:',
        '0,0,0',
        '-1,-1,-1'
    ]
    valid_result_arrs = [
        arr[...,3:5,:],
        arr[4:5,:,:],
        arr[0,0,0],
        arr[-1,-1,-1],
    ]
    for string, subarr in zip(valid_idx_strings, valid_result_arrs):
        assert np.all(arr[util.create_slice_from_str(string)] == subarr), f"{util.create_slice_from_str(string)}, {subarr}"
    
    invalid_idx_strings = [
        '',
    ]     
    for idx in invalid_idx_strings:
        with pytest.raises(ValueError):
            subarry = arr[util.create_slice_from_str(idx)]

####

def test_recursive_to_device():
    if not torch.cuda.is_available():
        logging.warning('CUDA not available, skipping recursive_to_device test.')
        return
    
    tensor = torch.rand(10,10)
    tensor = util.recursive_to_device(tensor, torch.device('cuda'))
    nested_list = [tensor, [[tensor], tensor]]
    nested_tuple = (tensor, [(tensor,), tensor])
    
    recursive_cuda_check(tensor)
    recursive_cuda_check(nested_list)
    recursive_cuda_check(nested_tuple)    

def recursive_cuda_check(iterable):
    if isinstance(iterable, torch.Tensor):
        assert iterable.device.type == 'cuda'
    elif isinstance(iterable, Iterable):
        for item in iterable:
            recursive_cuda_check(item)

#####

def test_recursive_detach():
    undetach_tensor = torch.rand(10,10, requires_grad=True)
    tensor = util.recursive_detach(undetach_tensor)
    nested_list = [tensor, [[tensor], tensor]]
    nested_tuple = (tensor, [(tensor,), tensor])
    empty_list = []
    empty_tuple = tuple([])
    
    assert undetach_tensor.requires_grad
    recursive_detach_check(tensor)
    recursive_detach_check(nested_list)
    recursive_detach_check(nested_tuple)    
    recursive_detach_check(empty_list)    
    recursive_detach_check(empty_tuple)    

def recursive_detach_check(iterable):
    if isinstance(iterable, torch.Tensor):
        assert not iterable.requires_grad
    elif isinstance(iterable, Iterable):
        for item in iterable:
            recursive_detach_check(item)
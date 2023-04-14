from typing import Sequence, Tuple

import einops
import torch


def get_patch_centers_1d(
    dim_length: int,
    patch_length: int,
    patch_step: int,
    distribute_patches: bool = True,
    device: torch.device = None
) -> torch.Tensor:
    min = patch_length // 2
    max = dim_length - min - 1
    if max < min:
        max = min
    patch_centers = torch.arange(min, max + 1, step=patch_step, device=device)
    if distribute_patches is True:
        delta = max - patch_centers[-1]
        shifts = torch.linspace(0, delta, steps=len(patch_centers), device=device)
        patch_centers += torch.round(shifts).long()
    return patch_centers


def get_patch_centers_2d(
    image_shape: Sequence[int],
    patch_shape: Tuple[int, int],
    patch_step: Tuple[int, int],
    distribute_patches: bool = True,
    device: torch.device = None,
) -> torch.Tensor:
    pc_h, pc_w = [
        get_patch_centers_1d(
            dim_length=dim_length,
            patch_length=window_length,
            patch_step=step,
            distribute_patches=distribute_patches,
            device=device,
        )
        for dim_length, window_length, step
        in zip(image_shape[-2:], patch_shape, patch_step)
    ]
    n_ph, n_pw = len(pc_h), len(pc_w)
    phh = einops.repeat(pc_h, 'ph -> ph pw', pw=n_pw)
    pww = einops.repeat(pc_w, 'pw -> ph pw', ph=n_ph)
    patch_centers = einops.rearrange([phh, pww], 'hw h w -> h w hw')
    return patch_centers


def get_patch_centers_3d(
    image_shape: Sequence[int],
    patch_shape: Tuple[int, int, int],
    patch_step: Tuple[int, int, int],
    distribute_patches: bool = True,
    device: torch.device = None
) -> torch.Tensor:
    pc_d, pc_h, pc_w = [
        get_patch_centers_1d(
            dim_length=dim_length,
            patch_length=window_length,
            patch_step=step,
            distribute_patches=distribute_patches,
            device=device,
        )
        for dim_length, window_length, step
        in zip(image_shape[-3:], patch_shape, patch_step)
    ]
    n_pd, n_ph, n_pw = len(pc_d), len(pc_h), len(pc_w)
    pdd = einops.repeat(pc_d, 'pd -> pd ph pw', ph=n_ph, pw=n_pw)
    phh = einops.repeat(pc_h, 'ph -> pd ph pw', pd=n_pd, pw=n_pw)
    pww = einops.repeat(pc_w, 'pw -> pd ph pw', pd=n_pd, ph=n_ph)
    patch_centers = einops.rearrange([pdd, phh, pww], 'dhw d h w -> d h w dhw')
    return patch_centers

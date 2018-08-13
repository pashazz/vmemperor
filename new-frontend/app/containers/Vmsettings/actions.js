/*
 *
 * Vmsettings actions
 *
 */

import {
  VM_CONVERT, VM_REQUEST_DISKINFO, VM_SET_DISKINFO, VDI_DETACH, VDI_ATTACH, VM_WATCH,
} from './constants';

export function vm_convert(uuid, mode)
{
  return {
    type: VM_CONVERT,
    uuid, mode
  };
}

export function vdi_detach(vm, vdi)
{
  return {
    type: VDI_DETACH,
    vm, vdi
  }
}

export function vdi_attach(vm, vdi)
{
  return {
    type: VDI_ATTACH,
    vm, vdi
  }
}

export function requestDiskInfo(uuid)
{
  return {
    type: VM_REQUEST_DISKINFO,
    uuid,
  };
}

export function setDiskInfo(data)
{
  return {
    type: VM_SET_DISKINFO,
    data
  }
}

export function vmWatch(uuid)
{
  return {
    type: VM_WATCH,
    uuid
  }
}

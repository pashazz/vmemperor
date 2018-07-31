/*
 *
 * Vmsettings actions
 *
 */

import {
  VM_CONVERT, VM_REQUEST_DISKINFO, VM_SET_DISKINFO,
} from './constants';

export function vm_convert(uuid, mode)
{
  return {
    type: VM_CONVERT,
    uuid, mode
  };
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

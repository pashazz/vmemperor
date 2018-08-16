/*
 *
 * Vmsettings actions
 *
 */

import {
  VM_CONVERT,
  VM_REQUEST_INFO,
  VM_SET_INFO,
  VDI_DETACH,
  VDI_ATTACH,
  VM_WATCH,
  VM_REQUEST_RESOURCE,
  VM_SET_RESOURCE,
  ISO_ATTACH,
  NET_ACTION,
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

export function iso_attach(vm, iso)
{
  return {
    type: ISO_ATTACH,
    vm, iso
  }
}

export function net_action(vm, net, action)
{
  return {
    type: NET_ACTION,
    vm, net, action
  }
}



export function requestInfo(resourceType, uuid)
{
  return {
    type: VM_REQUEST_INFO,
    resourceType,
    uuid,
  };
}

export function requestResourceData(resourceType, page, pageSize)
{
  return {
    type: VM_REQUEST_RESOURCE,
    resourceType,
    page,
    pageSize
  }
}

export function setResourceData(resourceType, data)
{
  return{
    type: VM_SET_RESOURCE,
    resourceType,
    data,
  }
}



export function setInfo(resourceType, data)
{
  return {
    type: VM_SET_INFO,
    resourceType,
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

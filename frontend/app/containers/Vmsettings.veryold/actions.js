/*
 *
 * VmSettings actions
 *
 */

import {
  REQUEST_VMINFO, SET_VMINFO,
} from './constants';

export function requestVMInfo(uuid) {
  return {
    type: REQUEST_VMINFO,
    uuid
  };
}

export function setVMInfo(data){
    return {
      type: SET_VMINFO,
      data
    }
  }


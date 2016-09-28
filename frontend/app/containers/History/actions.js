/*
 *
 * History actions
 *
 */

import {
  SET_VMS,
  CLEAR_VM,
} from './constants';

export function setVMStates(vms) {
  return {
    type: SET_VMS,
    vms,
  };
}

export function stopTracking(id) {
  return {
    type: CLEAR_VM,
    id,
  };
}

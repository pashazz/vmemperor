/*
 *
 * CreateVm actions
 *
 */

import {
  SET_POOLS,
  TOGGLE_MODAL,
  CREATE_VM,
} from './constants';

export function setPools(pools) {
  return {
    type: SET_POOLS,
    pools,
  };
}

export function createVM(form) {
  return {
    type: CREATE_VM,
    form,
  };
}

export function toggleModal() {
  return {
    type: TOGGLE_MODAL,
  };
}

/*
 *
 * VMs actions
 *
 */
import {
  SET_VM_LIST,
  SET_FILTER,
  SET_SORT,
  RUN_VM_ACTION,
} from './constants';

export function setVMList(list) {
  return {
    type: SET_VM_LIST,
    list,
  };
}

export function setVMFilter(name, value) {
  return {
    type: SET_FILTER,
    name,
    value,
  };
}

export function setVMSort(column) {
  return {
    type: SET_SORT,
    column,
  };
}

export function runVMAction(name, vm) {
  return {
    type: RUN_VM_ACTION,
    name,
    vm,
  };
}

/*
 *
 * Vms actions
 * As for now, we only need 'uuid' and 'power_state' in 'row'
 * for vm_select, vm_deselect, vm_select_all, vm_deselect_all
 */

import {
  VM_DELETE, VM_DESELECT, VM_HALT, VM_RUN, VM_SELECT, VM_DESELECT_ALL, VM_SELECT_ALL,
  VM_RUN_ERROR, VM_NOTIFICATION_INCREASE, VM_NOTIFICATION_DECREASE
} from './constants';

export function run(uuid, notifyId)
{
  return {
    type: VM_RUN,
    uuid,
    notifyId,
  }
}

export function halt(uuid, notifyId) {
  return {
    type: VM_HALT,
    uuid,
    notifyId
  }

}

export function vmNotificationIncrease(notifyId) {
  return {
    type: VM_NOTIFICATION_INCREASE,
    notifyId
  }
}

export function vmNotificationDecrease (notifyId) {
  return {
    type: VM_NOTIFICATION_DECREASE,
    notifyId
  }
}


export function vm_delete(uuid) {
  return {
    type: VM_DELETE,
    uuid
  }
}

export function vm_select(uuid) {
  return {
    type: VM_SELECT,
    uuid
  }
}

export function vm_deselect(uuid)
{
  return {
    type: VM_DESELECT,
    uuid
  }
}

export function vm_select_all(uuids)
{
  return {
    type: VM_SELECT_ALL,
    uuids
  }
}

export function vm_deselect_all()
{
  return {
    type: VM_DESELECT_ALL,
  }
}

//TODO May we use it for another types of errors in the future?
export function vm_run_error(payload, date)
{
  const {message, details} = JSON.parse(payload);
  return {
    type: VM_RUN_ERROR,
    errorText: message,
    errorType: details[0],
    ref: details[1],
    errorDetailedText: details[2].trim(),
    date: date,
  }
}

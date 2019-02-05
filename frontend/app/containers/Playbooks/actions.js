/*
 *
 * Playbooks actions
 *
 */

import {
  SET_PLAYBOOKS,
  EXECUTE_PLAYBOOK
} from './constants';

export function setPlaybooks(data) {
  return {
    type: SET_PLAYBOOKS,
    data: data
  };
}

export function executePlaybook(playbook, uuids, form){
  return {
    type: EXECUTE_PLAYBOOK,
    playbook,
    uuids,
    form,
  }
}

/*
 *
 * Playbooks actions
 *
 */

import {
  SET_PLAYBOOKS,
} from './constants';

export function setPlaybooks(data) {
  return {
    type: SET_PLAYBOOKS,
    data: data
  };
}

/*
 *
 * Vncview actions
 *
 */

import {
  VNC_REQUESTED,
  VNC_URL_ACQUIRED,
} from './constants';

export function vncRequest(uuid) {
  return {
    type: VNC_REQUESTED,
    uuid
  };
}

export function vncAcquire(url) {
  return {
    type: VNC_URL_ACQUIRED,
    url
  }
}

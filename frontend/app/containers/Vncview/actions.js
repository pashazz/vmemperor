/*
 *
 * Vncview actions
 *
 */

import {
  VNC_ERROR,
  VNC_REQUESTED,
  VNC_URL_ACQUIRED,
} from './constants';

export function vncRequest(uuid) {
  return {
    type: VNC_REQUESTED,
    uuid
  };
}

export function vncAcquire(url, uuid) {
  return {
    type: VNC_URL_ACQUIRED,
    url,
    uuid
  }
}

export function vncError(error)
{
  return {
    type: VNC_ERROR,
    error
  }
}

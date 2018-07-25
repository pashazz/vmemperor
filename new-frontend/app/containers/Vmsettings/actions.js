/*
 *
 * Vmsettings actions
 *
 */

import {
  VM_CONVERT,
} from './constants';

export function vm_convert(uuid, mode)
{
  return {
    type: VM_CONVERT,
    uuid, mode
  }
}

/*
 *
 * LoginPage actions
 *
 */

import {
  SET_POOLS,
} from './constants';

export function setPools(pools) {
  return {
    type: SET_POOLS,
    pools,
  };
}

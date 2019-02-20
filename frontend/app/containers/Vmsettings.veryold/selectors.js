import { createSelector } from 'reselect';
import {Map} from 'immutable';
import VM from 'models/VM';
/**
 * Direct selector to the vmsettings state domain
 */
const makeSelectVmsettingsDomain = () => (state) => state.get('vmsettings', new Map());

/**
 * Other specific selectors
 */

const makeSelectVminfo = () => createSelector(
  makeSelectVmsettingsDomain(),
  state => state.get('vminfo', new VM())
);

/**
 * Default selector used by VMSettings
 */


export {
  makeSelectVminfo,
}

import { createSelector } from 'reselect';

/**
 * Direct selector to the vmsettings state domain
 */
const makeSelectAppDomain = () => (state) => state.get('app');
const selectVmData = (state) => selectAppData(state).get('vm_data');
/**
 * Other specific selectors
 */

const makeSelectVmData = () => createSelector(
  makeSelectAppDomain(),
  state =>{ console.log(state); return state.get('vm_data') }
);
/**
 * Default selector used by VMSettings
 */

export {
  makeSelectVmData
};

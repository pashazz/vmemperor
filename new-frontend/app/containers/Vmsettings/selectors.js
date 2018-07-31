import { createSelector } from 'reselect';

/**
 * Direct selector to the vmsettings state domain
 */
const makeSelectVmSettingsDomain = () => (state) => state.get('vmsettings');
const makeSelectAppDomain = () => (state) => state.get('app');
const selectVmData = (state) => selectAppData(state).get('vm_data');
/**
 * Other specific selectors
 */

const makeSelectVmData = () => createSelector(
  makeSelectAppDomain(),
  state =>{ return state.get('vm_data'); }
);

const makeSelectDiskInfo = () => createSelector(
  makeSelectVmSettingsDomain(),
  state => { return state.get('vm_disk_info').entrySeq().map(value => {
    return {
      key: value[0],
      ...value[1].toJS(),
    };
  }).toArray()}
);
/**
 * Default selector used by VMSettings
 */

export {
  makeSelectVmData,
  makeSelectDiskInfo
};

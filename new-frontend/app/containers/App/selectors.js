import { createSelector } from 'reselect';

const selectRouter = (state) => state.get('route');

const makeSelectLocation = () => createSelector(
  selectRouter,
  (routerState) => routerState.location
);


const selectAppData = (state) => state.get('app');
const selectVmData = (state) => selectAppData(state).get('vm_data');
const makeSelectVmDataForTable = () => createSelector( //Only choose what is needed for table
  selectVmData,
  (substate) => {
    return  substate.map(item => {
      const {power_state, name_label, uuid} = item;
      return {power_state, name_label, uuid};
    });
  }
);
export {
  makeSelectLocation,
  makeSelectVmDataForTable,
};

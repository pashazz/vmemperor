import { createSelector } from 'reselect';

const selectRouter = (state) => state.get('route');

const makeSelectLocation = () => createSelector(
  selectRouter,
  (routerState) => routerState.location
);


const selectAppData = (state) => state.get('app');
const selectVmData = (state) => selectAppData(state).get('vm_data');

const makeSelectVmData = () => createSelector(
  selectVmData,
  (substate) => {console.log("VM_DATA: ", substate); return substate}
);

export {
  makeSelectLocation,
  makeSelectVmData,
};

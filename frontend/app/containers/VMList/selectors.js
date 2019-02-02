import { createSelector } from 'reselect';

/**
 * Direct selector to the vms state domain
 */

const selectAppData = (state) => state.get('app');
const selectVmData = (state) => selectAppData(state).get('vm_data');


const selectVmsData = (state) => state.get('vms');
const selectSelectionData =  (state) => selectVmsData(state).get('selected');
const makeSelectVmDataForTable = () => createSelector( //Only choose what is needed for table
  selectVmData,
  (substate) => { //Immutable map
    return  substate.map(item => {
      const {power_state, name_label, start_time, uuid,  ref} = item;
      return {power_state, name_label, start_time,uuid};
    }).toIndexedSeq().toArray();
  }
);

/**
 *
 * @returns a map with uuid as key and name_label as value
 */
const makeSelectVmDataNames = () => createSelector(
  selectVmData,
  (substate) => {
    return substate.map(item => {
      return item.name_label;
    });
  }
);


const makeSelectSelection = () => createSelector( //Table selection
  selectSelectionData,
  (substate)  => {//Immutable set
    return substate.toSeq().toArray();
  }
);


const makeSelectSelectionPowerState = (power) => createSelector(
  selectVmData, //Map of uuids
  selectSelectionData, //Set of uuids
  (vmSubstate, selectionSubstate) => {
    return selectionSubstate.filter(
      id => vmSubstate.has(id) &&
        vmSubstate.get(id).power_state === power).toSeq().toArray();
  });

const makeSelectSelectionRunning = () =>
  makeSelectSelectionPowerState('Running');

const makeSelectSelectionHalted = () =>
  makeSelectSelectionPowerState('Halted');

const makeStartButtonDisabled = () => createSelector(
  makeSelectSelectionHalted(),
  (halted) => halted.length === 0);


const makeStopButtonDisabled = () => createSelector(
  makeSelectSelectionRunning(),
  (running) => running.length === 0);


const makeTrashButtonDisabled = () => createSelector(
  makeSelectSelection(),
  (selection) => selection.length === 0);

export {
  makeSelectVmDataForTable,
  makeSelectVmDataNames,
  makeSelectSelection,
  makeSelectSelectionRunning,
  makeSelectSelectionHalted,
  makeStartButtonDisabled,
  makeStopButtonDisabled,
  makeTrashButtonDisabled
}

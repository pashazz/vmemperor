/*
 *
 * VMList reducer
 *
 */

import { combineReducers } from 'redux-immutable';
import { fromJS, Set, Map} from 'immutable';
import {
  VM_SELECT, VM_DESELECT, VM_SELECT_ALL, VM_DESELECT_ALL, VM_NOTIFICATION_INCREASE, VM_NOTIFICATION_DECREASE
} from './constants';


const selected = (state = Set(), action) =>
{
  switch (action.type)
  {

    case VM_SELECT:
      return state.add(action.uuid);
    case VM_DESELECT:
      return state.delete(action.uuid);
    case VM_SELECT_ALL:
      return Set(action.uuids);
    case VM_DESELECT_ALL:
      return Set();
    default:
      return state;
  }

};

export default combineReducers(
  {
    selected,
  }
);

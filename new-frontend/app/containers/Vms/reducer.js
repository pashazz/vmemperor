/*
 *
 * Vms reducer
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

const notifications = (state = Map(), action) =>
{
  switch (action.type)
  {
    case VM_NOTIFICATION_INCREASE:
      return state.update(action.notifyId, 0, val => val + 1);
    case VM_NOTIFICATION_DECREASE:
      if (state.get(action.notifyId) === 1)
        return state.delete(action.notifyId);
      else
        return state.update(action.notifyId, val => val - 1);
    default:
      return state;



  }
};

export default combineReducers(
  {selected,
  notifications}
);

/*
 *
 * History reducer
 *
 */

import { combineReducers } from 'redux-immutable';
import { fromJS } from 'immutable';
import {
  SET_VMS,
  CLEAR_VM,
} from './constants';

const vmsInitial = fromJS({});

function vms(state = vmsInitial, action) {
  switch (action.type) {
    case SET_VMS:
      return fromJS(action.vms);
    case CLEAR_VM:
      return state.delete(action.id);
    default:
      return state;
  }
}

const historyReducer = combineReducers({
  vms,
});

export default historyReducer;

/*
 *
 * Vmsettings reducer
 *
 */

import { fromJS } from 'immutable';
import {combineReducers} from 'redux-immutable';
import {VM_SET_DISKINFO} from "./constants";

const initialState = fromJS({});

const vm_disk_info = (state = initialState, action) =>
{
  switch (action.type) {
    case VM_SET_DISKINFO:
      return fromJS(action.data);
    default:
      return state;
  }
};


export default combineReducers(
  {
    vm_disk_info,
  }
);

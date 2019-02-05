/*
 *
 * VmSettings reducer
 *
 */

import { fromJS } from 'immutable';
import { combineReducers } from 'redux-immutable';
import {
  SET_VMINFO,
  REQUEST_VMINFO
} from "./constants";
import VM from 'models/VM';


const vminfo = (state = fromJS({}), action) =>
{
  switch (action.type)
  {
    case SET_VMINFO:
      return new VM(action.data);
    default:
      return state;
  }
};

export default combineReducers ({
  vminfo,
});

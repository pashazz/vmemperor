/*
 *
 * Vmsettings reducer
 *
 */

import { fromJS } from 'immutable';
import {combineReducers} from 'redux-immutable';
import {VM_SET_DISKINFO, VM_SET_RESOURCE, VM_WATCH} from "./constants";

const initialState = fromJS({});

const vm_disk_info = (state = initialState, action) =>
{
  switch (action.type) {
    case VM_SET_DISKINFO:
      if (action.data)
        return fromJS(action.data);
      else
        return fromJS({});
    default:
      return state;
  }
};

const isoList = (state = fromJS([]), action) =>
{
  switch (action.type) {
    case VM_SET_RESOURCE:
      switch (action.resourceType) {
        case 'iso':
              if (action.data) {
                return fromJS(action.data);
              }
              else {
                return fromJS([]);
              }
        default:
          return state;
      }
    default:
      return state;
  }
  
};

const vdiList = (state = fromJS([]), action) =>
{
  switch (action.type) {
    case VM_SET_RESOURCE:
      switch (action.resourceType) {
        case 'vdi':
          if (action.data) {
            return fromJS(action.data);
          }
          else {
            return fromJS([]);
          }
        default:
          return state;
      }
    default:
      return state;
  }

};

const uuid = (state = "", action) =>
{
  switch (action.type) {
    case VM_WATCH:
      return action.uuid;
    default:
      return state;
  }
};


export default combineReducers(
  {
    vm_disk_info,
    isoList,
    vdiList,
    uuid,
  }
);

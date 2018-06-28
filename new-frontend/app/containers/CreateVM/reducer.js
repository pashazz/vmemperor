/*
 *
 * CreateVm reducer
 *
 */

import { combineReducers } from 'redux-immutable';
import { List, fromJS } from 'immutable';
import {
  SET_POOLS,
  TOGGLE_MODAL,
} from './constants';
import Pool from 'models/Pool';

const poolsInitial = fromJS([]);

function pools(state = poolsInitial, action) {
  switch (action.type) {
    case SET_POOLS:
      return List.of(...action.pools.map(p => new Pool(p)));
    default:
      return state;
  }
}

const modalInitial = false;

function modal(state = modalInitial, action) {
  switch (action.type) {
    case TOGGLE_MODAL:
      return !state;
    default:
      return state;
  }
}

const createVMReducer = combineReducers({
  pools,
  modal,
});

export default createVMReducer;

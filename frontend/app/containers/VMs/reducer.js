/*
 *
 * VMs reducer
 *
 */
import { combineReducers } from 'redux-immutable';
import { fromJS, List } from 'immutable';
import {
  SET_VM_LIST,
  SET_FILTER,
  SET_SORT,
  RUN_VM_ACTION,
} from './constants';
import VM from 'models/VM';

const listInitial = fromJS([]);

function vmSetChanging(vm, changing) {
  return changing.uuid === vm.uuid ? vm.set('changing', true) : vm;
}

function list(state = listInitial, action) {
  switch (action.type) {
    case SET_VM_LIST:
      return List.of(...action.list.map(info => new VM(info)));
    case RUN_VM_ACTION:
      return state.map(vm => vmSetChanging(vm, action.vm));
    default:
      return state;
  }
}

const filtersInitial = fromJS({
  name: '',
  pool: '',
  ip: '',
  state: '',
});

function filters(state = filtersInitial, action) {
  switch (action.type) {
    case SET_FILTER:
      return state.set(action.name, action.value);
    default:
      return state;
  }
}

const sortInitial = fromJS({
  order: 'asc',
  column: 'name',
});

function updateWith(state, column) {
  if (state.get('column') === column) {
    return state.update('order', v => v === 'asc' ? 'desc' : 'asc'); // eslint-disable-line no-confusing-arrow
  }
  return sortInitial.set('column', column);
}

function sort(state = sortInitial, action) {
  switch (action.type) {
    case SET_SORT:
      return updateWith(state, action.column);
    default:
      return state;
  }
}

const VMsReducer = combineReducers({
  list,
  filters,
  sort,
});

export default VMsReducer;

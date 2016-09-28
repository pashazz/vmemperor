/*
 *
 * Templates reducer
 *
 */
import { combineReducers } from 'redux-immutable';
import { fromJS, List } from 'immutable';
import {
  SET_TEMPLATE_LIST,
  SET_FILTER,
  SET_SORT,
  RUN_TEMPLATE_ACTION,
} from './constants';
import Template from 'models/Template';

const listInitial = fromJS([]);

function updateChanging(template, changing) {
  return template.uuid === changing.uuid ? template.set('changing', true) : template;
}

function list(state = listInitial, action) {
  switch (action.type) {
    case SET_TEMPLATE_LIST:
      return List.of(...action.list.map(template => new Template(template)));
    case RUN_TEMPLATE_ACTION:
      return state.map(template => updateChanging(template, action.template));
    default:
      return state;
  }
}

const filtersInitial = fromJS({
  name: '',
  pool: '',
  mirror: '',
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

const templatesReducer = combineReducers({
  list,
  filters,
  sort,
});

export default templatesReducer;

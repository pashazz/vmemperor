/*
 *
 * Templates actions
 *
 */

import {
  SET_TEMPLATE_LIST,
  SET_FILTER,
  SET_SORT,
  RUN_TEMPLATE_ACTION,
} from './constants';

export function setTemplateList(list) {
  return {
    type: SET_TEMPLATE_LIST,
    list,
  };
}

export function setTemplateFilter(name, value) {
  return {
    type: SET_FILTER,
    name,
    value,
  };
}

export function setTemplateSort(column) {
  return {
    type: SET_SORT,
    column,
  };
}

export function runTemplateAction(name, template) {
  return {
    type: RUN_TEMPLATE_ACTION,
    name,
    template,
  };
}

/*
 *
 * CreateVm reducer
 *
 */

import { combineReducers } from 'redux-immutable';
import { List, fromJS } from 'immutable';
import {
  SET_ISOS,
  SET_NETWORK,
  SET_NETWORKS,
  SET_POOLS, SET_TEMPLATES,
  TOGGLE_MODAL,
} from './constants';
import Pool from 'models/Pool';
import ISO from 'models/ISO';
import Network from 'models/Network';
import Template from 'models/Template';

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

const isos = (state = fromJS([]), action) =>
{
  switch (action.type)
  {
    case SET_ISOS:
      return List.of(...action.isos.map(iso => new ISO(iso)));
    default:
      return state;
  }
};

const networks = (state = fromJS([]), action) =>
{
  switch (action.type)
  {
    case SET_NETWORKS:
      return List.of(...action.networks.map(net => new Network(net)));
    default:
      return state;
  }
};


const tmpls = (state = fromJS([]), action) =>
{
  switch(action.type)
  {
    case SET_TEMPLATES:
      return List.of(...action.templates.map(tmpl => new Template(tmpl)));
    default:
      return state;
  }

};

const createVMReducer = combineReducers({
  pools,
  modal,
  isos,
  networks,
  tmpls
});

export default createVMReducer;

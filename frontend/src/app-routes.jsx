import React from 'react';
import { Route, Redirect } from 'react-router';

import Master    from './components/master.jsx';
import VMs       from './components/vms.jsx';
import Templates from './components/templates.jsx';
import CreateVM  from './components/create-vm.jsx';

const AppRoutes = (
  <Route name="root" path="/" handler={Master}>
    <Route name="vms" handler={VMs} />
    <Route name="templates" handler={Templates} />
    <Route name="create-vm" handler={CreateVM} />

    <Redirect from="/" to="vms" />
  </Route>
);

export default AppRoutes;

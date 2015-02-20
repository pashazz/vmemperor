var React = require('react'),
    Router = require('react-router'),
    Route = Router.Route,
    Redirect = Router.Redirect,
    DefaultRoute = Router.DefaultRoute;

var Master = require('./components/master.jsx'),
    VMs = require('./components/vms.jsx'),
    Templates = require('./components/templates.jsx'),
    CreateVM = require('./components/create-vm.jsx');

var AppRoutes = (
  <Route name="root" path="/" handler={Master}>
    <Route name="vms" handler={VMs} />
    <Route name="templates" handler={Templates} />
    <Route name="create-vm" handler={CreateVM} />

    <Redirect from="/" to="vms" />
  </Route>
);

module.exports = AppRoutes;
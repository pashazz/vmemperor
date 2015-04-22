(function () {

  var React = require('react'),
    Router = require('react-router'),
    Login = require('./login.jsx'),
    AppRoutes = require('./app-routes.jsx'),
    SessionStore = require('./flux/session-store');

  window.React = React;

  var init = function(session) {
    if(session !== null) {
      Router
        .create({
          routes: AppRoutes,
          scrollBehavior: Router.ScrollToTopBehavior
        })
        .run(function (Handler) {
          React.render(<Handler/>, document.body);
        });
    } else {
      React.render(<Login />, document.body);
    }
  };

  init(SessionStore.getData());

  SessionStore.listen(init);

})();

import React from 'react';
import Router from 'react-router';
import Login from './login.jsx';
import AppRoutes from './app-routes.jsx';
import SessionStore from './flux/session-store';

(function () {
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

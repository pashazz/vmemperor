//import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles'
import * as React from 'react'
import { Suspense } from 'react'
import { ApolloProvider } from 'react-apollo-hooks'
import * as ReactDOM from 'react-dom'
import apolloClient from './apollo-client'
import App from './components/App'
import registerServiceWorker from './registerServiceWorker'
//import './index.css'
import 'bootstrap/dist/bootstrap.min.css';

ReactDOM.render(
      <ApolloProvider client={apolloClient}>
      <Suspense fallback={null}>
        <App />
      </Suspense>
    </ApolloProvider>,
  document.getElementById('root') as HTMLElement,
);

registerServiceWorker();

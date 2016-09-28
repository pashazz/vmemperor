/**
*
* SinglePoolLogin
*
*/

import React, { PropTypes as T } from 'react';

import { injectIntl, intlShape } from 'react-intl';
import messages from './messages';
import styles from './styles.css';

class SinglePoolLogin extends React.Component { // eslint-disable-line react/prefer-stateless-function
  static propTypes = {
    description: T.string.isRequired,
    index: T.number.isRequired,
    intl: intlShape.isRequired,
  };

  render() {
    const { description, index, intl } = this.props;
    const loginPlaceholder = intl.formatMessage(messages.loginPlaceholder);
    const passwordPlaceholder = intl.formatMessage(messages.passwordPlaceholder);
    return (
      <div className="form-inline" >
        <div className={['input-group', styles.poolForm].join(' ')}>
          <div className="input-group-addon">{description}</div>
          <input type="text" className="form-control" placeholder={loginPlaceholder} name={`login${index}`} />
          <input type="password" className="form-control" placeholder={passwordPlaceholder} name={`password${index}`} />
        </div>
      </div>
    );
  }
}

export default injectIntl(SinglePoolLogin);

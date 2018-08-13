/**
*
* VmsettingsForm
*
*/

import React from 'react';
import Power from './subforms/power';
import Storage from './subforms/storage';
// import styled from 'styled-components';

import { FormattedMessage } from 'react-intl';
import messages from './messages';
import { Nav, NavItem, Badge, NavLink, TabContent, TabPane, Row, Col, Card, CardTitle, CardText, Button} from 'reactstrap';
import classnames from 'classnames';

import T from 'prop-types';

//import Vncview from 'containers/Vncview/Loadable';


class VmsettingsForm extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  constructor(props) {
  super(props);
  this.toggle = this.toggle.bind(this);
  this.state = {
    activeTab: 'power',
  }
  }


   toggle(tab) {
   if (this.state.activeTab !== tab) {
      this.setState({
        activeTab: tab
      });
    }


  }

  render() {
    const data = this.props.data;
    return (
      <div>
        <h3 className="text-center">{data.name_label} <Badge color="primary">{data.power_state}</Badge>
          {data.hasIn(['os_version', 'name']) &&
          (<Badge color="success">{data.getIn(['os_version', 'name'])}</Badge>)}
        </h3>

        <Nav tabs>
          <NavItem>
            <NavLink
              className={classnames({ active: this.state.activeTab === 'power' })}
              onClick={() => { this.toggle('power'); }}
            >
             Power
            </NavLink>
          </NavItem>

          <NavItem>
            <NavLink
              className={classnames({ active: this.state.activeTab === 'vnc' })}
              onClick={() => { this.toggle('vnc'); }}
            >
              VNC
            </NavLink>
          </NavItem>


          <NavItem>
            <NavLink
                 className={classnames({ active: this.state.activeTab === 'storage' })}
              onClick={() => { this.toggle('storage'); }}
            >
             Storage
            </NavLink>
          </NavItem>
          <NavItem>
            <NavLink
              className={classnames({ active: this.state.activeTab === 'network' })}
              onClick={() => { this.toggle('storage'); }}
            >
              Network
            </NavLink>
          </NavItem>
          <NavItem>
            <NavLink
              className={classnames({ active: this.state.activeTab === '2' })}
              onClick={() => { this.toggle('2'); }}
            >
              Moar Tabs
            </NavLink>
          </NavItem>
        </Nav>
        <TabContent activeTab={this.state.activeTab}>
          <TabPane tabId="power">
            <Row>
              <Col sm="12">
              <Power data={data}
                     onHalt={this.props.onHalt}
                     onReboot={this.props.onReboot}
                     onConvertVm={this.props.onConvertVm}
              />
              </Col>
            </Row>
          </TabPane>
          <TabPane tabId="storage">
            <Row>
              <Col sm="12">
                <Storage
                data={data}
                diskInfo={this.props.diskInfo}
                onDetachVdi={this.props.onDetachVdi}
                onAttachVdi={this.props.onAttachVdi}
                />
              </Col>
            </Row>
          </TabPane>
          <TabPane tabId="vnc">
            <h1>Use power tab for now</h1>
          </TabPane>
          <TabPane tabId="network">
          </TabPane>
          <TabPane tabId="2">
            <Row>
              <Col sm="6">
                <Card body>
                  <CardTitle>Special Title Treatment</CardTitle>
                  <CardText>With supporting text below as a natural lead-in to additional content.</CardText>
                  <Button>Go somewhere</Button>
                </Card>
              </Col>
              <Col sm="6">
                <Card body>
                  <CardTitle>Special Title Treatment</CardTitle>
                  <CardText>With supporting text below as a natural lead-in to additional content.</CardText>
                  <Button>Go somewhere</Button>
                </Card>
              </Col>
            </Row>
          </TabPane>
        </TabContent>
      </div>
    );
    }
    static propTypes = {
      data: T.any.isRequired,
      diskInfo: T.any.isRequired,
      onHalt: T.func.isRequired,
      onReboot: T.func.isRequired,
      onConvertVm: T.func.isRequired,
      onDetachVdi: T.func.isRequired,
      onAttachVdi: T.func.isRequired,
    }


}


export default VmsettingsForm;

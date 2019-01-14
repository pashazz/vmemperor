/**
*
* VmsettingsForm
*
*/

import React from 'react';
import Power from './subforms/power';
import Storage from './subforms/storage';
import Network from './subforms/network';
// import styled from 'styled-components';

import { FormattedMessage } from 'react-intl';
import messages from './messages';
import { Nav, NavItem, Badge, NavLink, TabContent, TabPane, Row, Col, Card, CardTitle, CardText, Button} from 'reactstrap';
import classnames from 'classnames';

import T from 'prop-types';
import Vncview from 'containers/Vncview/Loadable';
import VM from 'models/VM';


class VmsettingsForm extends React.PureComponent { // eslint-disable-line react/prefer-stateless-function
  constructor(props) {
  super(props);
  this.toggle = this.toggle.bind(this);
  this.state = {
    activeTab: 'power',
    vncActivated: false,
  }
  }


   toggle(tab) {
     console.log("Toggled tab", tab);
   if (this.state.activeTab !== tab) {
      this.setState({
        activeTab: tab
      });
      if (tab === 'vnc' && !this.state.vncActivated)
      {
        this.setState({
          vncActivated: true,
        });
      }
    }

  }

  render() {
    const data = this.props.data;
    console.log("Current tab:", this.state.activeTab);
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
              onClick={() => {console.log("CLOCK"); this.toggle('vnc'); }}
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
              onClick={() => { this.toggle('network'); }}
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
                onAttachIso={this.props.onAttachIso}
                onAttachVdi={this.props.onAttachVdi}
                requestIso={this.props.requestIso}
                requestVdi={this.props.requestVdi}
                isoList={this.props.isoList}
                vdiList={this.props.vdiList}
                />
              </Col>
            </Row>
          </TabPane>
          <TabPane tabId="vnc">
            {
              this.state.vncActivated && (
                <Vncview uuid={this.props.data.uuid}/>
              ) || (<h1>NO VNC HERE</h1>)
            }
          </TabPane>
          <TabPane tabId="network">
            <Row>
              <Col sm="12">
                <Network
                  data={data}
                  networks={this.props.netInfo}
                  onAttach={this.props.onAttachNet}
                  onDetach={this.props.onDetachNet}
                  requestNet={this.props.requestNet}
                  netList={this.props.netList}
                  />
              </Col>
            </Row>
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
      data: T.instanceOf(VM).isRequired,
      diskInfo: T.any.isRequired,
      netInfo: T.array.isRequired,
      onHalt: T.func.isRequired,
      onReboot: T.func.isRequired,
      onConvertVm: T.func.isRequired,
      onDetachVdi: T.func.isRequired,
      onAttachVdi: T.func.isRequired,
      onAttachIso: T.func.isRequired,
      onAttachNet: T.func.isRequired,
      onDetachNet: T.func.isRequired,
      requestNet: T.func.isRequired,
      requestIso: T.func.isRequired,
      requestVdi: T.func.isRequired,
      isoList: T.array.isRequired,
      vdiList: T.array.isRequired,
      netList: T.array.isRequired,


    }


}


export default VmsettingsForm;

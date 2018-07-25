import React, {PureComponent} from 'react';
import T from 'prop-types';
import {Button, Card, CardTitle, CardText, Col, Row, CardFooter,CardBody, CardSubtitle, ButtonGroup} from 'reactstrap';
import FullHeightCard from 'components/FullHeightCard';
import {VM_STATE_RUNNING} from "../../../containers/App/constants";

//import DateDiff from 'utils/datediff';
import  VM from 'models/VM';

import { FormattedMessage } from 'react-intl';
import messages from  '../messages';

class Power extends PureComponent {
  static propTypes = {
    onReboot: T.func.isRequired,
    onHalt: T.func.isRequired,
    onConvertVm: T.func.isRequired,
    data: T.instanceOf(VM),
  };
  render()
  {
    const { data } = this.props;

    const current_date = new Date();
    const start_date = new Date(data.start_time);

    let uptime_text = null;

    switch (data.power_state)
    {
      case VM_STATE_RUNNING:
        uptime_text = "I'm up since " +  start_date.toLocaleString() + ".";
        break;
      default:
        uptime_text = "I'm " + data.power_state.toLowerCase() + ".";
    }

    const nets = data['networks'];
    const addresses = data.networks.map((value, key) => {
      let text= "";
      if (value.get('ip'))
      {
        text = "IPv4: " +  value.get('ip') + " (Network " + key + ")\n"
      }
      if (value.get('ipv6'))  {

        text += "IPv6:" + value.get('ipv6') + " (Network " + key + ")";
      }
      if (!text)
      {
        text = "Not available";
      }

      return text;
    }).valueSeq().toArray();
    return(
      <React.Fragment>
      <Row>
        <Col sm={6}>
      <FullHeightCard>
        <CardBody>
          <CardTitle>Power status</CardTitle>
        <CardText>{ uptime_text} (X days Y hours Z minutes W seconds)
        <br/>
        </CardText>
        </CardBody>
        <CardFooter>
        <div>
          { data.power_state === 'Running' && (
        <Button size="lg" color="danger" onClick={this.props.onReboot}>Reboot  </Button>)}
          {' '}
        <Button size="lg" color="primary" onClick={this.props.onHalt}>{ (data.power_state === 'Halted') ?
          <FormattedMessage {...messages.turnon}/> :
          <FormattedMessage {...messages.halt}/>
        } </Button>
        </div>
        </CardFooter>
      </FullHeightCard>
        </Col>
        <Col sm={6}>
          <FullHeightCard>

            <CardBody>
              <CardTitle>Access</CardTitle>

              {addresses && (
                <React.Fragment>
                  <CardSubtitle>IP addresses</CardSubtitle>
                  <CardText>
                    {addresses.map(address => <div>{address}</div>)}
                  </CardText>
                </React.Fragment>
              ) || (
                <CardSubtitle>Connect your VM to a network to access it </CardSubtitle>)
              }
            </CardBody>
            <CardFooter>
              <div>
                <Button disabled={data.power_state !== 'Running'} size="lg" color="success"
                onClick={() => {
                  const win = window.open('/desktop/' + data.uuid, '_blank');
                  win.focus();
                }}>Go to Desktop</Button>
              </div>
            </CardFooter>
          </FullHeightCard>

        </Col>
      </Row>
        <Row>
          <Col sm={6}>
            <FullHeightCard>
              <CardBody>
                <CardTitle>Virtualization mode</CardTitle>
                {data.power_state !== 'Halted' && (
                <CardSubtitle>Halt to switch mode</CardSubtitle>)}

                <CardText><h4>{data.domain_type.toUpperCase()}</h4></CardText>
              </CardBody>
              <CardFooter>
                <Button
                  disabled={data.power_state !== 'Halted'}
                  size="lg"
                  color="info"
                  onClick={this.props.onConvertVm}
                >Switch to
                  {data.domain_type === 'pv' ? ' HVM' : ' PV'}
                </Button>
              </CardFooter>
            </FullHeightCard>
          </Col>
        </Row>
        <Row>
          <Col>
            <Card>
             <CardBody>
               <CardTitle>
                 Boot parameters
               </CardTitle>
               <CardText>

               </CardText>
             </CardBody>
            </Card>
          </Col>
        </Row>
      </React.Fragment>

    );
  }
}

export default Power;

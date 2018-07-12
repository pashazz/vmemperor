import React, {PureComponent} from 'react';
import T from 'prop-types';
import {Button, Card, CardTitle, CardText, Col, Row, CardFooter,CardBody, CardSubtitle, ButtonGroup} from 'reactstrap';
import FullHeightCard from 'components/FullHeightCard';

class Power extends PureComponent {
  static propTypes = {

  };
  render()
  {
    return(
      <Row>
        <Col sm={6}>
      <FullHeightCard>
        <CardBody>
          <CardTitle>Power status</CardTitle>
        <CardText>I'm up since Jun 1, 2010 (X days Y hours Z minutes W seconds)</CardText>
        </CardBody>
        <CardFooter>
        <div>
        <Button size="lg" color="danger">Reboot</Button>{' '}
        <Button size="lg" color="primary">Halt</Button>
        </div>
        </CardFooter>
      </FullHeightCard>
        </Col>
        <Col sm={6}>
          <FullHeightCard>

            <CardBody>
              <CardTitle>Access</CardTitle>
              <CardSubtitle>IP addresses</CardSubtitle>
            <CardText>

             XXX.XXX.XXX.XXX (Network 1)<br/>

             XXX.XXX.XXX.YYY (Network 2)<br/>

            </CardText>
            </CardBody>
            <CardFooter>
              <div>
                <Button size="lg" color="success">Go to Desktop</Button>
              </div>
            </CardFooter>
          </FullHeightCard>

        </Col>
      </Row>


    );
  }
}

export default Power;

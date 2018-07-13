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
      <React.Fragment>
      <Row>
        <Col sm={6}>
      <FullHeightCard>
        <CardBody>
          <CardTitle>Power status</CardTitle>
        <CardText>I'm up since Jun 1, 2010 (X days Y hours Z minutes W seconds)
        <br/>
        </CardText>
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
        <Row>
          <Col sm={6}>
            <FullHeightCard>
              <CardBody>
                <CardTitle>Virtualization mode</CardTitle>
                <CardSubtitle>Halt to switch mode</CardSubtitle>

                <CardText><h4>PV</h4></CardText>
              </CardBody>
              <CardFooter>
                <Button size="lg" color="info">Switch to HVM</Button>
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

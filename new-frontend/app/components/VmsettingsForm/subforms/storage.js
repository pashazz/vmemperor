import React, {PureComponent} from 'react';
import T from 'prop-types';
import {Button, Card, CardTitle, CardText, Table, Col, Row, CardFooter,CardBody, CardSubtitle, ButtonGroup} from 'reactstrap';
import FullHeightCard from 'components/FullHeightCard';

class Storage extends PureComponent {

  render()
  {
    return (
      <React.Fragment>
      <Row>
        <Col sm={12}>
          <Card>
            <CardBody>
              <CardTitle>Virtual hard disks</CardTitle>
              <CardText>
                <Table>
                  <thead>
                  <tr>
                  <th>#</th>
                  <th>Name</th>
                  <th>Size</th>
                  </tr>
                  </thead>
                  <tbody>
                  <th scope="row">1</th>
                  <td>0</td>
                  <td>2 GB</td>
                  </tbody>
                </Table>
              </CardText>
            </CardBody>
            <CardFooter>
              <Button size="lg" color="success"> Attach </Button>
              <Button size="lg" color="danger"> Detach </Button>
            </CardFooter>
          </Card>

        </Col>
      </Row>
      <Row>
        <Col>
      <Card>
        <CardBody>
          <CardTitle>CDROM drives</CardTitle>
          <Table>
            <thead>
            <tr>
              <th>#</th>
              <th>Name</th>
              <th>Size</th>
            </tr>
            </thead>
            <tbody>
            <th scope="row">1</th>
            <td>0</td>
            <td>2 GB</td>
            </tbody>
          </Table>
        </CardBody>
      </Card>
        </Col>
      </Row>
      </React.Fragment>
    );
  }
}
export default Storage;

import React, {PureComponent} from 'react';
import T from 'prop-types';
import {Button, Card, CardTitle, CardText, Table, Col, Row, CardFooter,CardBody, CardSubtitle, ButtonGroup} from 'reactstrap';
import FullHeightCard from 'components/FullHeightCard';
import NextTable from 'react-bootstrap-table-next';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
import faCheck from '@fortawesome/fontawesome-free-solid/faCheck';

const checkBoxFormatter = (cell, row) =>
{
  if (cell)
  {
    return (
      <span>
        { cell && (<FontAwesomeIcon icon={faCheck}/>)}
      </span>
    )
  }
};

const sizeFormatter = (cell, row) =>
{
  const suffixes = ['b', 'Kb', 'Mb', 'Gb', 'Tb', 'Pb'];
  let number = Number(cell);
  let i = 0;
  if (number < 1)
  {
    number = 0;
  }
  else {
    i = Math.trunc(Math.log(number) / Math.log(1024))  + 1;
    number = number / Math.pow(1024, i);

    if (number <= 0.5)
    {
      number *= 1024;
      i -= 1;
    }
  }
  const newNumber = +number.toFixed(2);
  if (newNumber !== number) {
    number = "~" + newNumber;
  }
  return (
    <span>
      {number + " " + suffixes[i]}
    </span>
  );

};

const columns = [
  {
    dataField: 'device',
    text: 'Name'

  },
  {
    dataField: 'type',
    text: 'Type',

  },
  {
    dataField: 'name_label',
    text: 'Disk name',

  },

  {
    dataField: 'virtual_size',
    text: 'Size',
    formatter: sizeFormatter,
  },
  {
    dataField: 'attached',
    text: 'Attached',
    formatter: checkBoxFormatter,
  },

  {
    dataField: 'bootable',
    text: 'Bootable',
    formatter: checkBoxFormatter,
  },


];


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
                <NextTable
                  columns={columns}
                  data={this.props.diskInfo}
                  keyField="key"

                  />
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
